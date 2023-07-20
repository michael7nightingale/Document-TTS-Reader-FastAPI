from fastapi import APIRouter, Request, Body
from app.services.tts import synth_audio


translator_router = APIRouter(
    prefix='/translator'
)


@translator_router.post("/text-to-speech")
async def text_to_speech(request: Request, text: str = Body(), language: str = "ru"):
    """Main page."""
    filepath = request.app.state.STATIC_DIR + "124124"
    synth_audio(filepath=filepath, text=text)
