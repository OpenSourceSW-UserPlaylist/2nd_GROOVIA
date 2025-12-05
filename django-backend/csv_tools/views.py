import csv
import re
import requests
from django.http import JsonResponse
from .csv_manager import (
    save_song_to_csv, load_songs_from_csv,
    save_features_to_csv, load_features_from_csv
)

# Spotify 곡 데이터 정리 (정규화 + 파싱)
def parse_spotify_data(track_json):
    try:
        title = re.sub(r'\s+', ' ', track_json.get('name', 'Unknown')).strip()
        artist = ', '.join([a['name'] for a in track_json.get('artists', [])])
        genre = track_json.get('genre', 'Unknown')
        bpm = track_json.get('tempo', 'Unknown')  # tempo는 별도 API로도 가능
        url = track_json.get('external_urls', {}).get('spotify', '')
        album = track_json.get('album', {}).get('name', '')
        album_art = track_json.get('album', {}).get('images', [{}])[0].get('url', '')

        # 특수문자 정규화
        def normalize(text):
            text = text.strip()
            text = re.sub(r'[^\w\s.,!?#-]', '', text)
            text = re.sub(r'\s+', ' ', text)
            return text.title()

        return {
            'title': normalize(title),
            'artist': normalize(artist),
            'genre': normalize(genre),
            'bpm': bpm,
            'url': url,
            'album': normalize(album),
            'album_art': album_art
        }

    except Exception as e:
        print("Spotify 데이터 파싱 중 오류:", e)
        return None


# Spotify 단일 곡 정보 가져오기
def get_spotify_track(track_id, token):
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json()


# 여러 곡 입력(최대 3곡) 처리
def get_multiple_tracks(request):
    track_ids = request.GET.get('track_ids', '')
    token = request.GET.get('token')

    if not track_ids or not token:
        return JsonResponse({'status': 'error', 'message': 'track_ids 또는 token이 없습니다.'})

    track_ids = [tid.strip() for tid in track_ids.split(',') if tid.strip()]
    if len(track_ids) > 3:
        return JsonResponse({'status': 'error', 'message': '최대 3곡까지만 입력 가능합니다.'})

    all_tracks = []
    for tid in track_ids:
        track_json = get_spotify_track(tid, token)
        parsed = parse_spotify_data(track_json)
        if parsed:
            all_tracks.append(parsed)

    if not all_tracks:
        return JsonResponse({'status': 'error', 'message': 'Spotify 데이터 파싱 실패'})

    # CSV 저장 (곡별로 추가)
    for t in all_tracks:
        save_song_to_csv({
            "title": t["title"],
            "artist": t["artist"],
            "genre": t["genre"],
            "bpm": t["bpm"],
            "mood": "Unknown"
        })

    return JsonResponse({
        'status': 'success',
        'count': len(all_tracks),
        'data': all_tracks
    })


# CSV 직접 저장 (로컬 테스트용)
#def save_song(request):
#    sample = {
#        'title': 'Shape of You',
#        'artist': 'Ed Sheeran',
#        'genre': 'Pop',
#        'bpm': '96',
#        'mood': 'Happy'
#    }
#    save_song_to_csv(sample)
#    return JsonResponse({'status': 'success', 'message': '샘플 곡 저장 완료'})


# CSV 불러오기 (전체 곡 목록 보기)
def get_songs(request):
    data = load_songs_from_csv()
    return JsonResponse({'status': 'success', 'count': len(data), 'songs': data})