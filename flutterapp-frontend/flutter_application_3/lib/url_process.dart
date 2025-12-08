import 'dart:convert'; // JSON 처리를 위해 필수
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class UrlProcessorScreen extends StatefulWidget {
  @override
  _UrlProcessorScreenState createState() => _UrlProcessorScreenState();
}

class _UrlProcessorScreenState extends State<UrlProcessorScreen> {
  String _resultText = "결과가 여기에 표시됩니다.";

  // Django로 데이터 전송하는 함수
  Future<void> sendUrlsToBackend() async {
    // **중요**: 로컬 테스트 시 IP 주소 설정
    // Android 에뮬레이터: 'http://10.0.2.2:8000/api/process-urls/'
    // iOS 시뮬레이터: 'http://127.0.0.1:8000/api/process-urls/'
    // 실제 기기: PC의 내부 IP (예: 192.168.0.x:8000...)
    final String apiUrl = 'https://ungifted-witchingly-sol.ngrok-free.dev/api/process-urls/';

    try {
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "urls": [
            "https://google.com",
            "https://naver.com"
          ] // 사용자가 입력한 URL 리스트를 여기에 넣으세요
        }),
      );

      if (response.statusCode == 200) {
        // 성공 시 데이터 파싱
        final data = jsonDecode(utf8.decode(response.bodyBytes)); // 한글 깨짐 방지
        setState(() {
          _resultText = data['results'].toString();
        });
      } else {
        setState(() {
          _resultText = "오류 발생: ${response.statusCode}";
        });
      }
    } catch (e) {
      setState(() {
        _resultText = "네트워크 에러: $e";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Django-Flutter 연동")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: sendUrlsToBackend,
              child: Text("URL 전송 및 결과 받기"),
            ),
            SizedBox(height: 20),
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(_resultText),
            ),
          ],
        ),
      ),
    );
  }
}