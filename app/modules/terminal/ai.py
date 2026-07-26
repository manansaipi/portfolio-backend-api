import os
import time
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from google import genai
from google.genai import types

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.modules.terminal.schemas import AIRequest
from app.modules.terminal.constants import SYSTEM_PROMPT, MODELS
from app.modules.terminal.tts import generate_tts_audio
from app.modules.terminal.terminal_logs import save_terminal_log_entry

router = APIRouter(
    prefix="/api/ai",
    tags=["AI"]
)

@router.post("/ask")
@limiter.limit("5/day")
def ask_ai(request: Request, payload: AIRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    start_time = time.time()

    # Retrieve API keys from env
    key1 = os.environ.get("GEMINI_API_KEY", "")
    key2 = os.environ.get("GEMINI_API_KEY_2", "")
    keys = [k for k in [key1, key2] if k]

    if not keys:
        return {"response": "System error: Gemini API key is missing. The site owner needs to add GEMINI_API_KEY to their environment variables."}

    for key in keys:
        client = genai.Client(api_key=key)
        for model_name in MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=payload.question,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.7,
                    ),
                )
                print(f"Successfully generated response using model {model_name} with key ending in {key[-4:] if key else 'None'}")
                
                audio_result = generate_tts_audio(response.text)
                execution_time_ms = int((time.time() - start_time) * 1000)
                audio_b64 = audio_result.get("audioBase64") if isinstance(audio_result, dict) else None

                # Save AI log to database
                try:
                    save_terminal_log_entry(
                        db=db,
                        request=request,
                        background_tasks=background_tasks,
                        input_text=payload.question,
                        is_ai_mode=True,
                        response_text=response.text,
                        execution_time_ms=execution_time_ms,
                        audio_base64=audio_b64,
                        screen_width=payload.screen_width,
                        screen_height=payload.screen_height,
                        language=payload.language,
                        referrer=payload.referrer
                    )
                except Exception as log_err:
                    print(f"Error saving AI log to DB: {log_err}")
                
                if audio_result:
                    return {
                        "response": response.text,
                        "audioResult": audio_result
                    }
                else:
                    return {
                        "response": response.text
                    }

            except Exception as e:
                print(f"Failed using model {model_name} with key ending in {key[-4:] if key else 'None'}: {e}")
                # If we exhausted the models and keys
                if key == keys[-1] and model_name == MODELS[-1]:
                    return {"response": "Sorry, the AI service is currently unavailable or quota exceeded."}
                continue
    
    return {"response": "Sorry, all API services are currently unavailable."}
