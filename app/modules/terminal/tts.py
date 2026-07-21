import os
import base64
import struct
from google import genai
from elevenlabs.client import ElevenLabs
from .constants import GEMINI_TTS_MODELS, ELEVENLABS_VOICE_IDS

def generate_tts_audio(text: str):
    if not text or not text.strip():
        return None
        
    audio_data = _generate_gemini_tts(text)
    if not audio_data:
        audio_data = _generate_elevenlabs_tts(text)
        
    return audio_data

def _generate_gemini_tts(text: str):
    gemini_key1 = os.getenv("GEMINI_API_KEY")
    gemini_key2 = os.getenv("GEMINI_API_KEY_2")
    
    gemini_keys = [k for k in [gemini_key1, gemini_key2] if k]
    
    for gemini_key in gemini_keys:
        try:
            client = genai.Client(api_key=gemini_key)
            for model_id in GEMINI_TTS_MODELS:
                try:
                    stream = client.interactions.create(
                        model=model_id,
                        input=text,
                        response_format={"type": "audio"},
                        generation_config={
                            "speech_config": [
                                {"voice": "Achernar"}
                            ]
                        },
                        stream=True
                    )
                    
                    audio_bytes = bytearray()
                    for event in stream:
                        if getattr(event, "event_type", None) == "step.delta":
                            if getattr(event, "delta", None) and getattr(event.delta, "type", None) == "audio":
                                audio_bytes.extend(base64.b64decode(event.delta.data))
                                
                    if audio_bytes:
                        # Create WAV header for 24kHz, 16-bit, mono PCM
                        sample_rate = 24000
                        num_channels = 1
                        bits_per_sample = 16
                        num_frames = len(audio_bytes) // (num_channels * (bits_per_sample // 8))
                        
                        byte_rate = sample_rate * num_channels * (bits_per_sample // 8)
                        block_align = num_channels * (bits_per_sample // 8)
                        data_size = num_frames * block_align
                        chunk_size = 36 + data_size
                        
                        wav_header = struct.pack('<4sI4s4sIHHIIHH4sI',
                                                 b'RIFF', chunk_size, b'WAVE', b'fmt ', 16,
                                                 1, num_channels, sample_rate, byte_rate,
                                                 block_align, bits_per_sample, b'data', data_size)
                        
                        final_audio = wav_header + audio_bytes
                        print(f"Successfully generated Gemini TTS using model {model_id} with key ending in {gemini_key[-4:] if gemini_key else 'None'}")
                        return {
                            "audio_base64": base64.b64encode(final_audio).decode('utf-8'),
                            "alignment": None,
                            "audio_format": "audio/wav"
                        }
                except Exception as model_err:
                    print(f"Gemini TTS ({model_id}) failed: {model_err}")
                    continue
        except Exception as key_err:
            print(f"Gemini key failed: {key_err}")
            continue
            
    return None

def _generate_elevenlabs_tts(text: str):
    key1 = os.getenv("ELEVENLABS_API_KEY")
    key2 = os.getenv("ELEVENLABS_API_KEY_2")
    key3 = os.getenv("ELEVENLABS_API_KEY_3")
    
    keys = [k for k in [key1, key2, key3] if k]
    if not keys:
        return None
    
    for i, api_key in enumerate(keys):
        client = ElevenLabs(api_key=api_key)
        
        response_obj = None
        for voice_id in ELEVENLABS_VOICE_IDS:
            try:
                response_obj = client.text_to_speech.convert_with_timestamps(
                    voice_id=voice_id,
                    text=text,
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128"
                )
                break  # Success, exit the voice loop
            except Exception as voice_err:
                print(f"Voice {voice_id} failed for key {i+1} ({voice_err}). Trying next...")
                continue
                
        if response_obj:
            print(f"Successfully generated ElevenLabs TTS using voice {voice_id} with key ending in {api_key[-4:] if api_key else 'None'}")
            # Manually construct the dict to ensure stable JSON keys and avoid serialization issues
            return {
                "audio_base64": response_obj.audio_base_64,
                "alignment": {
                    "characters": response_obj.alignment.characters,
                    "character_start_times_seconds": response_obj.alignment.character_start_times_seconds,
                    "character_end_times_seconds": response_obj.alignment.character_end_times_seconds
                },
                "audio_format": "audio/mpeg"
            }
            
        print(f"All voices failed for API key {i+1}. Moving to next key...")
        
    return None