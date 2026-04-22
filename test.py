import os
from dotenv import load_dotenv
import httpx

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = "21m00Tcm4TlvDq8ikWAM"

url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

headers = {
    "xi-api-key": api_key,
    "Content-Type": "application/json",
    "Accept": "audio/mpeg",
}
payload = {
    "text": "Once there was a crow.",
    "model_id": "eleven_multilingual_v2",
    "output_format": "mp3_44100_128",
    "voice_settings": {"stability": 0.60, "similarity_boost": 0.70},
}

r = httpx.post(url, headers=headers, json=payload, timeout=120)
print(r.status_code)
print(r.text[:500])