from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import chat, pdf_routes, upload

app = FastAPI(title="AI Form Assistant")

# CORS for Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(pdf_routes.router)

@app.get("/")
def root():
    return {"message": "AI Form Assistant API is running"}