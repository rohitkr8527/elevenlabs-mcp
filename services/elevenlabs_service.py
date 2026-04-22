from __future__ import annotations

import os
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
AUDIO_OUTPUT_DIR = Path(
    os.getenv("AUDIO_OUTPUT_DIR", str(PROJECT_ROOT / "outputs" / "audio"))
).resolve()
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


async def speak_with_style(
    text: str,
    style: str,
    file_name: str | None = None,
    auto_open: bool = True,
) -> dict:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY is missing. Add it to your .env file.")

    normalized_style = style.strip().lower()
    if normalized_style not in VOICE_PRESETS:
        available = ", ".join(VOICE_PRESETS.keys())
        raise RuntimeError(f"Unknown style '{style}'. Available styles: {available}")

    preset = VOICE_PRESETS[normalized_style]
    voice_id = preset["voice_id"]

    if not voice_id:
        raise RuntimeError(f"Voice ID for style '{normalized_style}' is missing in your .env file.")

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

    url = TTS_URL_TEMPLATE.format(voice_id=voice_id)

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        audio_bytes = response.content

    await anyio.Path(output_path).write_bytes(audio_bytes)

    opened = False
    if auto_open and AUTO_OPEN_AUDIO:
        opened = auto_open_file(output_path)

    return {
        "success": True,
        "message": "I generated the audio successfully and saved it locally. Opening it now."
        if opened
        else "I generated the audio successfully and saved it locally.",
        "file_path": str(output_path),
        "opened_automatically": opened,
        "style": normalized_style,
        "voice_label": preset["label"],
        "model_id": preset["model_id"],
    }