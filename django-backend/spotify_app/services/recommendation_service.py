# spotify_app/services/recommendation_service.py
import os
import tempfile
import numpy as np

from .apple_client import fetch_apple_track_metadata, download_preview, extract_features_from_audio, build_metadata_vector, combine_feature_vectors
from spotify_app.engines.HNSW_Engine import HNSWRecommender
from csv_tools.csv_manager import save_features_to_csv


def run_recommendation(track_ids):

    final_vectors = []
    metadatas = []

    for tid in track_ids:
        
        # 1) 기본 메타데이터 추출
        meta = fetch_apple_track_metadata(tid)
        if not meta or "preview_url" not in meta:
            print("fail to get meta or preview_url")
            continue

        # 메타데이터 저장
        metadatas.append(meta)

        # 2) 30초 preview 다운로드
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as tmp:
            audio_m4a = download_preview(meta["preview_url"], tmp.name)

        # 3) 30초 preview의 vector 추출
        audio_vec = extract_features_from_audio(audio_m4a)
        os.remove(audio_m4a)

        if audio_vec is None: # 오디오 분석 실패한 트랙은 스킵
            print("fail to analyze")
            continue

        # 4) 기본 metadata vector 추출
        meta_vec = build_metadata_vector(meta)

        # 5) 두 벡터 병합
        try:
            final_vec = combine_feature_vectors(audio_vec, meta_vec)
        except Exception:
            continue
        
        # (features.csv에 저장)
        save_features_to_csv(
            title=meta["title"],
            artist=meta["artist"],
            final_vec=final_vec
        )

        final_vectors.append(final_vec)

    # 6) 유효한 track 없는 경우
    if len(final_vectors) == 0:
        raise ValueError("유효한 track 분석 실패: 모든 preview audio 벡터 추출 실패.")

    # 7) HNSW recommender 사용
    recommender = HNSWRecommender(dim=len(final_vectors[0]))
    results, mood_keywords = recommender.recommend(
        input_vectors=final_vectors,          # 여러 곡의 결합 벡터 리스트
        input_metadata_list=metadatas,       # 각 곡의 metadata 리스트
        top_k=10
    )

    return results, mood_keywords

