import csv
import os
import re

CSV_FILE = "songs.csv"

# 문자열 정규화 (공백, 특수문자 제거 등)
def normalize_text(text):
    text = text.strip()
    # 해시태그(#), 괄호, 하이픈(-), 언더바(_)은 일부 유지
    text = re.sub(r'[^\w\s#()\-]', '', text)  
    # 여러 공백 하나로 합치기
    text = re.sub(r'\s+', ' ', text)
    # 맨 앞 글자 대문자 (영문만)
    return text.strip().title()

# CSV 저장
def save_song_to_csv(song_data):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "artist", "genre", "bpm", "mood"])

        # 파일이 새로 생성됐다면 헤더 추가
        if not file_exists:
            writer.writeheader()

        # 정규화된 데이터 저장
        normalized = {
            "title": normalize_text(song_data["title"]),
            "artist": normalize_text(song_data["artist"]),
            "genre": normalize_text(song_data["genre"]),
            "bpm": str(song_data["bpm"]).strip(),
            "mood": normalize_text(song_data["mood"])
        }
        writer.writerow(normalized)

# CSV 불러오기 + 파싱
def load_songs_from_csv():
    songs = []
    if not os.path.exists(CSV_FILE):
        return songs

    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # 파싱: 숫자형 변환, 불필요 공백 제거
            try:
                row["bpm"] = int(row["bpm"])
            except ValueError:
                row["bpm"] = None
            row["title"] = normalize_text(row["title"])
            row["artist"] = normalize_text(row["artist"])
            row["genre"] = normalize_text(row["genre"])
            row["mood"] = normalize_text(row["mood"])
            songs.append(row)
    return songs

if __name__ == "__main__":
    save_song_to_csv({
        'title': 'Shape of You',
        'artist': 'Ed Sheeran',
        'genre': 'Pop',
        'bpm': '96',
        'mood': 'Happy'
    })

    songs = load_songs_from_csv()
    print(songs)