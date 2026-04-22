import streamlit as st
from pathlib import Path
import asyncio

from mcp_client import MCPClient
from llm_service import generate_narration_text

PYTHON_PATH = r"C:\Users\rohit\elevenlabs-mcp\venv\Scripts\python.exe"
SERVER_SCRIPT = r"C:\Users\rohit\elevenlabs-mcp\server\mcp_app.py"
CWD = r"C:\Users\rohit\elevenlabs-mcp"


@st.cache_resource
def get_client():
    return MCPClient(PYTHON_PATH, SERVER_SCRIPT, CWD)


client = get_client()

st.title("LLM + ElevenLabs Voice ")

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
    "Enter your prompt",
    "Explain Retreival Augmented Generation in Short"
)

style = st.selectbox("Choose style", styles, index=3)
file_name = st.text_input("File name (optional)", "generated_audio")

if st.button("Generate Text + Audio"):
    try:
        with st.spinner("Generating text with Groq..."):
            llm_output = generate_narration_text(prompt)

        st.subheader("Generated Text")
        st.write(llm_output)

        with st.spinner("Generating audio..."):
            result = client.call_tool(
                "speak_with_style",
                {
                    "text": llm_output,
                    "style": style,
                    "file_name": file_name or None,
                    "auto_open": False,
                },
            )

        st.subheader("Audio Result")
        st.success(result.get("message", "Audio generated successfully"))

        file_path = result.get("file_path", "")
        st.write("Saved at:", file_path)

        audio_file = Path(file_path)
        if audio_file.exists():
            with open(audio_file, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
        else:
            st.warning("Audio file not found.")

    except Exception as e:
        st.error(str(e))