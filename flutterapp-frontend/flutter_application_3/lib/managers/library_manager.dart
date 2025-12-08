import '../models/music_track.dart';

// 1. 플레이리스트 데이터 모델
class MyPlaylist {
  final String name;
  final List<MusicTrack> tracks;
  final DateTime createdAt;

  MyPlaylist({
    required this.name,
    required this.tracks,
    required this.createdAt,
  });
}

// 2. 라이브러리 매니저 (데이터 저장소)
class LibraryManager {
  // 앱 전체에서 공유되는 저장소 (Singleton 패턴처럼 사용)
  static final List<MyPlaylist> savedPlaylists = [];

  // 플레이리스트 추가 함수
  static void addPlaylist(String name, List<MusicTrack> tracks) {
    savedPlaylists.add(MyPlaylist(
      name: name,
      tracks: tracks,
      createdAt: DateTime.now(),
    ));
  }
}