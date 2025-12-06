# views.py

from django.http import JsonResponse
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response

# csv_manager 임포트
from .csv_manager import save_song_to_csv, load_songs_from_csv


def save_recommendations_to_csv(recommendations_list):
    """
    팀원으로부터 받은 10곡의 추천 결과를 CSV에 저장합니다.
    (이 함수는 CSV_FILE에 종속적이며, 기존 save_song_to_csv를 활용합니다.)
    """
    for song in recommendations_list:
        # save_song_to_csv 함수는 title, artist, album_art 등을 저장할 수 있도록
        # csv_manager.py에서 이미 수정되었다고 가정합니다.
        save_song_to_csv({
            "title": song.get("title", ""),
            "artist": song.get("artist", ""),
            "album_art": song.get("album_art", ""), # 핵심 필드
            "genre": "Recommended", # 임시값
            "bpm": 0, # 임시값
            "mood": "Recommended" # 임시값
        })


@api_view(['POST'])
def process_and_send_recommendations(request):
    """
    1. 추천팀의 결과 (JSON)를 받아 CSV에 저장합니다.
    2. 저장된 데이터를 Django에서 읽어와 Flutter에 JSON으로 반환합니다.
    """
    try:
        # 1. 추천팀의 결과 받기 (POST Body에 포함된 10곡 리스트)
        # 추천팀의 리턴값 구조: [ {"title": "...", "artist": "...", "album_art": "..."}, ... ]
        recommended_data = request.data.get("recommendations", []) 

        if not recommended_data or len(recommended_data) != 10:
            return Response({'status': 'error', 'message': '10곡의 추천 데이터가 필요합니다.'}, status=400)
        
        # 2. 데이터를 CSV에 저장
        save_recommendations_to_csv(recommended_data)
        
        # 3. CSV에 저장된 데이터를 다시 Django로 로드 (확인 및 전송)
        # 실제로는 방금 저장한 10곡만 로드하는 것이 효율적이지만, 
        # load_songs_from_csv가 전체를 로드한다고 가정하고 필터링합니다.
        # 편의상, 방금 받은 recommended_data를 바로 사용합니다.
        
        # --- 최종 Flutter 반환 형식으로 정리 ---
        final_data = []
        for song in recommended_data:
            # title, artist, album_art 필드만 추출하여 전달
            final_data.append({
                "title": song.get("title", "Unknown Title"),
                "artist": song.get("artist", "Unknown Artist"),
                "album_art": song.get("album_art", "") # URL 전송
            })

    except Exception as e:
        print(f"데이터 처리 중 오류 발생: {e}")
        return Response({'status': 'error', 'message': f'데이터 처리 중 오류: {str(e)}'}, status=500)
    
    # 4. JSON 응답으로 반환
    return JsonResponse({
        'status': 'success',
        'count': len(final_data),
        'recommendations': final_data # Flutter가 이 리스트를 받아 UI를 구성
    })