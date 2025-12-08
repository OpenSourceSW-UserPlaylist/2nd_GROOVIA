import 'package:flutter/material.dart';
import 'home_screen.dart'; // 다음 화면 Import (HomeScreen이 이 파일에서 정의되지 않았으므로 필요)
import 'test_api_page.dart'; // 🔗 API Test Page Import (새로 추가)
import 'test_django_page.dart'; // 🔗 Django Test Page Import (새로 추가)

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _nameController = TextEditingController();

  void _login() {
    if (_nameController.text.isNotEmpty) {
      // 다음 화면으로 이동 (Home Screen)
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (context) => HomeScreen(userName: _nameController.text),),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('이름을 입력해주세요.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final primaryColor = Theme.of(context).primaryColor;

    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        backgroundColor: Colors.transparent,
        elevation: 0,
        // Splash Screen에서 pushReplacement로 왔기 때문에 pop은 동작하지 않지만,
        // 다른 경로로 접근할 경우를 대비하여 백 버튼을 남겨둡니다.
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            Navigator.of(context).pop();
          },
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 30.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            const SizedBox(height: 50),

            // Groovia 로고 섹션
            Column(
              children: [
                Icon(
                  Icons.music_note,
                  color: primaryColor,
                  size: 40.0,
                ),
                const SizedBox(height: 5),
                Text(
                  'Groovia',
                  style: TextStyle(
                    color: primaryColor,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 50),

            // 로그인 타이틀
            const Text(
              'Login to your name',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.white,
                fontSize: 26,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 40),

            // 이름 입력 필드 (TextFormField)
            TextField(
              controller: _nameController,
              decoration: InputDecoration(
                hintText: 'Your name',
                hintStyle: const TextStyle(color: Colors.grey),
                contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.0),
                  borderSide: BorderSide(color: primaryColor, width: 2),
                ),
              ),
              style: const TextStyle(color: Colors.white),
              keyboardType: TextInputType.text,
            ),

            const SizedBox(height: 40),

            // Start 버튼
            SizedBox(
              height: 50,
              child: ElevatedButton(
                onPressed: _login,
                style: ElevatedButton.styleFrom(
                  backgroundColor: primaryColor,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(25.0),
                  ),
                  elevation: 5,
                ),
                child: const Text(
                  'Start',
                  style: TextStyle(
                    color: Colors.black,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),

            const SizedBox(height: 20), // Start 버튼과 새 버튼 사이 간격 추가

            // 🔗 API Test Page 이동 버튼 추가 (요청하신 부분)
            /* SizedBox(
              height: 50, // 높이를 Start 버튼과 일치시킴
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => TestApiPage(),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blueAccent,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(25.0), // Start 버튼과 일치시킴
                  ),
                  elevation: 5,
                ),
                child: const Text(
                  '🔗 API Test Page',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
            ),

            const SizedBox(height: 20),

            // 🔗 Django Test Page 이동 버튼 추가 (요청하신 부분)
            SizedBox(
              height: 50, // 높이를 Start 버튼과 일치시킴
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => DjangoTestScreen(),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blueAccent,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(25.0), // Start 버튼과 일치시킴
                  ),
                  elevation: 5,
                ),
                child: const Text(
                  '🔗 Django Test Page',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
            ), */

            const Spacer(), // 남은 공간을 차지하여 하단 위젯을 밀어냅니다.

            // 하단 Spotify 저작권 표시 (기존과 동일)
            Padding(
              padding: const EdgeInsets.only(bottom: 20.0),
              child: Column(
                children: [
                  const Text(
                    '@Spotify',
                    style: TextStyle(
                      color: Color(0xFF1ED760),
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 5),
                  const Text(
                    'Powered by Spotify',
                    style: TextStyle(
                      color: Colors.grey,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}