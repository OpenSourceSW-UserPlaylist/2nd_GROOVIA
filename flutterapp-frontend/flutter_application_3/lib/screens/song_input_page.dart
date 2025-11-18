import 'package:flutter/material.dart';
import 'category_result_page.dart';

class SongInputPage extends StatefulWidget {
  final String userName;

  const SongInputPage({super.key, required this.userName});

  @override
  State<SongInputPage> createState() => _SongInputPageState();
}

class _SongInputPageState extends State<SongInputPage> {
  final TextEditingController _songController = TextEditingController();
  final List<String> _songs = [];

  void _addSong() {
    String song = _songController.text.trim();
    if (song.isEmpty) return;

    setState(() {
      _songs.add(song);
      _songController.clear();
    });
  }

  void _removeSong(int index) {
    setState(() {
      _songs.removeAt(index);
    });
  }

  void _analyzeSongs() {
    if (_songs.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('먼저 노래를 한 곡 이상 입력해주세요!')));
      return;
    }

    // 다음 페이지로 이동
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) =>
            CategoryResultPage(songs: _songs, userName: widget.userName),
      ),
    );

    // 이후 Django API 연동으로 대체 예정
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('분석을 시작합니다...')));

    // TODO: 다음 화면(로딩 → 카테고리 결과)으로 이동
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black,
        title: Text(
          'Hi, ${widget.userName} 👋',
          style: const TextStyle(color: Colors.white),
        ),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Enter songs or artists',
              style: TextStyle(color: Colors.white, fontSize: 18),
            ),
            const SizedBox(height: 12),

            // 입력창
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _songController,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'e.g. Perfect - Ed Sheeran',
                      hintStyle: const TextStyle(color: Colors.grey),
                      filled: true,
                      fillColor: const Color(0xFF1E1E1E),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        vertical: 14,
                        horizontal: 16,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                ElevatedButton(
                  onPressed: _addSong,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.greenAccent[400],
                    foregroundColor: Colors.black,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 14,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  child: const Text('Add'),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // 입력된 노래 리스트
            Expanded(
              child: _songs.isEmpty
                  ? const Center(
                      child: Text(
                        'No songs added yet 🎵',
                        style: TextStyle(color: Colors.grey),
                      ),
                    )
                  : ListView.builder(
                      itemCount: _songs.length,
                      itemBuilder: (context, index) {
                        return Container(
                          margin: const EdgeInsets.only(bottom: 8),
                          decoration: BoxDecoration(
                            color: const Color(0xFF1E1E1E),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: ListTile(
                            title: Text(
                              _songs[index],
                              style: const TextStyle(color: Colors.white),
                            ),
                            trailing: IconButton(
                              icon: const Icon(Icons.delete, color: Colors.red),
                              onPressed: () => _removeSong(index),
                            ),
                          ),
                        );
                      },
                    ),
            ),

            // 분석 버튼
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _analyzeSongs,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.greenAccent[400],
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  'Analyze 🎧',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
