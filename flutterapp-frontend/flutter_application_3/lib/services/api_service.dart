import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Android 에뮬레이터 기준
  static const String baseUrl = "http://10.0.2.2:8000";

  /// 1) Ping API
  static Future<String> ping() async {
    final url = Uri.parse("$baseUrl/api/spotify/ping/");
    final res = await http.get(url);

    if (res.statusCode == 200) {
      final jsonBody = jsonDecode(res.body);
      return jsonBody["message"] ?? "No message";
    } else {
      throw Exception("Failed to ping server: ${res.statusCode}");
    }
  }

  /// 2) CSV Songs 조회 API
  static Future<List<dynamic>> getSongs() async {
    final url = Uri.parse("$baseUrl/api/csv/songs/");
    final res = await http.get(url);

    if (res.statusCode == 200) {
      final jsonBody = jsonDecode(res.body);
      return jsonBody["songs"] ?? [];
    } else {
      throw Exception("Failed to load songs: ${res.statusCode}");
    }
  }
}
