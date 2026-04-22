from services.elevenlabs_service import list_voice_styles, speak_with_style
from server.schemas import SpeakWithStyleInput


def list_voice_styles_tool() -> dict:
    return list_voice_styles()


async def speak_with_style_tool(arguments: dict) -> dict:
    payload = SpeakWithStyleInput(**arguments)
    return await speak_with_style(
        text=payload.text,
        style=payload.style,
        file_name=payload.file_name,
        auto_open=payload.auto_open,
    )