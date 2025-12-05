# spotify_app/services/apple_client.py
import requests
import librosa
import numpy as np

ITUNES_LOOKUP_URL = "https://itunes.apple.com/lookup"


# ===============================
# 음악의 기본 metadata 가져오는 함수
# ===============================
def fetch_apple_track_metadata(track_id: int):

    url = f"{ITUNES_LOOKUP_URL}?id={track_id}"
    
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
    except:
        return None
    
    results = data.get("results", [])
    if not results:
        return None
    
    item = results[0]   # trackId로 조회했으므로 정확히 1개
    
    # 필요한 필드 변환
    meta = {
        "genre_id": item.get("primaryGenreId", 0),
        "track_time_ms": item.get("trackTimeMillis", 0),
        "explicitness": item.get("trackExplicitness", "notExplicit"),
        "is_streamable": item.get("isStreamable", True),
        "disc_number": item.get("discNumber", 0),
        "disc_count": item.get("discCount", 0),
        "release_year": int(item.get("releaseDate", "1970")[:4]),
        
        # 추가로 반환하면 좋은 보조 정보
        "title": item.get("trackName"),
        "artist": item.get("artistName"),
        "preview_url": item.get("previewUrl"),
        "cover_url": item.get("artworkUrl100"),
    }

    return meta


# ======================================
# 30초 url에서 metadata 추출 함수(librosa)
# ======================================
def extract_features_from_audio(file_path):

    try:
        y, sr = librosa.load(file_path, sr=22050, mono=True)
    except Exception as e:
        print("  ❌ librosa.load 실패:", e)
        return None

    # Tempo
    try:
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        tempo = float(tempo)
    except:
        tempo = 0.0

    # MFCC (13)
    try:
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        # 만약 mfcc가 (13, N)이 아니면 강제로 shape 맞춤
        if mfcc.shape[0] != 13:
            print("  ❗ MFCC shape 보정:", mfcc.shape)
            mfcc_fixed = np.zeros((13, mfcc.shape[1]))
            num = min(13, mfcc.shape[0])
            mfcc_fixed[:num, :] = mfcc[:num, :]
            mfcc = mfcc_fixed

        mfcc_mean = np.mean(mfcc, axis=1)
    except Exception as e:
        print("  ❌ MFCC 실패:", e)
        mfcc_mean = np.zeros(13)

    # Centroid
    try:
        sc = librosa.feature.spectral_centroid(y=y, sr=sr)
        spec_centroid = float(np.mean(sc))
    except:
        spec_centroid = 0.0

    # Bandwidth
    try:
        sb = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        spec_bandwidth = float(np.mean(sb))
    except:
        spec_bandwidth = 0.0

    # ZCR
    try:
        zc = librosa.feature.zero_crossing_rate(y)
        zcr = float(np.mean(zc))
    except:
        zcr = 0.0

    # RMS
    try:
        rms = float(np.mean(librosa.feature.rms(y=y)))
    except:
        rms = 0.0

    # Spectral Contrast
    try:
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        contrast_mean = np.mean(contrast, axis=1)
    except:
        contrast_mean = np.zeros(7)

    # Chroma
    try:
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
    except:
        chroma_mean = np.zeros(12)

    # Final vector
    feature_vector = np.array([
        tempo,
        spec_centroid,
        spec_bandwidth,
        zcr,
        rms,
        *mfcc_mean,
        *contrast_mean,
        *chroma_mean
    ], dtype=float)

    if feature_vector.shape[0] != 37:
        print("❌ vector length mismatch:", feature_vector.shape)
        return None

    return feature_vector


def download_preview(url, save_path):
    r = requests.get(url)
    with open(save_path, "wb") as f:
        f.write(r.content)
    return save_path


"""
'곡명 + 아티스트명' 문구를 넣으면 가장 정확한 trackId 반환
"""
def get_track_id_by_name(term: str):
    
    url = "https://itunes.apple.com/search"
    params = {
        "term": term,
        "limit": 1,       # 가장 유사한 1곡만
        "media": "music"  # 음악만 검색
    }

    r = requests.get(url, params=params)
    results = r.json().get("results", [])

    if not results:
        return None
    
    return results[0].get("trackId")


def explicit_to_numeric(value: str):
    mapping = {
        "notExplicit": 0,
        "cleaned": 1,
        "explicit": 2
    }
    return mapping.get(value, 0)


def build_metadata_vector(meta):
    return np.array([
        meta["genre_id"] or 0,
        meta["track_time_ms"] or 0,
        explicit_to_numeric(meta["explicitness"]),
        1 if meta["is_streamable"] else 0,
        meta["disc_number"] or 0,
        meta["disc_count"] or 0,
        meta["release_year"] or 0,
    ], dtype=float)

def combine_feature_vectors(audio_vec, meta_vec):
    return np.concatenate([audio_vec, meta_vec])


# ======================================
# 입력받은 문자열 -> ['artist','title'] 형식 수정
# ======================================
def parse_artist_title_list(items: list[str] | None) -> list[list[str]]:

    if not items:
        return []

    result = []

    for item in items[:3]:  # 최대 3개만 처리
        if not item or "," not in item:
            continue  # 형식 불량 → 스킵

        # "아티스트, 제목" → ["아티스트", "제목"]
        parts = item.split(",", 1)  # 왼쪽부터 1번만 split
        artist = parts[0].strip()
        title = parts[1].strip()

        if artist and title:
            result.append([artist, title])

    return result
