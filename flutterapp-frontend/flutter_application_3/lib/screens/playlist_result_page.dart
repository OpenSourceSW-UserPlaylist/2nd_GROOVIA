import 'package:flutter/material.dart';
import '../models/music_track.dart'; // 📌 모델 경로 확인
import '../managers/library_manager.dart'; // 📌 라이브러리 매니저 import 필수

class PlaylistResultPage extends StatelessWidget {
  final String userName;
  final List<MusicTrack> tracks;
  final List<String> tags; // 태그 리스트

  const PlaylistResultPage({
    super.key,
    required this.userName,
    required this.tracks,
    required this.tags,
  });

  // 💾 플레이리스트 저장 팝업 함수
  void _showSaveDialog(BuildContext context) {
    final TextEditingController nameController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: const Color(0xFF282828), // 다크 테마 배경
          title: const Text("Save Playlist", style: TextStyle(color: Colors.white)),
          content: TextField(
            controller: nameController,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              hintText: "플레이리스트 이름을 입력하세요",
              hintStyle: TextStyle(color: Colors.grey),
              enabledBorder: UnderlineInputBorder(borderSide: BorderSide(color: Color(0xFF1DB954))),
              focusedBorder: UnderlineInputBorder(borderSide: BorderSide(color: Color(0xFF1DB954), width: 2)),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("취소", style: TextStyle(color: Colors.grey)),
            ),
            TextButton(
              onPressed: () {
                if (nameController.text.isNotEmpty) {
                  // 📌 1. 라이브러리 매니저에 저장 요청
                  LibraryManager.addPlaylist(nameController.text, tracks);
                  
                  Navigator.pop(context); // 팝업 닫기
                  
                  // 2. 저장 완료 알림 (SnackBar)
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text("'${nameController.text}' 라이브러리에 저장됨! ✅"),
                      backgroundColor: const Color(0xFF1DB954),
                      duration: const Duration(seconds: 2),
                    ),
                  );
                }
              },
              child: const Text("저장", style: TextStyle(color: Color(0xFF1DB954), fontWeight: FontWeight.bold)),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black, // 배경 검정
      appBar: AppBar(
        backgroundColor: Colors.black,
        elevation: 0,
        title: const Text(
          'Your Playlist Ready! 🎵',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        // 💾 상단 우측 저장 버튼
        actions: [
          IconButton(
            icon: const Icon(Icons.save_alt, color: Colors.white),
            onPressed: () => _showSaveDialog(context),
            tooltip: '라이브러리에 저장',
          ),
        ],
      ),
      body: Column(
        children: [
          // 📝 1. 상단 안내 문구
          Padding(
            padding: const EdgeInsets.fromLTRB(24, 20, 24, 10),
            child: Text(
              '$userName님의 취향을 저격할\nGroovia 믹스가 완성되었습니다!',
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 18,
                height: 1.5,
              ),
            ),
          ),

          // 🏷️ 2. 태그 키워드 (Wrap 위젯)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
            child: Wrap(
              alignment: WrapAlignment.center,
              spacing: 8.0,
              runSpacing: 8.0,
              children: tags.map((tag) {
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1DB954).withOpacity(0.15),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFF1DB954), width: 1),
                  ),
                  child: Text(
                    tag,
                    style: const TextStyle(
                      color: Color(0xFF1DB954),
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                );
              }).toList(),
            ),
          ),

          const SizedBox(height: 10),

          // 🎵 3. 결과 리스트
          Expanded(
            child: tracks.isEmpty
                ? const Center(
                    child: Text(
                      "추천 결과가 없습니다.",
                      style: TextStyle(color: Colors.grey),
                    ),
                  )
                : ListView.builder(
                    itemCount: tracks.length,
                    itemBuilder: (context, index) {
                      final track = tracks[index];

                      return Container(
                        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        decoration: BoxDecoration(
                          color: const Color(0xFF1E1E1E), // 카드 배경색
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: ListTile(
                          contentPadding: const EdgeInsets.all(12),
                          // 앨범 아트
                          leading: ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: Image.network(
                              track.albumImage,
                              width: 60,
                              height: 60,
                              fit: BoxFit.cover,
                              errorBuilder: (context, error, stackTrace) =>
                                  Container(width: 60, height: 60, color: Colors.grey[800]),
                            ),
                          ),
                          // 제목
                          title: Text(
                            track.title,
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          // 가수
                          subtitle: Padding(
                            padding: const EdgeInsets.only(top: 4.0),
                            child: Text(
                              track.artist,
                              style: const TextStyle(color: Colors.grey),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          // 재생 아이콘 (장식용)
                          trailing: IconButton(
                            icon: const Icon(
                              Icons.play_circle_fill,
                              color: Color(0xFF1DB954),
                              size: 40,
                            ),
                            onPressed: () {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text("'${track.title}' 재생 중...")),
                                );
                            },
                          ),
                        ),
                      );
                    },
                  ),
          ),

          // 🏠 4. 하단 홈으로 가기 버튼
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton(
                onPressed: () => Navigator.popUntil(context, (route) => route.isFirst),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.grey[800],
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(30)),
                ),
                child: const Text(
                  "Back to Home",
                  style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ),
          
          // 🍎 출처 표기
          const Padding(
            padding: EdgeInsets.only(bottom: 20),
            child: Text(
              "Data sourced from Apple Music",
              style: TextStyle(color: Colors.grey, fontSize: 10),
            ),
          ),
        ],
      ),
    );
  }
}