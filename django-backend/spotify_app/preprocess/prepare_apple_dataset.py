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
TERMS_US = [

    # 알파벳
    *list("abcdefghijklmnopqrstuvwxyz"),

    # 2글자 조합 
    "lo","li","le","la","lu","ly",
    "he","hi","ha","ho","hu",
    "me","ma","mo","mi",
    "sa","se","si","so","su",
    "ta","te","ti","to",
    "ra","re","ri","ro","ru",
    "no","ne","na","ni","nu",
    "ki","ka","ko","ke","ku",
    "ch","sh","th","tr","br","dr","st","sp","cl","cr",
    "pr","pl","fr","fl","gr","gl","bl","sl","sm","sn",
    "wh","wr","sk","sc",

    # 기본 영어 단어
    "love","you","me","night","time","life","dream","day","world","home",
    "heart","light","baby","summer","blue","star","story","again","forever",
    "rain","sky","fire","dance","stay","run","way","high","alone","lost",
    "back","hold","new","old","feel","right","fall","wish","true","break",
    "moon","sun","girl","boy","with","without","never","always","happy",

    # 감정/상태 단어
    "hope","fear","pain","joy","cry","smile","tears","wild","free","cold",
    "warm","dark","bright","deep","sweet","bad","good","better","worst",

    # 자연·환경 단어
    "ocean","sea","river","water","wind","storm","snow","ice","earth",
    "sunset","sunrise","shadow","silver","gold","green","red","black","white",

    # 행동 기반 동사
    "listen","hear","show","make","take","move","touch","hurt","save",
    "lose","find","stay","go","come","fly","rise","falling","running",
]

TERMS_JP = [

    # 히라가나 기본 세트
    "あ","い","う","え","お",
    "か","き","く","け","こ",
    "さ","し","す","せ","そ",
    "た","ち","つ","て","と",
    "な","に","ぬ","ね","の",
    "は","ひ","ふ","へ","ほ",
    "ま","み","む","め","も",
    "や","ゆ","よ",
    "ら","り","る","れ","ろ",
    "わ","を","ん",

    # 가타카나로도 추가
    "ア","イ","ウ","エ","オ",
    "カ","キ","ク","ケ","コ",
    "サ","シ","ス","セ","ソ",
    "タ","チ","ツ","テ","ト",

    # 제목에서 매우 흔한 단어
    "愛","恋","夢","桜","空","光","心","星",
    "夜","海","夏","冬","雨","風","涙","花",
    "君","僕","私","未来","希望","世界"
]

TERMS_KR = [

    # 기본 자모 확장 (가-하)
    "가","거","고","구","기","겨","교","규","길",
    "나","너","노","누","니","녀","뉴","냐",
    "다","더","도","두","디","대","동",
    "라","러","로","루","리","레","료",
    "마","머","모","무","미","매","묘",
    "바","버","보","부","비","배",
    "사","서","소","수","시","세","쇼",
    "아","어","오","우","이","애","여","요","유",
    "자","저","조","주","지","재","줘",
    "차","처","초","추","치","채",
    "카","커","코","쿠","키",
    "타","터","토","투","티",
    "파","퍼","포","푸","피",
    "하","허","호","후","히","해","햐",

    # 인기 단어 기반
    "사랑","이별","시간","하루","밤","우리","나","너","꿈","길","마음","기억",
    "봄","여름","가을","겨울","별","눈","하늘","비","바람","햇살","세상",
    "빛","운명","희망","초록","그날","마지막","처음","순간",

    # 감정/형용사
    "행복","슬픔","외로움","그리움","온기","아픔",
    "따뜻한","차가운","조용한","소중한",

    # 동사 계열
    "다시","함께","영원","돌아","떠나","기다려","웃어","울어","만나","헤어져",
    "잊어","기억해","사라져","멈춰","달려","부서져",

    # 영어 혼용 
    "love","heart","boy","girl","dream","run","forever","light","blue","stay","fall","wish"
]

COUNTRY_TERMS = {
    "US": TERMS_US,
    "KR": TERMS_KR,
    "JP": TERMS_JP
}

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
# Search API
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
                time.sleep(0.75)
                return [item.get("trackId") for item in data.get("results", []) if item.get("trackId")]
        except:
            pass

        time.sleep(0.75)

    print(f"[Search Error] term='{term}' 실패")
    return []


# ======================================================
# Lookup API
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

        time.sleep(0.5)

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
        0,   
        item.get("trackTimeMillis", 0),
        explicit_to_numeric(item.get("trackExplicitness")),
        1, 1, 1,
        release_year
    ]


# ======================================================
# 병렬로 실행되는 작업 함수 
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
        "genre_name": item.get("primaryGenreName"),
        "release_date": item.get("releaseDate"),
        "vector": final_vec.tolist()
    }


# ======================================================
# 메인 로직
# ======================================================
def build_apple_dataset():
    print("\nApple Music dataset 수집 시작...")

    # ----------------------------------------------
    # 1) Search (병렬 처리)
    # ----------------------------------------------
    COUNTRIES = ["US", "JP", "KR"]

    # term-country 모든 조합 생성
    tasks = []
    for country in COUNTRIES:
        terms = COUNTRY_TERMS[country]
        for term in terms:
            tasks.append((term, country))

    print("\nParallel Searching terms...")

    all_ids = []
    with Pool(processes=max(cpu_count() // 2, 2)) as pool:
        results = list(tqdm(pool.imap(search_task, tasks), total=len(tasks)))

    for ids in results:
        all_ids.extend(ids)

    unique_ids = list(set(all_ids))
    print(f"\ntrackId 후보: {len(unique_ids)} 개")

    # ----------------------------------------------
    # 2) Lookup
    # ----------------------------------------------
    metadata_full = []
    batch_size = 200

    print("\nRunning Lookup batches...")

    for i in tqdm(range(0, len(unique_ids), batch_size)):
        batch = unique_ids[i:i + batch_size]
        results = lookup_tracks_batch(batch)

        for item in results:
            if item.get("previewUrl") and item.get("trackId"):
                metadata_full.append(item)

    print(f"\npreviewUrl 존재하는 곡: {len(metadata_full)} 개")

    # ----------------------------------------------
    # 3) 병렬 Feature Extraction
    # ----------------------------------------------
    print("\nExtracting audio features (Parallel)...")

    num_workers = max(cpu_count() - 1, 2)
    print(f"병렬 프로세스: {num_workers} core(s)")

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
                    "genre_name": result["genre_name"],
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
    print("Apple DB 생성 완료!")
    print(f"벡터 개수: {len(final_vectors)} tracks")
    print(f"저장 위치: {VECTORS_OUT}")
    print("=======================================")


# ======================================================
if __name__ == "__main__":
    build_apple_dataset()
