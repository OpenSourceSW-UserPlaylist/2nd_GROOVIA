from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from spotify_app.services.recommendation_service import run_recommendation
from spotify_app.services.apple_client import get_track_id_by_name, parse_artist_title_list
from csv_tools.csv_manager import save_song_to_csv

from dotenv import load_dotenv
from django.conf import settings

load_dotenv()

# ============================================================
# 모드 스위치
# ============================================================
ACTIVAE_MODE = getattr(settings, "ACTIVAE_MODE", "A")   
# 기본값 A(Flutter POST 모드) / B(브라우저 테스트 모드)



# ============================================================
# B 모드: runserver + 브라우저 GET → 자동 추천 실행 (테스트용)
# ============================================================
class AppleRecommendView(APIView):

    def get(self, request):

        # 테스트용 기본 sample 3개
        sample = [
            ["아이유", "밤편지"],
            ["임창정", "소주한잔"],
            ["Dean", "instagram"]
        ]

        # ================================
        # 1. 곡명 + 아티스트명 → trackId 변환
        # ================================
        track_ids = []
        for artist, title in sample:
            term = f"{artist} {title}"
            tid = get_track_id_by_name(term)
            if tid:
                track_ids.append(tid)

        if not track_ids:
            return Response(
                {"error": "기본 테스트 곡들의 trackId 검색 실패"},
                status=400
            )

        # ================
        # 2. 추천 로직 실행
        # ================
        results, mood_keywords = run_recommendation(track_ids)

        # songs.csv에 저장
        for song in results:
            save_song_to_csv({
                "title": song.get("title", ""),
                "artist": song.get("artist", ""),
                "genre": "Recommended",
                "bpm": 0,
                "mood": "Recommended"
            })

        return Response({
            "message": "Apple 테스트 추천 실행 완료",
            "input_ids": sample,
            "mood_keywords": mood_keywords,
            "recommended": results
        })

    def post(self, request):
        return Response({
            "error": "이 URL은 GET 테스트용입니다. POST가 아닙니다."
        }, status=405)
        



# ============================================================
# A 모드: Flutter POST → URL 목록 → track_id 추출 → 추천
# ============================================================
class AppleUrlProcessView(APIView):

    def get(self, request):
        return Response({"msg": "GET received. 이 Endpoint는 POST용입니다."})

    def post(self, request):

        # ---------------------------------------------------
        # 0) 모드 체크
        # ---------------------------------------------------
        if ACTIVAE_MODE != "A":
            return Response(
                {"error": "현재 모드는 A(Flutter POST 모드)가 아닙니다."},
                status=400
            )

        # ---------------------------------------------------
        # 1) URL 리스트 추출
        # ---------------------------------------------------
        input_info = request.data.get("urls", [])

        if not input_info:
            return Response(
                {"error": "URL 리스트가 비어있습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------------------------------------------
        # 2) Artist-Title parsing
        # ---------------------------------------------------
        try:
            parsed_track_info = parse_artist_title_list(input_info)
        except Exception as e:
            return Response(
                {"error": f"artist-title parsing 오류: {str(e)}"},
                status=400
            )

        # ---------------------------------------------------
        # 3) TrackId 검색
        # ---------------------------------------------------
        track_ids = []
        print("\ntrack_id 검색 시작")

        for artist, title in parsed_track_info:
            term = f"{artist} {title}"
            print(f"  > 검색 term = '{term}'")

            try:
                tid = get_track_id_by_name(term)
                print("검색 결과 tid =", tid)
            except Exception as e:
                print("get_track_id_by_name 실패:", e)
                continue

            if tid:
                track_ids.append(tid)

        print("최종 track_ids =", track_ids)

        if not track_ids:
            return Response(
                {"error": "기본 테스트 곡들의 trackId 검색 실패"},
                status=400
            )

        # ---------------------------------------------------
        # 4) Apple 추천 실행
        # ---------------------------------------------------
        print("\nApple 추천 실행 시작...")
        try:
            results, mood_keywords = run_recommendation(track_ids)
        except Exception as e:
            return Response(
                {"error": f"추천 실행 중 오류 발생: {str(e)}"},
                status=500
            )

        print("\n추천 결과:")
        print("results =", results)
        print("mood_keywords =", mood_keywords)

        # ---------------------------------------------------
        # 5) songs.csv 저장
        # ---------------------------------------------------
        print("\nsongs.csv 저장 시작")
        for song in results:
            try:
                save_song_to_csv({
                    "title": song.get("title", ""),
                    "artist": song.get("artist", ""),
                    "genre": "Recommended",
                    "bpm": 0,
                    "mood": "Recommended"
                })
                print("저장 완료:", song.get("title"))
            except Exception as e:
                print("songs.csv 저장 실패:", e)

        # ---------------------------------------------------
        # 6) 응답 반환
        # ---------------------------------------------------
        print("\nAPI 최종 응답 반환")

        return Response({
            "message": "Apple 테스트 추천 실행 완료",
            "input_ids": track_ids,
            "mood_keywords": mood_keywords,
            "recommended": results
        })



# ============================================================
# PingView (기본 연결 확인용)
# ============================================================
class PingView(APIView):
    def get(self, request):
        return Response({
            "message": "pong",
            "mode": ACTIVAE_MODE  # 현재 모드 알려주기
        })
# ========================================================= #















# ========================================================= #
# FeatureExtractView: 미사용
'''
class FeatureExtractView(APIView): #for test
    """ 기본 Mega Extractor """
    def get(self, request):
        token = request.GET.get("token")
        track_id = request.GET.get("track_id")

        metadata = get_track_metadata(track_id, token)
        features = extract_features(metadata)

        return Response({
            "success": True,
            "mode": "basic",
            "features": features
        })
'''

# RecommendView: 미사용
'''
class RecommendView(APIView): #for test
    """
    MultiTrackFeatureExtractView 결과(JSON)를 입력받아
    Annoy 기반 추천 10곡 반환
    """

    def post(self, request):
        tracks = request.data.get("tracks", [])

        if len(tracks) == 0:
            return Response({"error": "tracks missing"}, status=400)

        user_vectors = []

        try:
            for track in tracks:
                nf = track["features"]["numeric_vector"]
                gf = track["features"]["genre_vector"]
                vector = nf + gf
                user_vectors.append(vector)

        except Exception as e:
            return Response({"error": str(e)}, status=400)

        # Annoy 추천 실행
        rec = AnnoyRecommender()
        recommended_ids = rec.recommend_top_k(user_vectors, k=10)

        return Response({
            "success": True,
            "mode": "embedding",
            "features": features
            "recommended_track_ids": recommended_ids,
            "count": len(recommended_ids)
        })
'''

# RecommendView: 미사용 (검색 결과 필요 시 사용)
'''
class SpotifySearchView(APIView): # Spotify 곡 검색 결과를 Django REST API로 전달하는 엔드포인트
    def get(self, request):
        access_token = request.GET.get("token")
        query = request.GET.get("q", "IU")
        if not access_token:
            return Response({"error": "Missing access token"}, status=400)

        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=5"
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return Response(r.json())
'''
