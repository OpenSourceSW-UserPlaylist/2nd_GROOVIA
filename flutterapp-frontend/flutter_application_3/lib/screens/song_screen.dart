import 'package:flutter/material.dart';

class SongScreen extends StatelessWidget {
  final String songTitle;
  final String artistName;
  // TODO: 실제 앱에서는 앨범 아트 URL과 가사 데이터가 필요합니다.
  final String imageUrl; 
  
  const SongScreen({
    super.key,
    required this.songTitle,
    required this.artistName,
    required this.imageUrl,
  });

  @override
  Widget build(BuildContext context) {
    // Groovia 메인 녹색
    final primaryColor = Theme.of(context).primaryColor; 

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_downward, color: Colors.white),
          onPressed: () => Navigator.pop(context), // 화면 닫기
        ),
        title: const Text(
          'Playing from Playlist',
          style: TextStyle(fontSize: 14, color: Colors.grey),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.more_vert, color: Colors.white),
            onPressed: () {
              // TODO: 'Menu' 모달 표시 로직 구현
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0),
          child: Column(
            children: <Widget>[
              const SizedBox(height: 30),
            
              // 🖼️ 앨범 아트
              _buildAlbumArt(context),
            
              const SizedBox(height: 50),

              // 🎵 노래 정보
              _buildSongInfo(primaryColor),

              const SizedBox(height: 40),

              // 📏 재생 바 및 시간 표시
              _buildPlaybackBar(primaryColor),

              const SizedBox(height: 30),

              // ⏯️ 컨트롤 버튼
              _buildControls(primaryColor),

              const SizedBox(height: 50),

              // 🎤 가사 (현재 재생 중인 가사 강조)
              _buildLyricsSection(primaryColor),
              
              const SizedBox(height: 30),
            ],
          ),
        ),
      ),
    );
  }

  // 앨범 아트 위젯
  Widget _buildAlbumArt(BuildContext context) {
    return AspectRatio(
      aspectRatio: 1 / 1,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(15.0),
        child: Image.asset(
          imageUrl,
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) {
            return Container(
              color: Colors.grey[800],
              child: const Icon(Icons.music_note, size: 100, color: Colors.white),
            );
          },
        ),
      ),
    );
  }

  // 노래 정보 위젯
  Widget _buildSongInfo(Color primaryColor) {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                songTitle,
                style: const TextStyle(
                  fontSize: 26,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 5),
              Text(
                artistName,
                style: TextStyle(
                  fontSize: 18,
                  color: Colors.grey[400],
                ),
              ),
            ],
          ),
        ),
        // 좋아요 버튼
        IconButton(
          icon: const Icon(Icons.favorite_border, color: Colors.white, size: 28),
          onPressed: () { /* TODO: 좋아요 로직 */ },
        ),
      ],
    );
  }

  // 재생 바 위젯
  Widget _buildPlaybackBar(Color primaryColor) {
    // TODO: 실제 재생 상태와 연동해야 함
    const double currentPosition = 0.6; // 60% 진행 가정
    return Column(
      children: [
        LinearProgressIndicator(
          value: currentPosition,
          backgroundColor: Colors.grey.withOpacity(0.3),
          valueColor: AlwaysStoppedAnimation<Color>(primaryColor),
        ),
        const SizedBox(height: 5),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '1:23', // 현재 시간 (더미)
              style: TextStyle(fontSize: 12, color: Colors.grey[400]),
            ),
            Text(
              '-1:17', // 남은 시간 (더미)
              style: TextStyle(fontSize: 12, color: Colors.grey[400]),
            ),
          ],
        ),
      ],
    );
  }

  // 컨트롤 버튼 위젯
  Widget _buildControls(Color primaryColor) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        // 셔플
        IconButton(
          icon: Icon(Icons.shuffle, color: Colors.grey[400], size: 28),
          onPressed: () { /* TODO: 셔플 로직 */ },
        ),
        // 이전 곡
        IconButton(
          icon: const Icon(Icons.skip_previous, color: Colors.white, size: 48),
          onPressed: () { /* TODO: 이전 곡 로직 */ },
        ),
        // 재생/일시정지
        CircleAvatar(
          radius: 35,
          backgroundColor: Colors.white,
          child: IconButton(
            icon: const Icon(Icons.pause, color: Colors.black, size: 40),
            onPressed: () { /* TODO: 재생/일시정지 로직 */ },
          ),
        ),
        // 다음 곡
        IconButton(
          icon: const Icon(Icons.skip_next, color: Colors.white, size: 48),
          onPressed: () { /* TODO: 다음 곡 로직 */ },
        ),
        // 반복
        IconButton(
          icon: Icon(Icons.repeat, color: Colors.grey[400], size: 28),
          onPressed: () { /* TODO: 반복 로직 */ },
        ),
      ],
    );
  }

  // 가사 섹션 위젯
  Widget _buildLyricsSection(Color primaryColor) {
    // 이미지에 보이는 가사 텍스트
    const String currentLyric = "Create you wish it feel high";
    const String nextLyric = "You never look at the sky";
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // 현재 가사 (강조)
        Container(
          padding: const EdgeInsets.all(15),
          decoration: BoxDecoration(
            color: primaryColor.withOpacity(0.1), // 흐릿한 녹색 배경
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: primaryColor, width: 1),
          ),
          child: Text(
            currentLyric,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: primaryColor,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        const SizedBox(height: 10),
        // 다음 가사
        Text(
          nextLyric,
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Colors.grey[500],
            fontSize: 16,
          ),
        ),
      ],
    );
  }
}