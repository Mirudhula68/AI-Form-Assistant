import 'dart:io';

import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:open_filex/open_filex.dart';
import 'package:path_provider/path_provider.dart';
import 'package:speech_to_text/speech_to_text.dart';

import 'services/api_service.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'AI Form Assistant',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() =>
      _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final TextEditingController
      answerController =
      TextEditingController();

  final FlutterTts flutterTts =
      FlutterTts();

  final SpeechToText speechToText =
      SpeechToText();

  String question = "";
  bool isLoading = false;
  bool fileUploaded = false;
  bool completed = false;
  bool isListening = false;

  String sessionId = DateTime.now()
      .millisecondsSinceEpoch
      .toString();

  @override
  void initState() {
    super.initState();
    initTTS();
  }

  Future<void> initTTS() async {
    await flutterTts.setSpeechRate(
      0.45,
    );
    await flutterTts.setPitch(1.0);
  }

  Future<void> speak(
      String text) async {
    await flutterTts.stop();
    await flutterTts.speak(text);
  }

  Future<void>
      pickAndUploadFile() async {
    try {
  setState(() {
    isLoading = true;

    // reset old form state
    completed = false;
    fileUploaded = false;
    question = "";
    answerController.clear();

    // create fresh session
    sessionId = DateTime.now()
        .millisecondsSinceEpoch
        .toString();
  });

      FilePickerResult? result =
          await FilePicker.platform
              .pickFiles();

      if (result == null) {
        setState(() {
          isLoading = false;
        });
        return;
      }

      File file = File(
        result.files.single.path!,
      );

      final uploadResponse =
          await ApiService
              .uploadFile(file);

      String filename =
          uploadResponse[
              "filename"];

      final startResponse =
          await ApiService
              .startChat(
        sessionId: sessionId,
        filename: filename,
      );

      String q =
          startResponse[
              "question"];

      setState(() {
        question = q;
        fileUploaded = true;
        isLoading = false;
      });

      speak(q);
    } catch (e) {
      setState(() {
        isLoading = false;
      });

      if (!mounted) return;

      ScaffoldMessenger.of(
              context)
          .showSnackBar(
        SnackBar(
          content:
              Text("Error: $e"),
        ),
      );
    }
  }

  Future<void> sendAnswer()
      async {
    if (answerController
        .text
        .trim()
        .isEmpty) {return; }

    try {
      setState(() {
        isLoading = true;
      });

      final response =
          await ApiService
              .sendAnswer(
        sessionId: sessionId,
        text: answerController
            .text,
      );

      answerController.clear();

      if (response[
              "completed"] ==
          true) {
        setState(() {
          completed = true;
          question =
              "Form completed successfully ✅";
          isLoading = false;
        });

        speak(
          "Form completed successfully",
        );

        return;
      }

      String q =
          response["question"];

      setState(() {
        question = q;
        isLoading = false;
      });

      speak(q);
    } catch (e) {
      setState(() {
        isLoading = false;
      });
    }
  }

  Future<void> startListening()
      async {
    bool available =
        await speechToText
            .initialize();

    if (!available) return;

    setState(() {
      isListening = true;
    });

    speechToText.listen(
      onResult: (result) {
        setState(() {
          answerController.text =
              result.recognizedWords;
        });
      },
    );
  }

  Future<void> stopListening()
      async {
    await speechToText.stop();

    setState(() {
      isListening = false;
    });
  }

  Future<void>
      downloadPdf() async {
    try {
      setState(() {
        isLoading = true;
      });

      Directory dir =
          await getApplicationDocumentsDirectory();

      String savePath =
          "${dir.path}/filled_form.pdf";

      await Dio().download(
        ApiService.getPdfUrl(
            sessionId),
        savePath,
      );

      setState(() {
        isLoading = false;
      });

      OpenFilex.open(savePath);
    } catch (e) {
      setState(() {
        isLoading = false;
      });

      if (!mounted) return;

      ScaffoldMessenger.of(
              context)
          .showSnackBar(
        SnackBar(
          content:
              Text("Download failed"),
        ),
      );
    }
  }

  @override
  Widget build(
      BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "AI Form Assistant",
        ),
      ),
      body: Padding(
        padding:
            const EdgeInsets.all(
                16),
        child: Column(
          children: [
            ElevatedButton(
              onPressed:
                  isLoading
                      ? null
                      : pickAndUploadFile,
              child: const Text(
                "Upload Form",
              ),
            ),

            const SizedBox(
                height: 30),

            if (question.isNotEmpty)
  Container(
    width: double.infinity,
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: Colors.blue.shade50,
      borderRadius: BorderRadius.circular(12),
    ),
    child: Row(
      crossAxisAlignment:
          CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Text(
            question,
            style:
                const TextStyle(
              fontSize: 18,
            ),
          ),
        ),

        IconButton(
          icon: const Icon(
            Icons.volume_up,
            color: Colors.blue,
          ),
          onPressed: () async {
            await flutterTts.stop();
            await flutterTts.speak(
              question,
            );
          },
        ),
      ],
    ),
  ),

            const SizedBox(
                height: 20),

            if (fileUploaded &&
                !completed)
              TextField(
                controller:
                    answerController,
                decoration:
                    const InputDecoration(
                  border:
                      OutlineInputBorder(),
                  hintText:
                      "Enter answer...",
                ),
              ),

            const SizedBox(
                height: 10),

            if (fileUploaded &&
                !completed)
              Row(
                children: [
                  Expanded(
                    child:
                        ElevatedButton(
                      onPressed:
                          isLoading
                              ? null
                              : sendAnswer,
                      child:
                          const Text(
                        "Send",
                      ),
                    ),
                  ),

                  const SizedBox(
                      width: 10),

                  FloatingActionButton(
                    mini: true,
                    onPressed:
                        isListening
                            ? stopListening
                            : startListening,
                    child: Icon(
                      isListening
                          ? Icons.mic
                          : Icons
                              .mic_none,
                    ),
                  ),
                ],
              ),

            const SizedBox(
                height: 20),

            if (completed)
              ElevatedButton.icon(
                onPressed:
                    downloadPdf,
                icon: const Icon(
                    Icons.download),
                label: const Text(
                  "Download PDF",
                ),
              ),

            if (isLoading)
              const Padding(
                padding:
                    EdgeInsets.only(
                        top: 20),
                child:
                    CircularProgressIndicator(),
              ),
          ],
        ),
      ),
    );
  }
}