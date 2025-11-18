import 'package:flutter/material.dart';
import 'package:flutter_application_3/services/api_service.dart';

class TestApiPage extends StatefulWidget {
  const TestApiPage({super.key});

  @override
  State<TestApiPage> createState() => _TestApiPageState();
}

class _TestApiPageState extends State<TestApiPage> {
  String _pingResult = "아직 요청 안 함";
  List<dynamic> _songs = [];

  Future<void> _callPing() async {
    try {
      String result = await ApiService.ping();
      setState(() {
        _pingResult = "서버 응답: $result";
      });
    } catch (e, st) {
      // 🔥 디버그용 출력
      print("Ping error: $e");
      print("Stack: $st");
      setState(() {
        _pingResult = "에러 발생(PING): $e";
      });
    }
  }

  Future<void> _loadSongs() async {
    try {
      List<dynamic> result = await ApiService.getSongs();
      setState(() {
        _songs = result;
        _pingResult = "노래 ${result.length}개 불러옴";
      });
    } catch (e, st) {
      print("Songs error: $e");
      print("Stack: $st");
      setState(() {
        _pingResult = "에러 발생(SONGS): $e";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("API Test Page")),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 🔹 Ping API 호출 버튼
            ElevatedButton(
              onPressed: _callPing,
              child: const Text("Ping API 호출"),
            ),
            const SizedBox(height: 10),
            Text(
              _pingResult,
              style: const TextStyle(color: Colors.white, fontSize: 16),
            ),

            const SizedBox(height: 30),

            // 🔹 CSV Songs 조회 버튼
            ElevatedButton(
              onPressed: _loadSongs,
              child: const Text("CSV Songs 불러오기"),
            ),

            const SizedBox(height: 12),
            Expanded(
              child: ListView.builder(
                itemCount: _songs.length,
                itemBuilder: (context, index) {
                  final s = _songs[index];
                  return ListTile(
                    title: Text(
                      s["title"] ?? "No title",
                      style: const TextStyle(color: Colors.white),
                    ),
                    subtitle: Text(
                      s["artist"] ?? "No artist",
                      style: const TextStyle(color: Colors.grey),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
      backgroundColor: Colors.black,
    );
  }
}
