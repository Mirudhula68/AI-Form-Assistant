from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

from app.routes.chat import sessions
from app.services.pdf_generator import generate_pdf

router = APIRouter()


@router.get("/generate-pdf")
def generate_pdf_api(session_id: str):

    session = sessions.get(session_id)

    if not session:
        return {"error": "Session not found"}

    questions = session["questions"]
    answers = session["answers"]

    output_path = "filled_form.pdf"

    generate_pdf(questions, answers, output_path)

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename="filled_form.pdf"
    )