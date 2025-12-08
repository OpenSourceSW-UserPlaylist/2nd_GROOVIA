import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

// ▼ 클래스 이름이 'DjangoTestScreen'이어야만 main.dart가 알아봅니다!
class DjangoTestScreen extends StatefulWidget {
  const DjangoTestScreen({super.key});

  @override
  State<DjangoTestScreen> createState() => _DjangoTestScreenState();
}

class _DjangoTestScreenState extends State<DjangoTestScreen> {
  String _resultText = "버튼을 눌러 통신 시작";

  Future<void> sendUrlsToBackend() async {
    final String apiUrl = 'https://ungifted-witchingly-sol.ngrok-free.dev/api/spotify/process-urls/';

    try {
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "urls": ["https://open.spotify.com/track/7dOeiXeTSfA1ixaYmQcWu7?si=dc9db57c69704cd3", 
                   "https://open.spotify.com/track/5ZAUiOlYURVJEJ5ktV03v5?si=1398546013ca4e5d",
                   "https://open.spotify.com/track/1iQzHvQDBXWFO6wcJE7K0E?si=e486e4aaa71440e8"
                  ]
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        setState(() {
          _resultText = "성공!\n${data['results'][0]['message']}";
        });
      } else {
        setState(() {
          _resultText = "오류: ${response.statusCode}";
        });
      }
    } catch (e) {
      setState(() {
        _resultText = "연결 실패: $e";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Django 연동 테스트")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(_resultText, textAlign: TextAlign.center),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: sendUrlsToBackend,
              child: Text("서버 통신"),
            ),
          ],
        ),
      ),
    );
  }
}