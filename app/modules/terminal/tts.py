from fastapi import APIRouter, HTTPException
from fastapi import APIRouter, HTTPException
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
        
        # Returns an AudioWithTimestampsResponse object
        response_obj = client.text_to_speech.convert_with_timestamps(
            voice_id="JBFqnCBsd6RMkjVDRZzb", 
            text=request.text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        # Manually construct the dict to ensure stable JSON keys and avoid serialization issues
        return {
            "audio_base64": response_obj.audio_base_64,
            "alignment": {
                "characters": response_obj.alignment.characters,
                "character_start_times_seconds": response_obj.alignment.character_start_times_seconds,
                "character_end_times_seconds": response_obj.alignment.character_end_times_seconds
            }
        }
    except Exception as e:
        print(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail="Error generating speech")
