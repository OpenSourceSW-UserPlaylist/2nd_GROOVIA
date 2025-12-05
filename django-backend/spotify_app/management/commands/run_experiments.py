def get_keywords_from_features(features):
    """
    Librosa로 추출된 4가지 특징(0.0 ~ 1.0 정규화된 값)을 받아
    분위기 키워드를 반환하는 함수
    """
    keywords = []

    # 1. 값 가져오기 (기본값 0.5)
    tempo = features.get('tempo', 0.5)          # 가중치 0.4 (가장 중요)
    energy = features.get('energy', 0.5)        # 가중치 0.3
    mfcc = features.get('mfcc_mean', 0.5)       # 가중치 0.15 (음색)
    centroid = features.get('spectral_centroid', 0.5) # 가중치 0.15 (밝기)

    # =========================================================
    # 로직 A: BPM & Energy 조합 (가중치 상위 70% 차지)
    # =========================================================
    
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

    # =========================================================
    # 로직 B: Spectral Centroid (밝기/음색 - 가중치 0.15)
    # =========================================================
    if centroid > 0.7:
        keywords.append("#청량한")
        keywords.append("#시원한")
    elif centroid < 0.3:
        keywords.append("#따뜻한")
        keywords.append("#몽환적인")

    # =========================================================
    # 로직 C: MFCC (소리의 풍부함/독특함 - 가중치 0.15)
    # =========================================================
    # MFCC 값이 높으면 소리가 복잡/풍부, 낮으면 깔끔/심플
    if mfcc > 0.7:
        keywords.append("#풍부한사운드")
    elif mfcc < 0.3:
        keywords.append("#미니멀")

    return keywords




import math

def calculate_weighted_distance(target, candidate):
    """
    사용자가 입력한 노래(target)와 DB 노래(candidate) 사이의 거리를 계산
    요청하신 가중치를 적용하여 거리를 측정함.
    """
    
    # ★ 요청하신 가중치 설정
    weights = {
        "tempo": 0.4,             # BPM (40%)
        "energy": 0.3,            # Energy (30%)
        "mfcc_mean": 0.15,        # MFCC (15%)
        "spectral_centroid": 0.15 # Brightness (15%)
    }

    total_distance = 0.0

    # 각 특징별로 (차이^2 * 가중치)를 계산
    for feature_name, weight in weights.items():
        v1 = target.get(feature_name, 0.5)
        v2 = candidate.get(feature_name, 0.5)
        
        # 차이 계산
        diff = v1 - v2
        
        # 가중치를 적용하여 거리에 더함
        # 가중치가 클수록 차이가 날 때 벌점이 커짐 -> 더 엄격하게 비슷한 걸 찾음
        total_distance += weight * (diff ** 2)

    # 유클리드 거리 반환 (작을수록 유사함)
    return math.sqrt(total_distance)