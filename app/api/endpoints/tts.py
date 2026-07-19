from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
from elevenlabs.client import ElevenLabs

router = APIRouter()

class TTSRequest(BaseModel):
    text: str
    
@router.post("/generate")
async def generate_speech(request: TTSRequest):
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ElevenLabs API key not configured")
        
    try:
        client = ElevenLabs(api_key=api_key)
        
        # Returns an iterator of bytes
        audio_stream = client.text_to_speech.convert(
            voice_id="4O1sYUnmtThcBoSBrri7",
            text=request.text,
            model_id="eleven_multilingual_v2"
        )
        
        return StreamingResponse(audio_stream, media_type="audio/mpeg")
    except Exception as e:
        print(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail="Error generating speech")
