class MusicTrack {
  final int trackId;
  final String title;
  final String artist;
  final String albumImage;
  final String appleMusicUrl;

  MusicTrack({
    required this.trackId,
    required this.title,
    required this.artist,
    required this.albumImage,
    required this.appleMusicUrl,

  });

  // JSON 데이터를 Dart 객체로 변환하는 공장
  factory MusicTrack.fromJson(Map<String, dynamic> json) {
    // 이미지 화질 개선 (100x100 -> 600x600)
    String rawImage = json['album_image'] ?? '';
    String highResImage = rawImage.replaceAll('100x100bb', '600x600bb');

    return MusicTrack(
      trackId: json['track_id'] ?? 0,
      title: json['title'] ?? 'Unknown Title',
      artist: json['artist'] ?? 'Unknown Artist',
      albumImage: highResImage, // 고화질 이미지 사용
      appleMusicUrl: json['apple_music_url'] ?? '',
    );
  }
}