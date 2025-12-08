import 'package:flutter/material.dart';
import 'song_screen.dart';
import 'song_input_page.dart'; 
import 'library_screen.dart'; // 📌 LibraryScreen import 확인

// 1. 더미 데이터 모델
class Album {
  final String title;
  final String imageUrl;
  final String subtitle;

  Album(this.title, this.imageUrl, this.subtitle);
}

// 2. 더미 데이터 리스트
final List<Album> topVibes = [
  Album('Dark Academia', 'assets/images/dark_academia.png', 'Playlist'),
  Album('Chill Rap', 'assets/images/chill_rap.png', 'Playlist'),
  Album('LoFi', 'assets/images/lofi.png', 'Playlist'),
  Album('Synthwave', 'assets/images/synthwave.png', 'Playlist'),
  Album('Focus Beats', 'assets/images/focus_beats.png', 'Playlist'),
  Album('K-Pop Mix', 'assets/images/k-pop.png', 'Playlist'),
];

final List<Album> topGenres = [
  Album('Hip Hop', 'assets/images/hiphop.png', 'Genre'),
  Album('Pop', 'assets/images/pop.png', 'Genre'),
  Album('Indie', 'assets/images/indie.png', 'Genre'),
  Album('Rock', 'assets/images/rock.png', 'Genre'),
];

class HomeScreen extends StatefulWidget {
  final String userName;
  const HomeScreen({super.key, this.userName = "User"});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0; // 현재 선택된 탭 인덱스

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      bottomNavigationBar: _buildBottomNavBar(context),
      
      // 📌 [수정된 부분] 탭 인덱스에 따라 화면(Body)을 교체합니다.
      body: _currentIndex == 2 
          ? const LibraryScreen() // Index 2 (Library)일 때 라이브러리 화면 표시
          : _buildHomeContent(context), // 그 외에는 기존 홈 화면 표시
    );
  }

  // 📌 기존 홈 화면 코드를 별도 위젯(함수)으로 분리하여 관리하기 쉽게 만듭니다.
  Widget _buildHomeContent(BuildContext context) {
    return CustomScrollView(
      slivers: <Widget>[
        SliverAppBar(
          backgroundColor: Theme.of(context).scaffoldBackgroundColor,
          expandedHeight: 80.0,
          floating: true,
          pinned: false,
          flexibleSpace: FlexibleSpaceBar(
            titlePadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
            title: Text(
              'Hi, ${widget.userName}',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            centerTitle: false,
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.notifications_none, color: Colors.white),
              onPressed: () {},
            ),
            IconButton(
              icon: const Icon(Icons.settings, color: Colors.white),
              onPressed: () {},
            ),
            const SizedBox(width: 10),
          ],
        ),
        SliverList(
          delegate: SliverChildListDelegate(
            [
              const Padding(
                padding: EdgeInsets.fromLTRB(20, 20, 20, 10),
                child: Text(
                  'Your Top Vibes',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              _buildAlbumGrid(topVibes),
              const SizedBox(height: 30),
              const Padding(
                padding: EdgeInsets.fromLTRB(20, 0, 20, 10),
                child: Text(
                  'Top Genres',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              _buildHorizontalList(topGenres),
              const SizedBox(height: 100),
            ],
          ),
        ),
      ],
    );
  }

  // 앨범 그리드 뷰 (동일)
  Widget _buildAlbumGrid(List<Album> albums) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          crossAxisSpacing: 15.0,
          mainAxisSpacing: 15.0,
          childAspectRatio: 3.0,
        ),
        itemCount: albums.length,
        itemBuilder: (context, index) {
          return _AlbumItem(album: albums[index]);
        },
      ),
    );
  }

  // 가로 스크롤 리스트 (동일)
  Widget _buildHorizontalList(List<Album> albums) {
    return SizedBox(
      height: 200,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 20.0),
        itemCount: albums.length,
        itemBuilder: (context, index) {
          return Padding(
            padding: const EdgeInsets.only(right: 15.0),
            child: _GenreCard(album: albums[index]),
          );
        },
      ),
    );
  }

  // 하단 내비게이션 바
  Widget _buildBottomNavBar(BuildContext context) {
    return BottomNavigationBar(
      backgroundColor: const Color(0xFF282828),
      selectedItemColor: Colors.white,
      unselectedItemColor: Colors.grey[600],
      type: BottomNavigationBarType.fixed,
      currentIndex: _currentIndex,
      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.home_filled),
          label: 'Home',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.search),
          label: 'Explore',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.library_books),
          label: 'Library',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.settings),
          label: 'Premium',
        ),
      ],
      onTap: (index) {
        setState(() {
          _currentIndex = index;
        });

        if (index == 1) { // Explore 탭 클릭 시 (페이지 이동)
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => SongInputPage(userName: widget.userName),
            ),
          ).then((_) {
            setState(() {
              _currentIndex = 0; // 돌아오면 홈으로 복귀
            });
          });
        }
        // 📌 Index 2 (Library)는 setState로 _currentIndex가 2가 되면서 body가 자동으로 바뀝니다.
      },
    );
  }
}

// _AlbumItem 위젯 (동일)
class _AlbumItem extends StatelessWidget {
  final Album album;
  const _AlbumItem({required this.album});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF282828),
        borderRadius: BorderRadius.circular(5.0),
      ),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => SongScreen(
                songTitle: album.title,
                artistName: 'Various Artists',
                imageUrl: album.imageUrl,
              ),
            ),
          );
        },
        child: Row(
          children: [
            SizedBox(
              width: 60,
              height: 60,
              child: Image.asset(album.imageUrl, fit: BoxFit.cover, cacheWidth: 200, errorBuilder: (context, error, stackTrace) {
                return Icon(Icons.image, size: 60, color: Colors.grey[400]);
              }),
            ),
            const SizedBox(width: 8),
            Flexible(
              child: Text(
                album.title,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// _GenreCard 위젯 (동일)
class _GenreCard extends StatelessWidget {
  final Album album;
  const _GenreCard({required this.album});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 150,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            height: 150,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(8.0),
              child: Image.asset(album.imageUrl, fit: BoxFit.cover, cacheWidth: 200, errorBuilder: (context, error, stackTrace) {
                return Container(
                  color: Colors.grey[800],
                  child: Center(child: Icon(Icons.image, size: 50, color: Colors.grey[400])),
                );
              }),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            album.title,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
            overflow: TextOverflow.ellipsis,
          ),
          Text(
            album.subtitle,
            style: TextStyle(
              color: Colors.grey[500],
              fontSize: 12,
            ),
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}