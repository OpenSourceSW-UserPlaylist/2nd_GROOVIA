import csv
import os
import re

# ----------------------------
#   SONGS CSV 기능
# ----------------------------

CSV_FILE = "songs.csv"
FEATURES_FILE = "features.csv"

# 문자열 정규화 (공백, 특수문자 제거 등)
def normalize_text(text):
    text = text.strip()
    # 해시태그(#), 괄호, 하이픈(-), 언더바(_)는 일부 유지
    text = re.sub(r'[^\w\s#()\-]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().title()

# SONG CSV 저장
def save_song_to_csv(song_data):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "artist", "genre", "bpm", "mood"])

        if not file_exists:
            writer.writeheader()

        normalized = {
            "title": normalize_text(song_data["title"]),
            "artist": normalize_text(song_data["artist"]),
            "genre": normalize_text(song_data["genre"]),
            "bpm": str(song_data["bpm"]).strip(),
            "mood": normalize_text(song_data["mood"])
        }
        writer.writerow(normalized)

# SONG CSV 불러오기
def load_songs_from_csv():
    songs = []
    if not os.path.exists(CSV_FILE):
        return songs

    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
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


# ----------------------------
#   FEATURES CSV 기능
# ----------------------------

# 특징값 저장
def save_features_to_csv(feature_data):
    file_exists = os.path.isfile(FEATURES_FILE)

    with open(FEATURES_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=[
            "title", "artist", "genre", "bpm",
            "danceability", "energy", "valence", "acousticness",
            "instrumentalness", "liveness", "speechiness"
        ])

        if not file_exists:
            writer.writeheader()

        writer.writerow(feature_data)

# 특징값 불러오기
def load_features_from_csv():
    features = []
    if not os.path.exists(FEATURES_FILE):
        return features

    with open(FEATURES_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            numeric_fields = [
                "bpm", "danceability", "energy", "valence",
                "acousticness", "instrumentalness", "liveness", "speechiness"
            ]

            for f in numeric_fields:
                try:
                    row[f] = float(row[f])
                except:
                    row[f] = None

            features.append(row)

    return features