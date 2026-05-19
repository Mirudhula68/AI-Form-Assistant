import pytesseract
from PIL import Image
import re
import os
import subprocess
import tempfile


# =========================
# CLEAN TEXT
# =========================
def clean_text(text: str) -> str:

    # remove extra spaces
    text = re.sub(r"\s+", " ", text)

    # remove numbering
    text = re.sub(r"^\d+[\.\s]*", "", text)

    # remove symbols
    text = re.sub(r"[;:]", "", text)

    # remove repeated Tamil OCR junk
    text = re.sub(r'([அ-ஹ])\1{2,}', '', text)

    # remove standalone Tamil garbage words
    text = re.sub(r'\b[அ-ஹ]{2,}\b', '', text)

    return text.strip()


# =========================
# REMOVE EXTRA CONTENT
# =========================
def remove_extra(text: str) -> str:
    text = re.sub(r"\(.*?attested.*?\)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"xerox.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"day\s+month\s+year", "", text, flags=re.IGNORECASE)
    return text.strip()


# =========================
# KEEP ONLY ENGLISH QUESTION
# =========================
def keep_english(text):

    english_words = re.findall(
        r'[A-Za-z][A-Za-z/\-\s()]*',
        text
    )

    result = " ".join(english_words)

    result = re.sub(r"\s+", " ", result)

    return result.strip()


# =========================
# CHECK TEXT
# =========================
def has_text(text: str) -> bool:
    return bool(re.search(r"[a-zA-Z]", text))


# =========================
# HEADER DETECTION
# =========================
def is_header(text: str) -> bool:
    t = text.lower()

    headers = [
        "application", "form", "award",
        "government", "department",
        "registration", "office"
    ]

    return any(word in t for word in headers)


# =========================
# VALID QUESTION
# =========================
def is_valid_question(text: str) -> bool:
    text = text.strip()

    if len(text) < 3:
        return False

    if not has_text(text):
        return False

    if len(text.split()) > 15:
        return False

    if is_header(text):
        return False

    return True


# =========================
# SPLIT SUB QUESTIONS
# =========================
def split_sub_questions(text):

    text = re.sub(r"\(\d+\)", "", text)

    # Tamil sub questions
    parts = re.split(r"\([\u0B85-\u0BB9]\)", text)

    cleaned_parts = []

    for p in parts:
        p = re.sub(r"[;:,]", "", p).strip()

        if len(p) > 2:
            cleaned_parts.append(p)

    # English fallback
    if len(cleaned_parts) <= 1:
        parts = re.split(r"\([a-zA-Z]\)", text)

        cleaned_parts = []

        for p in parts:
            p = re.sub(r"[;:,]", "", p).strip()

            if len(p) > 2:
                cleaned_parts.append(p)

    return cleaned_parts if cleaned_parts else [text]


# =========================
# MAIN EXTRACTION
# =========================
def extract_questions_from_image(image_path: str):

    text = pytesseract.image_to_string(
        Image.open(image_path).convert("L"),
        lang="tam+eng",
        config="--oem 3 --psm 4"
    )

    print("\n===== OCR OUTPUT =====\n", text)

    lines = text.split("\n")

    questions = []
    q_index = 1
    buffer = ""

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if is_header(line):
            continue

        # new numbered question
        if re.match(r"^\d+\.", line):

            if buffer:

                cleaned = clean_text(buffer)
                cleaned = remove_extra(cleaned)

                # keep only English
                cleaned = keep_english(cleaned)

                parts = split_sub_questions(cleaned)

                for part in parts:
                    if is_valid_question(part):
                        questions.append({
                            "id": str(q_index),
                            "question": part
                        })
                        q_index += 1

            buffer = line

        else:
            if buffer:
                buffer += " " + line
            else:
                buffer = line

    # LAST QUESTION
    if buffer:

        cleaned = clean_text(buffer)
        cleaned = remove_extra(cleaned)

        # keep only English
        cleaned = keep_english(cleaned)

        parts = split_sub_questions(cleaned)

        for part in parts:
            if is_valid_question(part):
                questions.append({
                    "id": str(q_index),
                    "question": part
                })
                q_index += 1

    # FALLBACK
    if len(questions) < 3:
        print("⚠️ fallback triggered")

        questions = []
        q_index = 1

        for line in lines:

            line = clean_text(line)
            line = remove_extra(line)

            # keep only English
            line = keep_english(line)

            parts = split_sub_questions(line)

            for part in parts:
                if is_valid_question(part):
                    questions.append({
                        "id": str(q_index),
                        "question": part
                    })
                    q_index += 1

    return questions


# =========================
# PDF SUPPORT
# =========================
def extract_questions_from_pdf(pdf_path: str):

    temp_dir = tempfile.mkdtemp()
    prefix = os.path.join(temp_dir, "page")

    subprocess.run(
        ["pdftoppm", "-png", "-r", "300", pdf_path, prefix],
        check=True
    )

    all_q = []

    for f in sorted(os.listdir(temp_dir)):
        if f.endswith(".png"):
            all_q.extend(
                extract_questions_from_image(
                    os.path.join(temp_dir, f)
                )
            )

    return all_q


def extract_questions(file_path: str):

    if file_path.lower().endswith(".pdf"):
        return extract_questions_from_pdf(file_path)

    return extract_questions_from_image(file_path)