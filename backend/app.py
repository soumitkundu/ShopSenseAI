import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
from config import Config
from bot.bot_handler import ShopSenseBot
from services.speech_service import text_to_speech_bytes

# ── Validate credentials at startup ───────────────────────────────
Config.validate()

# ── App setup ─────────────────────────────────────────────────────
app = FastAPI(
    title="ShopSense AI",
    description="Multimodal e-commerce product recommendation bot",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bot = ShopSenseBot()

# ── In-memory session store ────────────────────────────────────────
# Key: session_id string  →  Value: list of {role, content} dicts
# In production replace with Redis or Azure Cache
sessions: dict[str, list[dict]] = {}

MAX_HISTORY_TURNS = 10  # keep last 5 exchanges (10 messages)


def get_history(session_id: str) -> list[dict]:
    return sessions.get(session_id, [])


def update_history(
    session_id: str,
    user_message: str,
    assistant_message: str,
) -> None:
    history = sessions.setdefault(session_id, [])
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": assistant_message})
    # Trim to keep memory bounded
    if len(history) > MAX_HISTORY_TURNS:
        sessions[session_id] = history[-MAX_HISTORY_TURNS:]


# ── Request / Response schemas ─────────────────────────────────────
class TextRequest(BaseModel):
    session_id: str
    message: str


class TextResponse(BaseModel):
    session_id: str
    recommendation: str


# ── Routes ─────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health():
    """Quick liveness check."""
    return {"status": "ok", "service": "ShopSense AI", "version": "1.0.0"}


@app.post("/chat/text", response_model=TextResponse, tags=["Chat"])
async def chat_text(request: TextRequest):
    """
    Text modality endpoint.
    Accepts a plain text message and returns a GPT-4 recommendation.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    history = get_history(request.session_id)
    recommendation = await bot.handle_text(request.message, history)
    update_history(request.session_id, request.message, recommendation)

    return TextResponse(
        session_id=request.session_id,
        recommendation=recommendation,
    )


@app.post("/chat/voice", tags=["Chat"])
async def chat_voice(
    session_id: str = Form(...),
    audio_file: UploadFile = File(..., description="WAV audio file"),
):
    """
    Voice modality endpoint.
    Accepts a WAV audio upload, transcribes it, and returns:
    - transcript: what the bot heard
    - recommendation: GPT-4 product recommendation
    - audio_url: hint to call /tts with the recommendation text
    """
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=400,
            detail="Only audio files are accepted. Please upload a WAV file.",
        )

    audio_bytes = await audio_file.read()
    history = get_history(session_id)
    result = await bot.handle_voice(audio_bytes, history)

    update_history(session_id, result["transcript"], result["recommendation"])

    return JSONResponse({
        "session_id": session_id,
        "transcript": result["transcript"],
        "recommendation": result["recommendation"],
    })


@app.post("/chat/image", tags=["Chat"])
async def chat_image(
    session_id: str = Form(...),
    image_file: UploadFile = File(..., description="Product image (JPG/PNG)"),
):
    """
    Image modality endpoint.
    Accepts a product image upload, analyses it with Azure Computer Vision,
    and returns GPT-4o-mini product recommendations based on visual attributes.
    """
    if not image_file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are accepted (JPG, PNG).",
        )

    image_bytes = await image_file.read()
    history = get_history(session_id)
    result = await bot.handle_image(image_bytes, history)

    update_history(session_id, result["vision_summary"], result["recommendation"])

    return JSONResponse({
        "session_id": session_id,
        "vision_summary": result["vision_summary"],
        "recommendation": result["recommendation"],
    })


@app.post("/tts", tags=["Speech"])
async def synthesise_speech(request: TextRequest):
    """
    Text-to-Speech endpoint.
    Converts a recommendation text to WAV audio bytes.
    Frontend can play this directly in the browser.
    """
    audio_bytes = text_to_speech_bytes(request.message)
    return Response(
        content=audio_bytes,
        media_type="audio/wav",
        headers={"Content-Disposition": "inline; filename=response.wav"},
    )


@app.delete("/session/{session_id}", tags=["Session"])
async def clear_session(session_id: str):
    """Clear conversation history for a given session."""
    sessions.pop(session_id, None)
    return {"message": f"Session {session_id} cleared."}


# ── Entry point ────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=Config.APP_HOST,
        port=Config.APP_PORT,
        reload=Config.DEBUG,
    )