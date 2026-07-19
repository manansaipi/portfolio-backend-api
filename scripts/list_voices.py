import os
from dotenv import load_dotenv
load_dotenv()
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key=os.environ.get("ELEVENLABS_API_KEY"))
response = client.voices.get_all()
for v in response.voices:
    print(f"{v.name}: {v.voice_id} (category: {v.category})")
