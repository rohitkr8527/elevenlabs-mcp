from __future__ import annotations

import os
import edge_tts
import platform
import subprocess
from datetime import datetime
from pathlib import Path

import anyio
import httpx
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

from server.presets import VOICE_PRESETS

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
AUDIO_OUTPUT_DIR = Path(os.getenv("AUDIO_OUTPUT_DIR", str(PROJECT_ROOT / "outputs" / "audio"))).resolve()
AUTO_OPEN_AUDIO = os.getenv("AUTO_OPEN_AUDIO", "true").lower() == "true"
TTS_URL_TEMPLATE = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


def ensure_output_dir() -> None:
    AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_filename(name: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in name.strip())
    return cleaned.strip("_") or "audio"


def build_output_path(file_name: str | None, style: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = sanitize_filename(file_name) if file_name else f"{style}_{timestamp}"
    if not base.endswith(".mp3"):
        base = f"{base}.mp3"
    return (AUDIO_OUTPUT_DIR / base).resolve()


def auto_open_file(file_path: Path) -> bool:
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(str(file_path))  # type: ignore[attr-defined]
        elif system == "Darwin":
            subprocess.Popen(["open", str(file_path)])
        else:
            subprocess.Popen(["xdg-open", str(file_path)])
        return True
    except Exception:
        return False


def list_voice_styles() -> dict:
    styles = []
    for style_name, preset in VOICE_PRESETS.items():
        styles.append(
            {
                "style": style_name,
                "label": preset["label"],
                "description": preset["description"],
                "model_id": preset["model_id"],
            }
        )
    return {"styles": styles}



async def edge_fallback_tts(text: str, output_path: Path):
    communicate = edge_tts.Communicate(text=text, voice="en-US-AriaNeural")
    await communicate.save(str(output_path))


async def speak_with_style(text: str,style: str,file_name: str | None = None,auto_open: bool = True,) -> dict:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY is missing.")

    normalized_style = style.strip().lower()
    preset = VOICE_PRESETS.get(normalized_style)

    ensure_output_dir()
    output_path = build_output_path(file_name, normalized_style)

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    payload = {
        "text": text,
        "model_id": preset["model_id"],
        "output_format": "mp3_44100_128",
        "voice_settings": preset["voice_settings"],
    }

    url = TTS_URL_TEMPLATE.format(voice_id=preset["voice_id"])

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=payload)

            if response.status_code == 402:
                raise RuntimeError("ElevenLabs quota/voice restriction")

            response.raise_for_status()
            audio_bytes = response.content

        await anyio.Path(output_path).write_bytes(audio_bytes)

        engine = "elevenlabs"

    except Exception:
      
        await edge_fallback_tts(text, output_path)
        engine = "edge-tts"

    opened = False
    if auto_open and AUTO_OPEN_AUDIO:
        opened = auto_open_file(output_path)

    return {
        "success": True,
        "message": f"Audio generated using {engine}",
        "file_path": str(output_path),
        "engine": engine,
    }