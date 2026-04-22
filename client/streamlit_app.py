import streamlit as st
from pathlib import Path

from mcp_client import MCPClient
from llm_service import generate_narration_text

PYTHON_PATH = r"C:\Users\rohit\elevenlabs-mcp\venv\Scripts\python.exe"
SERVER_SCRIPT = r"C:\Users\rohit\elevenlabs-mcp\server\mcp_app.py"
CWD = r"C:\Users\rohit\elevenlabs-mcp"


@st.cache_resource
def get_client():
    return MCPClient(PYTHON_PATH, SERVER_SCRIPT, CWD)


client = get_client()

st.title("LLM + ElevenLabs Voice Studio")

if st.button("Load Voice Styles"):
    try:
        result = client.call_tool("list_voice_styles", {})
        st.session_state["styles"] = [s["style"] for s in result.get("styles", [])]
        st.success("Loaded styles")
    except Exception as e:
        st.error(str(e))

styles = st.session_state.get(
    "styles",
    ["interviewer", "recruiter", "podcast", "narrator", "preview"],
)

prompt = st.text_area(
    "What should the LLM generate?",
    "Narrate the story of the thirsty crow in short.",
)

style = st.selectbox("Choose voice style", styles, index=3)
file_name = st.text_input("File name (optional)", "story_audio")

if st.button("Generate Text + Audio"):
    try:
        with st.spinner("Generating text with Groq..."):
            generated_text = generate_narration_text(prompt)

        st.subheader("Generated Text")
        st.write(generated_text)

        with st.spinner("Generating audio with MCP server..."):
            result = client.call_tool(
                "speak_with_style",
                {
                    "text": generated_text,
                    "style": style,
                    "file_name": file_name or None,
                    "auto_open": False,
                },
            )

        st.success(result.get("message", "Audio generated"))
        file_path = result.get("file_path", "")
        st.write("Saved at:", file_path)

        audio_file = Path(file_path)
        if audio_file.exists():
            with open(audio_file, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
        else:
            st.warning("Audio file not found")

    except Exception as e:
        st.error(str(e))