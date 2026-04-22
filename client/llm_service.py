from pathlib import Path
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def get_llm() -> ChatGroq:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing in .env")
    return ChatGroq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=0.7,
    )


def generate_narration_text(user_prompt: str) -> str:
    llm = get_llm()

    messages = [
        SystemMessage(
            content=(
                "You are a helpful narration assistant. "
                "Generate short, clear, natural text suitable for text-to-speech narration. "
                "Keep it concise and smooth to listen to."
            )
        ),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    return response.content.strip()