import 'package:flutter/material.dart';

class PlaylistResultPage extends StatelessWidget {
  const PlaylistResultPage({super.key});

  @override
  Widget build(BuildContext context) {
    // 추후 Django → Spotify API 연동 시 실제 링크로 교체
    const playlistUrl = "https://open.spotify.com/playlist/example123";

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black,
        title: const Text(
          'Your Playlist Ready! 🎵',
          style: TextStyle(color: Colors.white),
        ),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const Text(
              '당신의 음악 취향에 맞는 플레이리스트가 완성되었습니다!',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white, fontSize: 18),
            ),
            const SizedBox(height: 40),

            const Icon(Icons.music_note, color: Colors.greenAccent, size: 80),
            const SizedBox(height: 20),

            const Text(
              '🎶 Groovia Vibe Mix',
              style: TextStyle(
                color: Colors.greenAccent,
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 40),

            // 링크 버튼
            ElevatedButton.icon(
              onPressed: () {
                // TODO: launch URL
              },
              icon: const Icon(Icons.open_in_new),
              label: const Text("Open in Spotify"),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.greenAccent[400],
                foregroundColor: Colors.black,
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 14,
                ),
              ),
            ),

            const Spacer(),

            ElevatedButton(
              onPressed: () =>
                  Navigator.popUntil(context, (route) => route.isFirst),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.grey[800],
                padding: const EdgeInsets.symmetric(
                  horizontal: 20,
                  vertical: 14,
                ),
              ),
              child: const Text(
                "Back to Home",
                style: TextStyle(color: Colors.white),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
