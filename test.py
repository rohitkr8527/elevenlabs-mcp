import asyncio
from dotenv import load_dotenv

load_dotenv()

from services.elevenlabs_service import list_voice_styles, speak_with_style


async def main():
    print("Available styles:")
    print(list_voice_styles())

    result = await speak_with_style(
        text="Retrieval augmented generation combines pre-existing knowledge from a large database with user input to produce more accurate and informative responses, rather than solely relying on generated text.",
        style="interviewer",
        file_name="direct_test",
        auto_open=True,
    )

    print("\nResult:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())