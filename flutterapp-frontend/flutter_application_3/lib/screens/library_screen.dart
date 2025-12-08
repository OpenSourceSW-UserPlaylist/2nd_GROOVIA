import 'package:flutter/material.dart';
import '../managers/library_manager.dart';
import 'playlist_result_page.dart'; // 상세보기를 위해 재사용

class LibraryScreen extends StatefulWidget {
  const LibraryScreen({super.key});

  @override
  State<LibraryScreen> createState() => _LibraryScreenState();
}

class _LibraryScreenState extends State<LibraryScreen> {
  @override
  Widget build(BuildContext context) {
    final playlists = LibraryManager.savedPlaylists; // 저장된 데이터 가져오기

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text("Your Library", style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.black,
      ),
      body: playlists.isEmpty
          ? Center(
              child: Text(
                "저장된 플레이리스트가 없습니다.",
                style: TextStyle(color: Colors.grey[600]),
              ),
            )
          : ListView.builder(
              itemCount: playlists.length,
              itemBuilder: (context, index) {
                final playlist = playlists[index];
                return ListTile(
                  leading: Container(
                    width: 50, height: 50,
                    color: Colors.grey[800],
                    child: const Icon(Icons.music_note, color: Colors.white),
                  ),
                  title: Text(
                    playlist.name,
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                  subtitle: Text(
                    "${playlist.tracks.length} songs • ${playlist.createdAt.toString().split(' ')[0]}",
                    style: const TextStyle(color: Colors.grey),
                  ),
                  onTap: () {
                    // 클릭하면 상세 페이지(기존 결과 페이지 재활용)로 이동
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => PlaylistResultPage(
                          userName: "User", // 저장된 거라 유저 이름은 고정하거나 저장 필요
                          tracks: playlist.tracks,
                          tags: const ['#Saved', '#MyLibrary'], // 저장된 태그
                        ),
                      ),
                    );
                  },
                );
              },
            ),
    );
  }
}