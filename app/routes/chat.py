from fastapi import APIRouter
import os
import re

from app.config import UPLOAD_DIR
from app.services.form_parser import extract_questions
from app.services.validator import validate_answer
from app.services.language import translate

router = APIRouter(prefix="/chat")

sessions = {}

SUPPORTED_LANGS = {
    "english": "en",
    "tamil": "ta",
    "hindi": "hi"
}


# =========================
# DETECT LANGUAGE
# =========================
def detect_lang(text):
    # Tamil Unicode range
    if re.search(r"[\u0B80-\u0BFF]", text):
        return "ta"
    return "en"


# =========================
# SAFE TRANSLATE (GENERIC)
# =========================
def safe_translate(text, target_lang):
    try:
        source_lang = detect_lang(text)

        # if already same language → no need to translate
        if source_lang == target_lang:
            return text

        translated = translate(text, source_lang, target_lang)

        # fallback if translation fails
        if translated.strip().lower() == text.strip().lower():
            translated = translate("Form field: " + text, source_lang, target_lang)

        return translated

    except:
        return text


# =========================
# CLEAN QUESTIONS
# =========================
def clean_questions(raw_questions):
    cleaned = []
    seen = set()

    for q in raw_questions:
        text = re.sub(r"\s+", " ", q["question"]).strip()

        if len(text) < 3:
            continue

        if len(text.split()) > 15:
            continue

        if text.lower() in seen:
            continue
        seen.add(text.lower())

        cleaned.append({
            "id": q["id"],
            "question": text
        })

    return cleaned


# =========================
# START CHAT
# =========================
@router.post("/start")
def start_chat(session_id: str, filename: str):

    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        return {"question": "File not found ❌"}

    raw_questions = extract_questions(file_path)
    questions = clean_questions(raw_questions)

    if not questions:
        return {"question": "No valid questions detected ❌"}

    sessions[session_id] = {
        "questions": questions,
        "answers": {},
        "index": 0,
        "language": None,
        "filename": filename
    }

    return {
        "question": "Which language do you prefer? (English / Tamil / Hindi)"
    }


# =========================
# ANSWER FLOW
# =========================
@router.post("/answer")
def answer(session_id: str, text: str):

    session = sessions.get(session_id)

    if not session:
        return {"completed": True}

    # ================= LANGUAGE SELECT =================
    if session["language"] is None:
        lang = text.lower().strip()

        if lang not in SUPPORTED_LANGS:
            return {"question": "Choose: English / Tamil / Hindi"}

        session["language"] = SUPPORTED_LANGS[lang]

        first_q = session["questions"][0]["question"]

        translated = safe_translate(first_q, session["language"])
        return {"question": translated}

    # ================= END =================
    if session["index"] >= len(session["questions"]):
        return {"completed": True, "answers": session["answers"]}

    current = session["questions"][session["index"]]
    q_text = current["question"]
    q_id = current["id"]

    valid, result = validate_answer(q_text, text)

    if not valid:
        translated_error = safe_translate(result, session["language"])
        return {"question": translated_error}

    session["answers"][q_id] = result
    session["index"] += 1

    if session["index"] >= len(session["questions"]):
        return {"completed": True, "answers": session["answers"]}

    next_q = session["questions"][session["index"]]["question"]

    translated = safe_translate(next_q, session["language"])

    return {"question": translated}