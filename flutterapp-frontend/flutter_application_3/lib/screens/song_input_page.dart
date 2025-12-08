import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/music_track.dart'; // 📌 MusicTrack 모델 경로 확인
import 'playlist_result_page.dart'; // 📌 결과 페이지 import 필수

class SongInputPage extends StatefulWidget {
  final String userName;
  const SongInputPage({super.key, required this.userName});

  @override
  State<SongInputPage> createState() => _SongInputPageState();
}

class _SongInputPageState extends State<SongInputPage> {
  // 📌 처음엔 입력창 1개로 시작
  final List<TextEditingController> _controllers = [
    TextEditingController(),
  ];

  bool _isLoading = false;

  // ➕ 입력창 추가 함수
  void _addInput() {
    if (_controllers.length >= 5) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('최대 5곡까지만 입력 가능합니다.')),
      );
      return;
    }
    setState(() {
      _controllers.add(TextEditingController());
    });
  }

  // ➖ 입력창 삭제 함수
  void _removeInput(int index) {
    setState(() {
      _controllers[index].dispose();
      _controllers.removeAt(index);
    });
  }

  // 🔗 Django 서버에 POST 요청을 보내고 결과 페이지로 이동하는 함수
  Future<void> _searchAndNavigate() async {
    // 1. 비어있지 않은 입력값만 필터링하여 POST Body에 담을 리스트 생성
    List<String> validSongs = _controllers
        .map((c) => c.text.trim())
        .where((text) => text.isNotEmpty)
        .toList();

    if (validSongs.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('최소 한 곡은 입력해주세요!')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      FocusScope.of(context).unfocus();
    });

    // ⚠️ [중요] POST 요청은 Body에 데이터를 담아 보내므로, URL은 깔끔하게 유지합니다.
    final Uri uri = Uri.https(
      'ungifted-witchingly-sol.ngrok-free.dev', // 도메인
      '/api/itunes/itunes-process-urls/',             // 경로
    );

    try {
      // 2. http.post를 사용하여 JSON 데이터를 Body에 담아 전송
      final response = await http.post(
        uri,
        headers: {
          "Content-Type": "application/json",
        },
        body: jsonEncode({
          'urls': validSongs, // 리스트를 JSON 배열로 인코딩하여 전송
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        
        if (data['recommended'] != null) {
          final List<dynamic> jsonList = data['recommended'];
          List<MusicTrack> resultTracks = jsonList.map((json) => MusicTrack.fromJson(json)).toList();

          // 3. 태그 키워드 파싱 (Django에서 보낸 이중 리스트 구조 처리)
          List<String> resultTags = [];
          if (data['mood_keywords'] != null && (data['mood_keywords'] as List).isNotEmpty) {
             final dynamic keywords = data['mood_keywords'][0]; 
             if (keywords is List) {
               resultTags = keywords.map((e) => e.toString()).toList();
             }
          }

          if (resultTags.isEmpty) resultTags = ['#Groovia', '#Mix'];

          if (!mounted) return;

          // 4. 데이터 전달 후 결과 페이지로 이동
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => PlaylistResultPage(
                userName: widget.userName,
                tracks: resultTracks,
                tags: resultTags,
              ),
            ),
          );
        }
      } else {
        print('Server Error: ${response.statusCode}');
        if (mounted) {
           ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('서버 오류: ${response.statusCode} (데이터 처리 실패)')),
          );
        }
      }
    } catch (e) {
      print('Network Error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('서버와 연결할 수 없습니다.')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  void dispose() {
    for (var c in _controllers) c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Create Your Vibe"),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Icon(Icons.queue_music, size: 80, color: Colors.white),
              const SizedBox(height: 20),
              const Text(
                "좋아하는 노래를 추가해주세요!",
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
              ),
              const SizedBox(height: 30),

              // 📌 동적 입력창 리스트를 표시하는 ListView
              ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _controllers.length,
                itemBuilder: (context, index) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 15.0),
                    child: Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _controllers[index],
                            style: const TextStyle(color: Colors.white),
                            decoration: InputDecoration(
                              labelText: 'Song ${index + 1}',
                              labelStyle: const TextStyle(color: Color(0xFF1DB954)),
                              hintText: '가수, 노래제목',
                              hintStyle: TextStyle(color: Colors.grey[500]),
                              filled: true,
                              fillColor: const Color(0xFF282828),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(10),
                                borderSide: BorderSide.none,
                              ),
                              contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
                            ),
                          ),
                        ),
                        // ➖ 삭제 버튼 (1개일 땐 삭제 불가)
                        if (_controllers.length > 1)
                          IconButton(
                            icon: const Icon(Icons.remove_circle_outline, color: Colors.redAccent),
                            onPressed: () => _removeInput(index),
                          ),
                      ],
                    ),
                  );
                },
              ),

              // ➕ 추가 버튼
              TextButton.icon(
                onPressed: _addInput,
                icon: const Icon(Icons.add, color: Color(0xFF1DB954)),
                label: const Text("노래 더 추가하기", style: TextStyle(color: Color(0xFF1DB954))),
              ),

              const SizedBox(height: 20),

              // 🔘 믹스 생성 버튼
              SizedBox(
                height: 55,
                child: _isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : ElevatedButton(
                        onPressed: _searchAndNavigate,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Theme.of(context).primaryColor,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(30),
                          ),
                        ),
                        child: const Text(
                          "믹스 생성하기",
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.black),
                        ),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}