import os
import base64
from google import genai
import struct

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY_2"))

try:
    stream = client.interactions.create(
        model="gemini-3.1-flash-tts-preview",
        input="Hello world",
        response_format={"type": "audio"},
        generation_config={
            "speech_config": [
                {"voice": "Despina"}
            ]
        },
        stream=True
    )
    
    audio_bytes = bytearray()
    for event in stream:
        if getattr(event, "event_type", None) == "step.delta":
            if getattr(event, "delta", None) and getattr(event.delta, "type", None) == "audio":
                audio_bytes.extend(base64.b64decode(event.delta.data))
                
    print(f"Received {len(audio_bytes)} bytes of audio data")
    if len(audio_bytes) > 0:
        print(f"First 16 bytes: {audio_bytes[:16].hex()}")
except Exception as e:
    print(f"Error: {e}")
