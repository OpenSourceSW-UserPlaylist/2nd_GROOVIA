import 'package:flutter/material.dart';
import 'screens/splash_screen.dart';

void main() {
  runApp(const GrooviaApp());
}

class GrooviaApp extends StatelessWidget {
  const GrooviaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Groovia',
      debugShowCheckedModeBanner: false, // 디버그 배너 제거
      theme: ThemeData(
        // 앱의 기본 테마를 어두운 테마로 설정
        brightness: Brightness.dark,
        // Groovia 테마의 메인 컬러로 사용할 녹색 계열을 정의 (Spotify 녹색과 유사)
        primaryColor: const Color(0xFF1DB954), 
        scaffoldBackgroundColor: const Color(0xFF121212), // 어두운 배경색
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF121212),
          elevation: 0,
        ),
        // 텍스트 필드 등에 사용될 입력 테마 설정 (선택 사항)
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: const Color(0xFF424242), // 어두운 입력 필드 배경색
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8.0),
            borderSide: BorderSide.none,
          ),
        ),
        textTheme: const TextTheme(
          bodyLarge: TextStyle(color: Colors.white),
          bodyMedium: TextStyle(color: Colors.white),
          titleMedium: TextStyle(color: Colors.white),
          // 필요한 다른 텍스트 스타일 정의
        ),
      ),
      home: const SplashScreen(), // 첫 화면으로 SplashScreen 지정
    );
  }
}