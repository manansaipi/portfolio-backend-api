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
    key1 = os.getenv("ELEVENLABS_API_KEY")
    key2 = os.getenv("ELEVENLABS_API_KEY_2")
    key3 = os.getenv("ELEVENLABS_API_KEY_3")
    
    keys = [k for k in [key1, key2, key3] if k]
    if not keys:
        raise HTTPException(status_code=500, detail="ElevenLabs API keys not configured")
        
    voice_ids = [
        "eFXGlWMynZa1K4PISafj",  # Preferred 1
        "4GWZV4vKLWkaf0Oxe6W5",  # Preferred 2
        "pNInz6obpgDQGcFmaJgB"   # Fallback (Adam, free tier compatible)
    ]
    
    for i, api_key in enumerate(keys):
        client = ElevenLabs(api_key=api_key)
        
        response_obj = None
        for voice_id in voice_ids:
            try:
                response_obj = client.text_to_speech.convert_with_timestamps(
                    voice_id=voice_id,
                    text=request.text,
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128"
                )
                break  # Success, exit the voice loop
            except Exception as voice_err:
                print(f"Voice {voice_id} failed for key {i+1} ({voice_err}). Trying next...")
                continue
                
        if response_obj:
            # Manually construct the dict to ensure stable JSON keys and avoid serialization issues
            return {
                "audio_base64": response_obj.audio_base_64,
                "alignment": {
                    "characters": response_obj.alignment.characters,
                    "character_start_times_seconds": response_obj.alignment.character_start_times_seconds,
                    "character_end_times_seconds": response_obj.alignment.character_end_times_seconds
                }
            }
            
        print(f"All voices failed for API key {i+1}. Moving to next key...")
        
    raise HTTPException(status_code=500, detail="Error generating speech with all configured keys and voices")
