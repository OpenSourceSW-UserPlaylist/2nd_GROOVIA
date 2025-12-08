import 'package:flutter/material.dart';
import 'login_screen.dart'; // LoginScreen으로 이동하기 위해 반드시 필요함

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    // 3초 후 로그인 화면으로 이동
    Future.delayed(const Duration(seconds: 3), () {
      if (mounted) {
        Navigator.of(context).pushReplacement(
          // 여기서 LoginScreen 위젯을 사용합니다.
          MaterialPageRoute(builder: (context) => const LoginScreen()),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Icon(
              Icons.music_note,
              color: Theme.of(context).primaryColor, 
              size: 80.0,
            ),
            const SizedBox(height: 10),
            Text(
              'Groovia',
              style: TextStyle(
                color: Theme.of(context).primaryColor, 
                fontSize: 36,
                fontWeight: FontWeight.bold,
                letterSpacing: -1.0,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
// 주의: login_screen.dart를 가져오는 것은 필요하며, 경고가 계속되면 IDE를 다시 시작해 보세요.