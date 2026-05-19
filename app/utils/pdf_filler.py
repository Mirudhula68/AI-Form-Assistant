import cv2
import numpy as np
import pytesseract
import re
from pytesseract import Output
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import blue, black


# ==================================================
# CHECKBOX DETECTION
# ==================================================
def detect_checkboxes(gray):
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        15, 2
    )

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    boxes = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if 12 < w < 30 and 12 < h < 30:
            boxes.append((x, y, w, h))

    return boxes


def match_checkbox(label, answer):
    l = label.lower().strip()
    a = answer.lower().strip()

    mapping = {
        "m": ["male", "m"],
        "f": ["female", "f"],
        "tg": ["tg", "transgender"],
        "sc": ["sc"],
        "st": ["st"],
        "mbc": ["mbc"],
        "bc": ["bc"],
        "oc": ["oc"]
    }

    return l in mapping and a in mapping[l]


def tick_checkbox(c, box, img_w, img_h, page_w, page_h):
    x, y, w, h = box
    px = (x + w / 2) / img_w * page_w
    py = page_h - ((y + h / 2) / img_h * page_h)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(px - 4, py - 4, "✔")


# ==================================================
# MAIN PDF FILLER
def auto_fill_any_form(image_path, output_pdf, answers_dict, family_members=None):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not loaded")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    pil = Image.open(image_path)

    ocr = pytesseract.image_to_data(
        pil,
        output_type=Output.DICT,
        config="--psm 6"
    )

    c = canvas.Canvas(output_pdf, pagesize=A4)
    page_w, page_h = A4
    img_h, img_w = img.shape[:2]

    # Background
    c.drawImage(image_path, 0, 0, width=page_w, height=page_h)

    # ==================================================
    # STEP 1: NORMALIZE QUESTION TEXT
    # ==================================================
    def normalize(text):
        t = (
            text.lower()
            .replace("(a)", "")
            .replace("(b)", "")
            .replace("(c)", "")
            .replace("(d)", "")
            .replace("(e)", "")
            .replace(":", "")
        )
        t = re.sub(r"_{2,}", "", t)
        t = re.sub(r"\.{2,}", "", t)
        t = t.strip()
        if t.startswith("enter "):
            t = t[6:].strip()
        
        t = re.sub(r"^\d+[\.\)]\s*", "", t)
        return t

    # ==================================================
    # STEP 2: BUILD ANCHORS (question → index)
    # ==================================================
    anchors = {}
    
    valid_ocr = []
    for i, w in enumerate(ocr["text"]):
        if not w:
            continue
        w_norm = normalize(w)
        if w_norm:
            valid_ocr.append({"index": i, "text": w_norm})

    for q in answers_dict.keys():
        qn = normalize(q)
        if not qn:
            continue
            
        q_tokens = qn.split()
        if not q_tokens:
            continue
            
        best_match_idx = -1
        
        # 1. Exact sequence search
        for idx in range(len(valid_ocr) - len(q_tokens) + 1):
            match = True
            for j, qt in enumerate(q_tokens):
                if qt not in valid_ocr[idx + j]["text"]:
                    match = False
                    break
            
            if match:
                best_match_idx = valid_ocr[idx + len(q_tokens) - 1]["index"]
                break
                
        # 2. Fallback substring search across text
        if best_match_idx == -1:
            running_str = ""
            for v in valid_ocr:
                running_str += v["text"] + " "
                if qn in running_str:
                    best_match_idx = v["index"]
                    break

        if best_match_idx != -1:
            # Check if there is a blank nearby to adjust X spacing slightly
            is_b = False
            for k in range(best_match_idx, min(best_match_idx + 6, len(ocr["text"]))):
                t = ocr["text"][k]
                if re.search(r"_{3,}|\.{3,}", t):
                    is_b = True
                    # Let's anchor exactly on the blank if we found one!
                    best_match_idx = k
                    break
            
            anchors[q] = {"index": best_match_idx, "is_blank": is_b}

    # ==================================================
    # STEP 3 & 4: FILL TEXT FIELDS AND TICK CHECKBOXES
    # ==================================================
    checkboxes = detect_checkboxes(gray)

    for q, answer in answers_dict.items():
        if q not in anchors:
            continue

        anchor_info = anchors[q]
        i = anchor_info["index"]
        is_blank = anchor_info["is_blank"]

        x = ocr["left"][i]
        y = ocr["top"][i]
        w = ocr["width"][i]
        h = ocr["height"][i]

        # Check if answer corresponds to a checkbox for THIS question
        y_ref = y
        found_checkbox = False

        for idx, label in enumerate(ocr["text"]):
            label = label.strip()
            if not label:
                continue
            
            # Check horizontally parallel OCR tokens
            if abs(ocr["top"][idx] - y_ref) < 18:
                if match_checkbox(label, str(answer)):
                    lx = ocr["left"][idx]
                    lw = ocr["width"][idx]
                    
                    for box in checkboxes:
                        bx, by, bw, bh = box
                        
                        # Match vertically and horizontally closely
                        if abs(by - ocr["top"][idx]) < 12:
                            # Box must be horizontally close to the extracted label text
                            # e.g., to the left or right of it within 40 pixels
                            if abs(bx + bw - lx) < 40 or abs(lx - bx) < 40 or abs(bx - (lx + lw)) < 40:
                                tick_checkbox(c, box, img_w, img_h, page_w, page_h)
                                found_checkbox = True

        # Only draw the text if no checkbox was ticked for this answer
        if not found_checkbox:
            if is_blank:
                pdf_x = (x + 10) / img_w * page_w
            else:
                pdf_x = (x + w + 12) / img_w * page_w

            pdf_y = page_h - ((y + h - 4) / img_h * page_h)

            c.setFont("Helvetica", 11)
            c.setFillColor(blue)
            c.drawString(pdf_x, pdf_y, str(answer))
            c.setFillColor(black)



    c.save()
