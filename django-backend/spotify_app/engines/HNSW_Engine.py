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
            if query_meta.get("genre_id") and item.get("genre_id"):
                if abs(item["genre_id"] - query_meta["genre_id"]) >= 3:
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
    # 가중치 계산 함수
    # ------------------------------------------------------------

    def calculate_weighted_distance(self, target, candidate):
        weights = {
            "tempo": 0.4,
            "energy": 0.3,
            "mfcc_mean": 0.15,
            "spectral_centroid": 0.15
        }

        total = 0.0
        for name, w in weights.items():
            diff = target.get(name, 0.5) - candidate.get(name, 0.5)
            total += w * (diff ** 2)

        return math.sqrt(total)
    

    def get_keywords_from_features(self, features):
        '''
        Librosa로 추출된 4가지 특징(0.0 ~ 1.0 정규화된 값)을 받아
        분위기 키워드를 반환하는 함수
        '''
        keywords = []

        # 1. 값 가져오기 (기본값 0.5)
        tempo = features.get('tempo', 0.4)          # 가중치 0.4 (가장 중요)
        energy = features.get('energy', 0.3)        # 가중치 0.3
        mfcc = features.get('mfcc_mean', 0.15)       # 가중치 0.15 (음색)
        centroid = features.get('spectral_centroid', 0.15) # 가중치 0.15 (밝기)

        # 로직 A: BPM & Energy 조합 (가중치 상위 70% 차지)
    
        # 1. 빠르고 강한 노래 (파티/운동)
        if tempo > 0.7 and energy > 0.7:
            keywords.extend(["#신나는", "#파티", "#텐션업", "#질주본능"])
    
        # 2. 느리고 조용한 노래 (휴식/새벽)
        elif tempo < 0.4 and energy < 0.4:
            keywords.extend(["#잔잔한", "#새벽감성", "#위로", "#혼자있을때"])
    
        # 3. 빠르지만 부드러운 노래 (드라이브/기분전환)
        elif tempo > 0.6 and energy < 0.6:
            keywords.extend(["#드라이브", "#산책", "#기분전환", "#경쾌한"])
    
        # 4. 느리지만 강렬한 노래 (비트감/그루브)
        elif tempo < 0.5 and energy > 0.6:
            keywords.extend(["#그루브", "#비트감", "#힙합", "#묵직한"])

        # 로직 B: Spectral Centroid (밝기/음색 - 가중치 0.15)
        if centroid > 0.7:
            keywords.append("#청량한")
            keywords.append("#시원한")
        elif centroid < 0.3:
            keywords.append("#따뜻한")
            keywords.append("#몽환적인")

        # 로직 C: MFCC (소리의 풍부함/독특함 - 가중치 0.15)
        # MFCC 값이 높으면 소리가 복잡/풍부, 낮으면 깔끔/심플
        if mfcc > 0.7:
            keywords.append("#풍부한사운드")
        elif mfcc < 0.3:
            keywords.append("#미니멀")

        return keywords

    # ------------------------------------------------------------
    # Re-ranking (벡터는 self.vectors[idx] 에서 직접 불러옴)
    # ------------------------------------------------------------
    def rerank(self, items, query_vector, query_meta):

        # 🔥 query_vector에서 4개 feature 추출
        query_features = {
            "tempo": query_vector[0],
            "spectral_centroid": query_vector[1],
            "mfcc_mean": float(query_vector[5]),   # 첫 번째 mfcc
            "energy": float(query_vector[4]),      # rms
        }

        for item in items:
            idx = item["idx"]
            v = self.vectors[idx]

            # 🔥 DB 벡터에서 동일 feature 추출
            candidate_features = {
                "tempo": v[0],
                "spectral_centroid": v[1],
                "mfcc_mean": float(v[5]),
                "energy": float(v[4]),
            }

            # 🔥 가중치 거리 계산
            dist = self.calculate_weighted_distance(query_features, candidate_features)

            # 🔥 점수 변환 — 거리가 작을수록 점수↑
            score = 1 / (1 + dist)
            item["score"] = score

            # 🔥 분위기 태그 추가 (optional)
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
                "preview_url": enriched.get("preview_url"), # 사용 안할 경우 제외
            })

            if not mood_keywords:
                mood_keywords.append(enriched.get("mood_keywords", []))

        return results, mood_keywords
    
        '''
        return reranked[:top_k]
        '''

    