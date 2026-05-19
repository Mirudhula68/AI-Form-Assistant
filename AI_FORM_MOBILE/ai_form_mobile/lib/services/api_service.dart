import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl =
      "http://192.168.1.12:8000";

  // Upload file
  static Future<Map<String, dynamic>> uploadFile(
      File file) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse("$baseUrl/chat/upload/"),
    );

    request.files.add(
      await http.MultipartFile.fromPath(
        'file',
        file.path,
      ),
    );

    var response = await request.send();

    var responseData =
        await response.stream.bytesToString();

    return jsonDecode(responseData);
  }

  // Start chat
  static Future<Map<String, dynamic>> startChat({
    required String sessionId,
    required String filename,
  }) async {
    final response = await http.post(
      Uri.parse(
          "$baseUrl/chat/start?session_id=$sessionId&filename=$filename"),
    );

    return jsonDecode(response.body);
  }

  // Send answer
  static Future<Map<String, dynamic>> sendAnswer({
    required String sessionId,
    required String text,
  }) async {
    final response = await http.post(
      Uri.parse(
          "$baseUrl/chat/answer?session_id=$sessionId&text=$text"),
    );

    return jsonDecode(response.body);
  }
  // Download generated PDF
static String getPdfUrl(String sessionId) {
  return "$baseUrl/generate-pdf?session_id=$sessionId";
}
}