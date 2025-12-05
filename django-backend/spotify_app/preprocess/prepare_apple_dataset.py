import os
import json
import requests
import numpy as np
import tempfile
import time
import subprocess
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

from spotify_app.services.apple_client import extract_features_from_audio


# ======================================================
# 저장 경로 설정
# ======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "apple_db"))

os.makedirs(OUTPUT_DIR, exist_ok=True)

VECTORS_OUT = os.path.join(OUTPUT_DIR, "apple_vectors.npy")
META_OUT = os.path.join(OUTPUT_DIR, "apple_metadata.json")

SEARCH_URL = "https://itunes.apple.com/search"
LOOKUP_URL = "https://itunes.apple.com/lookup"

AUDIO_DIM = 37
LIMIT_PER_TERM = 200


# ======================================================
# 검색 term 목록
# ======================================================
SEARCH_TERMS = []

# 알파벳 검색 추가 (26개)
for ch in "abcdefghijklmnopqrstuvwxyz":
    SEARCH_TERMS.append(ch)

# 2–3글자 keyword 추가
COMMON = ["lo", "li", "he", "me", "sa", "ta"]
SEARCH_TERMS += COMMON

# 일반 영어 단어 추가
BASIC = ["love", "you", "me", "night", "time", "life", "dream"]
SEARCH_TERMS += BASIC


# ======================================================
# 기본 유틸 함수
# ======================================================
def safe_json(r):
    try:
        return r.json()
    except:
        return None


def convert_to_wav(input_path, output_path):
    cmd = [
        "ffmpeg", "-y",
        "-loglevel", "quiet",
        "-i", input_path,
        "-ar", "22050",
        "-ac", "1",
        output_path
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        return output_path
    return None

def search_task(args):
        term, country = args
        return search_track_ids(term, country)

# ======================================================
# 1) Search API
# ======================================================
def search_track_ids(term, country="US"):
    params = {
        "term": term,
        "media": "music",
        "entity": "song",
        "limit": LIMIT_PER_TERM,
        "country": country
    }

    for attempt in range(2):
        try:
            r = requests.get(SEARCH_URL, params=params, timeout=5)
            data = safe_json(r)
            if data:
                time.sleep(0.15)
                return [item.get("trackId") for item in data.get("results", []) if item.get("trackId")]
        except:
            pass

        time.sleep(0.15)

    print(f"[Search Error] term='{term}' 실패")
    return []


# ======================================================
# 2) Lookup API
# ======================================================
def lookup_tracks_batch(track_ids):
    joined = ",".join(str(tid) for tid in track_ids)
    params = {"id": joined, "entity": "song"}

    for attempt in range(2):
        try:
            r = requests.get(LOOKUP_URL, params=params, timeout=5)
            data = safe_json(r)
            if data:
                return data.get("results", [])
        except:
            pass

        time.sleep(0.05)

    print("[Lookup Error] batch 조회 실패")
    return []


# ======================================================
# Metadata vector builder
# ======================================================
def explicit_to_numeric(value: str):
    mapping = {"notExplicit": 0, "cleaned": 1, "explicit": 2}
    return mapping.get(value, 0)


def build_metadata_vector(item):
    release_year = 0
    if item.get("releaseDate"):
        release_year = int(item["releaseDate"][:4])

    return [
        item.get("primaryGenreId", 0),
        item.get("trackTimeMillis", 0),
        explicit_to_numeric(item.get("trackExplicitness")),
        1, 1, 1,
        release_year
    ]


# ======================================================
# 🔥 병렬로 실행되는 작업 함수 (가장 중요)
# ======================================================
def process_track(item):
    """
    previewUrl 다운로드 → m4a → wav 변환 → feature 추출
    실패 시 None 반환
    """
    preview = item["previewUrl"]
    track_id = item["trackId"]

    # 1) m4a 다운로드
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as tmp:
            r = requests.get(preview, timeout=10)
            tmp.write(r.content)
            m4a_path = tmp.name
    except:
        return None

    # 2) m4a → wav
    wav_path = m4a_path.replace(".m4a", ".wav")
    wav_path = convert_to_wav(m4a_path, wav_path)
    os.remove(m4a_path)

    if not wav_path:
        return None

    # 3) Feature extract
    try:
        audio_vec = extract_features_from_audio(wav_path)
    except:
        audio_vec = None

    os.remove(wav_path)

    if audio_vec is None or len(audio_vec) != AUDIO_DIM:
        return None

    # 4) metadata vector
    meta_vec = build_metadata_vector(item)
    final_vec = np.concatenate([audio_vec, np.array(meta_vec)])

    # 최종 반환 값
    return {
        "track_id": track_id,
        "title": item.get("trackName"),
        "artist": item.get("artistName"),
        "preview_url": preview,
        "genre_id": item.get("primaryGenreId"),
        "release_date": item.get("releaseDate"),
        "vector": final_vec.tolist()
    }


# ======================================================
# 메인 로직
# ======================================================
def build_apple_dataset():
    print("\n🎵 Apple Music dataset 수집 시작...")

    # ----------------------------------------------
    # 1) Search (병렬 처리)
    # ----------------------------------------------
    COUNTRIES = ["US", "JP", "KR"]

    # term-country 모든 조합 생성
    tasks = []
    for term in SEARCH_TERMS:
        for country in COUNTRIES:
            tasks.append((term, country))

    print("\n🔍 Parallel Searching terms...")

    all_ids = []
    with Pool(processes=max(cpu_count() // 2, 2)) as pool:
        results = list(tqdm(pool.imap(search_task, tasks), total=len(tasks)))

    for ids in results:
        all_ids.extend(ids)

    unique_ids = list(set(all_ids))
    print(f"\n🔍 trackId 후보: {len(unique_ids)} 개")

    # ----------------------------------------------
    # 2) Lookup
    # ----------------------------------------------
    metadata_full = []
    batch_size = 200

    print("\n📡 Running Lookup batches...")

    for i in tqdm(range(0, len(unique_ids), batch_size)):
        batch = unique_ids[i:i + batch_size]
        results = lookup_tracks_batch(batch)

        for item in results:
            if item.get("previewUrl") and item.get("trackId"):
                metadata_full.append(item)

    print(f"\n🎧 previewUrl 존재하는 곡: {len(metadata_full)} 개")

    # ----------------------------------------------
    # 🔥 3) 병렬 Feature Extraction
    # ----------------------------------------------
    print("\n🎧 Extracting audio features (Parallel)...")

    num_workers = max(cpu_count() - 1, 2)
    print(f"🧵 병렬 프로세스: {num_workers} core(s)")

    final_vectors = []
    metadata_list = []

    with Pool(processes=num_workers) as pool:
        for result in tqdm(pool.imap(process_track, metadata_full), total=len(metadata_full)):
            if result:
                metadata_list.append({
                    "track_id": result["track_id"],
                    "title": result["title"],
                    "artist": result["artist"],
                    "preview_url": result["preview_url"],
                    "genre_id": result["genre_id"],
                    "release_date": result["release_date"]
                })
                final_vectors.append(result["vector"])

    # ----------------------------------------------
    # 4) Save
    # ----------------------------------------------
    np.save(VECTORS_OUT, np.array(final_vectors))

    with open(META_OUT, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, indent=2, ensure_ascii=False)

    print("\n=======================================")
    print("✅ Apple DB 생성 완료!")
    print(f"📦 벡터 개수: {len(final_vectors)} tracks")
    print(f"📌 저장 위치: {VECTORS_OUT}")
    print("=======================================")


# ======================================================
if __name__ == "__main__":
    build_apple_dataset()
