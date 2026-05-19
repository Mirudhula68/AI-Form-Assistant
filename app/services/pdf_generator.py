from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


def generate_pdf(questions, answers, output_path):

    # 🔥 FONT PATH
    font_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "fonts",
        "NotoSansTamil-Regular.ttf"
    )

    # 🔥 REGISTER FONT
    pdfmetrics.registerFont(TTFont("TamilFont", font_path))

    doc = SimpleDocTemplate(output_path)

    styles = getSampleStyleSheet()

    # 🔥 CUSTOM STYLE WITH TAMIL FONT
    tamil_style = ParagraphStyle(
        "TamilStyle",
        parent=styles["Normal"],
        fontName="TamilFont",
        fontSize=11,
        leading=14
    )

    elements = []

    for i, q in enumerate(questions, 1):
        q_text = q["question"]
        q_id = q["id"]

        ans = answers.get(q_id, "")

        text = f"{i}. {q_text} : {ans}"

        elements.append(Paragraph(text, tamil_style))
        elements.append(Spacer(1, 10))

    doc.build(elements)