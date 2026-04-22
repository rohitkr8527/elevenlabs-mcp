from pathlib import Path
from dotenv import load_dotenv
import os

# FORCE load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

def get_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"{key} is missing from .env")
    return value

VOICE_PRESETS = {
    "interviewer": {
        "label": "Confident Interviewer",
        "voice_id": get_env("ELEVENLABS_INTERVIEWER_VOICE_ID"),
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.55, "similarity_boost": 0.75},
        "description": "Professional, focused",
    },
    "recruiter": {
        "label": "Warm Recruiter",
        "voice_id": get_env("ELEVENLABS_RECRUITER_VOICE_ID"),
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.50, "similarity_boost": 0.75},
        "description": "Friendly HR tone",
    },
    "podcast": {
        "label": "Podcast Host",
        "voice_id": get_env("ELEVENLABS_PODCAST_VOICE_ID"),
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.80},
        "description": "Energetic",
    },
    "narrator": {
        "label": "Calm Narrator",
        "voice_id": get_env("ELEVENLABS_NARRATOR_VOICE_ID"),
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.60, "similarity_boost": 0.70},
        "description": "Clear explanation",
    },
    "preview": {
        "label": "Fast Preview",
        "voice_id": get_env("ELEVENLABS_INTERVIEWER_VOICE_ID"),
        "model_id": "eleven_flash_v2_5",
        "voice_settings": {"stability": 0.50, "similarity_boost": 0.70},
        "description": "Low latency",
    },
}