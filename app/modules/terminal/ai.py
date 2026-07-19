import os
from fastapi import APIRouter, Request, HTTPException
from google import genai
from google.genai import types

from app.core.rate_limiter import limiter
from app.modules.terminal.schemas import AIRequest
from app.modules.terminal.constants import SYSTEM_PROMPT, MODELS

router = APIRouter(
    prefix="/api/ai",
    tags=["AI"]
)

@router.post("/ask")
@limiter.limit("5/day")
def ask_ai(request: Request, payload: AIRequest):
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
                return {"response": response.text}
            except Exception as e:
                # If we exhausted the models and keys
                if key == keys[-1] and model_name == MODELS[-1]:
                    return {"response": "Sorry, the AI service is currently unavailable or quota exceeded."}
                continue
    
    return {"response": "Sorry, all API services are currently unavailable."}
