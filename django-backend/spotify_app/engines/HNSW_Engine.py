import hnswlib
import numpy as np
import json
import math
import os
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class HNSWRecommender:
    def __init__(self, dim=None, space="cosine"):
        self.index = None
        self.dim = dim
        self.space = space
        self.loaded = False
        self.vectors = None
        self.id_map = None

        # 테스트용 가중치 세팅
        self.distance_weights = {
            "tempo": 0.4,
            "energy": 0.3,
            "mfcc_mean": 0.15,
            "spectral_centroid": 0.15
        }

    # ------------------------------------------------------------
    # 리턴 json파일에 album_image, apple_music_url 추가
    # ------------------------------------------------------------
    def enrich_apple_metadata(self, item):
        """
        item: 추천 결과 한 개 (dict)
        필요한 정보(album_image, apple_music_url)를 Apple Lookup API에서 보완
        """
        tid = item["track_id"]
        url = f"https://itunes.apple.com/lookup?id={tid}"

        try:
            res = requests.get(url, timeout=3)
            data = res.json()

            if data.get("resultCount", 0) > 0:
                info = data["results"][0]

                item["album_image"] = info.get("artworkUrl100")
                item["apple_music_url"] = info.get("trackViewUrl") or info.get("collectionViewUrl")

        except Exception as e:
            # 기본값 fallback
            item["album_image"] = None
            item["apple_music_url"] = None

        return item

    # ------------------------------------------------------------
    # Load index + metadata
    # ------------------------------------------------------------
    def load_index(self):
        vectors_path = os.path.join(BASE_DIR, "../data/apple_db/apple_vectors.npy")
        id_map_path = os.path.join(BASE_DIR, "../data/apple_db/apple_metadata.json")

        # Load final vectors (audio_vec + meta_vec 결합한 DB 벡터)
        self.vectors = np.load(vectors_path)
        num_items, vec_dim = self.vectors.shape

        if self.dim is None:
            self.dim = vec_dim

        # Load metadata dict list
        with open(id_map_path, "r", encoding="utf-8") as f:
            self.id_map = json.load(f)

        # Create index
        self.index = hnswlib.Index(self.space, dim=self.dim)
        self.index.init_index(
            max_elements=num_items,
            ef_construction=400,
            M=32
        )

        self.index.add_items(self.vectors, np.arange(num_items))
        self.index.set_ef(200)

        self.loaded = True

    # ------------------------------------------------------------
    # Query vector = 입력된 여러 곡 벡터 평균
    # ------------------------------------------------------------
    def build_query_vector(self, vectors: list):
        if len(vectors) == 0:
            raise ValueError("vectors list is empty")
        return np.mean(np.vstack(vectors), axis=0)

    # ------------------------------------------------------------
    # Search (labels + metadata 둘 다 반환)
    # ------------------------------------------------------------
    def search_hnsw(self, query_vector, k=200):
        if not self.loaded:
            self.load_index()

        labels, distances = self.index.knn_query(query_vector, k=k)
        labels = labels[0].tolist()

        # metadata + label(index) 같이 반환
        results = []
        for idx in labels:
            data = self.id_map[idx].copy()
            data["idx"] = idx  # vector 접근용 label 추가
            results.append(data)

        return results

    # ------------------------------------------------------------
    # Post-filter: 메타데이터 기반 필터
    # ------------------------------------------------------------
    def post_filter(self, items, query_meta, max_year_gap=20):
        filtered = []

        for item in items:
            # 1) 연도 차이 필터
            try:
                year = int(item["release_date"][:4])
                q_year = int(query_meta["release_date"][:4])
                if abs(year - q_year) > max_year_gap:
                    continue
            except:
                pass

            # 2) 장르 차이
            query_major = self.infer_major_genre(query_meta)
            item_major = self.infer_major_genre(item)

            # genre mismatch가 강하면 제외
            incompatible = {
                ("pop", "country"),
                ("pop", "hiphop"),
                ("rnb", "country"),
                ("rnb", "rock"),
            }

            if (query_major, item_major) in incompatible:
                continue

            # 3) acousticness 필터
            if item.get("acousticness") and item["acousticness"] > 0.7:
                continue

            # 4) energy 필터
            if item.get("energy") and item["energy"] < 0.2:
                continue

            filtered.append(item)

        return filtered
    
    # ------------------------------------------------------------
    # Genre preprocessing: 입력곡 장르 기반 major-genre 결정
    # ------------------------------------------------------------
    def infer_major_genre(self, meta):
        """
        Apple Music의 genre_id는 불규칙하므로,
        primaryGenreName 또는 genreName 기반으로 major-genre를 추출하는 함수.
        """
        g = (meta.get("genre_name") or meta.get("genre_id") or meta.get("primaryGenreName") or meta.get("genreName") or "").lower()
        # Pop / Dance / Electronic 그룹
        if any(x in g for x in ["pop", "k-pop", "dance", "electronic", "edm"]):
            return "pop"

        # R&B 그룹
        if any(x in g for x in ["r&b", "soul"]):
            return "rnb"

        # Hip-hop / Rap 그룹
        if "hip" in g or "rap" in g:
            return "hiphop"

        # Rock 그룹
        if "rock" in g:
            return "rock"

        # Country 그룹
        if any(x in g for x in ["country", "folk"]):
            return "country"

        # 그 외 기타 장르
        return "etc"

    # ------------------------------------------------------------
    # 가중치 설정 함수
    # ------------------------------------------------------------

    def set_distance_weights(self, tempo, energy, mfcc_mean, spectral_centroid):
        """
        weight가 None이면 기존 weight 유지
        실험 코드에서만 사용하도록 설계
        """
        if tempo is not None:
            self.distance_weights["tempo"] = tempo
        if energy is not None:
            self.distance_weights["energy"] = energy
        if mfcc_mean is not None:
            self.distance_weights["mfcc_mean"] = mfcc_mean
        if spectral_centroid is not None:
            self.distance_weights["spectral_centroid"] = spectral_centroid

    # ------------------------------------------------------------
    # 가중치 계산 함수
    # ------------------------------------------------------------
    def calculate_weighted_distance(self, target, candidate):
        weights = self.distance_weights  # 항상 self 기준

        total = 0.0
        for name, w in weights.items():
            diff = target.get(name, 0.5) - candidate.get(name, 0.5)
            total += w * (diff ** 2)

        return math.sqrt(total)
    
    # ------------------------------------------------------------
    # 음악 키워드 추출 함수
    # ------------------------------------------------------------
    def get_keywords_from_features(self, features):

        keywords = []

        # 1) Raw 값
        tempo_raw = features.get('tempo', 100)  # BPM
        energy = features.get('energy', 0.2)
        mfcc_raw = features.get('mfcc_mean', -100)
        centroid_raw = features.get('spectral_centroid', 2000)

        # 2) 개선된 Normalization
        tempo = min(max((tempo_raw - 60) / 120, 0), 1)  # 60~180 기준
        centroid = min(max((centroid_raw - 1500) / 2000, 0), 1)  # 1500~3500 기준
        # MFCC는 그대로 raw 사용

        # <A. BPM + Energy 조합>
        high_tempo = tempo > 0.65     # 140 BPM 이상
        low_tempo  = tempo < 0.35     # 100 BPM 이하

        high_energy = energy > 0.30
        low_energy  = energy < 0.18

        # 1. 빠르고 강한 -> 파티/운동
        if high_tempo and high_energy:
            keywords += ["#신나는", "#파티", "#텐션업", "#질주본능"]

        # 2. 느리고 조용한 -> 잔잔/새벽
        elif low_tempo and low_energy:
            keywords += ["#잔잔한", "#새벽감성", "#위로", "#혼자있을때"]

        # 3. 빠르지만 부드러운 -> 드라이브
        elif high_tempo and low_energy:
            keywords += ["#드라이브", "#산책", "#경쾌한", "#기분전환"]

        # 4. 느리지만 강한 -> 비트/그루브
        elif low_tempo and high_energy:
            keywords += ["#그루브", "#비트감", "#힙합", "#묵직한"]


        # <B. Spectral Centroid (밝기)>
        if centroid_raw > 2600:
            keywords += ["#청량한", "#시원한"]
        elif centroid_raw < 1500:
            keywords += ["#따뜻한", "#몽환적인"]
        else:
            keywords += ["#감성적인", "#편안한"]

        # <C. MFCC (음색의 복잡도)>
        if mfcc_raw > -90:
            keywords.append("#풍부한사운드")
        elif mfcc_raw < -150:
            keywords.append("#미니멀")
        else:
            keywords.append("#트렌디한")

        return list(set(keywords))[:4]

    # ------------------------------------------------------------
    # Re-ranking 
    # ------------------------------------------------------------
    def rerank(self, items, query_vector, query_meta):

        # query_vector에서 4개 feature 추출
        query_features = {
            "tempo": query_vector[0],
            "spectral_centroid": query_vector[1],
            "mfcc_mean": float(query_vector[5]),   # 첫 번째 mfcc
            "energy": float(query_vector[4]),      # rms
        }

        for item in items:
            idx = item["idx"]
            v = self.vectors[idx]

            # DB 벡터에서 동일 feature 추출
            candidate_features = {
                "tempo": v[0],
                "spectral_centroid": v[1],
                "mfcc_mean": float(v[5]),
                "energy": float(v[4]),
            }

            # 가중치 거리 계산
            dist = self.calculate_weighted_distance(query_features, candidate_features)

            # 점수 변환: 거리가 작을수록 점수 높음
            score = 1 / (1 + dist)

            # 장르 mismatch penalty
            query_major = self.infer_major_genre(query_meta)
            item_major = self.infer_major_genre(item)

            if item_major != query_major:
                score *= 0.85  # soft penalty

            # mood penalty (tempo/energy/centroid mismatch)
            if query_features["tempo"] > 0.55 and candidate_features["tempo"] < 0.45:
                score *= 0.8

            if query_features["energy"] > 0.55 and candidate_features["energy"] < 0.45:
                score *= 0.8

            if query_features["spectral_centroid"] > 0.55 and candidate_features["spectral_centroid"] < 0.45:
                score *= 0.85

            if item_major in ["country", "hiphop"] and query_major in ["pop", "rnb"]:
                score *= 0.7

            item["score"] = score

            # 분위기 태그 추가
            item["mood_keywords"] = self.get_keywords_from_features(candidate_features)

        # 점수 높은 순 정렬
        items.sort(key=lambda x: x["score"], reverse=True)
        return items


    # ------------------------------------------------------------
    # Final recommend
    # ------------------------------------------------------------
    def recommend(self, input_vectors, input_metadata_list, top_k=10):

        # 평균 벡터
        qvec = self.build_query_vector(input_vectors)

        # 비교용 메타데이터(첫 곡)
        query_meta = input_metadata_list[0]

        # 1) Top-200 from HNSW
        raw_items = self.search_hnsw(qvec, k=200)

        # 2) Filter
        filtered = self.post_filter(raw_items, query_meta)

        # 3) Re-rank
        reranked = self.rerank(filtered, qvec, query_meta)

        final_items = reranked

        unique = []
        seen = set()
        
        # 중복 제거
        for item in final_items:
            key = (item["title"].strip().lower(), item["artist"].strip().lower())
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
            if len(unique) >= top_k:
                break

        # Json 변환
        results = []
        mood_keywords = []
        for item in unique:
            enriched = self.enrich_apple_metadata(item)

            results.append({
                "track_id": enriched["track_id"],
                "title": enriched["title"],
                "artist": enriched["artist"],
                "album_image": enriched.get("album_image"),
                "apple_music_url": enriched.get("apple_music_url"),
            })

            if not mood_keywords:
                mood_keywords.append(enriched.get("mood_keywords", []))

        return results, mood_keywords
    
        '''
        return reranked[:top_k]
        '''

    