import 'package:flutter/material.dart';
import 'screens/home_page.dart';

void main() {
  runApp(const GrooviaApp());
}

class GrooviaApp extends StatelessWidget {
  const GrooviaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Groovia',
      theme: ThemeData.dark().copyWith(scaffoldBackgroundColor: Colors.black),
      home: const HomePage(), // ✅ 홈화면 지정
    );
  }
}
