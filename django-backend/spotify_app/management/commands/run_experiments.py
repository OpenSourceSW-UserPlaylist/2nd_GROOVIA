import os
import csv
import json
import tempfile
from django.core.management.base import BaseCommand

from spotify_app.services.apple_client import (
    get_track_id_by_name,
    fetch_apple_track_metadata,
    download_preview,
    extract_features_from_audio,
    build_metadata_vector,
    combine_feature_vectors,
)

from spotify_app.engines.HNSW_Engine import HNSWRecommender


# -----------------------------------------
# 1) 실험용 가중치 세트 (tempo, energy, mfcc, centroid)
# -----------------------------------------
WEIGHT_CASES = [
    (0.4, 0.3, 0.15, 0.15),
    (0.7, 0.2, 0.05, 0.05),
    (0.2, 0.6, 0.1, 0.1),
    (1.0, 0.3, 0.1, 0.1),
    (0.3, 1.0, 0.1, 0.1),
]


# -----------------------------------------
# 2) 테스트용 입력곡 (3곡 고정)
# -----------------------------------------
TEST_TRACKS = [
    ["NewJeans", "Super Shy"],
    ["The Weeknd", "Blinding Lights"],
    ["Coldplay", "Hymn For The Weekend"],
]


# ----------------------------------------------------
# Helper: trackName + artist 로 track_id 자동 변환
# ----------------------------------------------------
def resolve_track_ids():
    ids = []
    for artist, title in TEST_TRACKS:
        tid = get_track_id_by_name(f"{artist} {title}")
        if tid:
            ids.append(tid)
    return ids



# -----------------------------------------
# 3) 단일 Weight Case 실행
# -----------------------------------------
def run_experiment(track_ids, weights):

    tempo_w, energy_w, mfcc_w, centroid_w = weights

    # 1) 입력곡 분석
    final_vectors = []
    metadatas = []

    for tid in track_ids:
        meta = fetch_apple_track_metadata(tid)
        if not meta or "preview_url" not in meta:
            continue
        metadatas.append(meta)

        # 30초 다운로드
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as tmp:
            path = download_preview(meta["preview_url"], tmp.name)

        # feature
        audio_vec = extract_features_from_audio(path)
        os.remove(path)

        if audio_vec is None:
            continue

        meta_vec = build_metadata_vector(meta)
        full_vec = combine_feature_vectors(audio_vec, meta_vec)
        final_vectors.append(full_vec)

    # 2) 추천 엔진 호출
    rec = HNSWRecommender(dim=len(final_vectors[0]))

    # 가중치 적용
    rec.set_distance_weights(tempo_w, energy_w, mfcc_w, centroid_w)

    results, _ = rec.recommend(
        input_vectors=final_vectors,
        input_metadata_list=metadatas,
        top_k=10
    )

    return results



# -----------------------------------------
# 4) Management Command
# -----------------------------------------
class Command(BaseCommand):
    help = "Run HNSW recommendation weight experiments"

    def handle(self, *args, **options):
        track_ids = resolve_track_ids()

        if len(track_ids) < 3:
            self.stdout.write(self.style.ERROR("입력곡 track_id 변환 실패"))
            return

        all_rows = []

        for idx, weights in enumerate(WEIGHT_CASES, start=1):
            self.stdout.write(f"\n=== Case {idx} / Weights = {weights} ===")

            results = run_experiment(track_ids, weights)

            rec_titles = [f"{x['title']} ({x['artist']})" for x in results]

            all_rows.append([
                f"case_{idx}",
                weights[0], weights[1], weights[2], weights[3],
                "; ".join(rec_titles)
            ])

            self.stdout.write(f" -> 완료 (추천곡 수: {len(results)})")

        # -----------------------------------------
        # CSV 저장
        # -----------------------------------------
        out_csv = "hnsw_experiment_results.csv"

        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "case_name",
                "tempo_w", "energy_w", "mfcc_w", "centroid_w",
                "recommended_songs"
            ])
            writer.writerows(all_rows)

        self.stdout.write(self.style.SUCCESS(f"\nCSV 생성됨: {out_csv}"))
