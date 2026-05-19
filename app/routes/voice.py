from fastapi import APIRouter, UploadFile, File
import speech_recognition as sr

router = APIRouter(prefix="/voice")

@router.post("/")
async def voice_to_text(
    file: UploadFile = File(...),
    language: str = "en"
):
    recognizer = sr.Recognizer()

    with sr.AudioFile(file.file) as source:
        audio = recognizer.record(source)

    lang_code = "ta-IN" if language.lower() == "tamil" else "en-IN"

    text = recognizer.recognize_google(audio, language=lang_code)

    return {"text": text}