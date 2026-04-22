# ElevenLabs MCP Demo Project

## Overview
This is a **demo project** showcasing how to build an end-to-end voice generation system using modern AI tools and APIs.

It converts natural language prompts into narrated audio through a modular pipeline:
- **Groq LLM** → generates narration text  
- **MCP Server** → exposes tool `speak_with_style`  
- **ElevenLabs API** → generates high-quality audio  
- **Streamlit UI** → provides an interactive interface  

---

##  Demo Flow
User Prompt → Groq LLM → Generated Text → MCP Tool Call → ElevenLabs → Audio Output

---

## Key Features
- 🔹 Demonstrates **MCP (Model Context Protocol)** integration  
- 🔹 Fast LLM inference using **Groq**  
- 🔹 Multiple voice styles (interviewer, narrator, etc.)  
- 🔹 Async backend for better performance  
- 🔹 Simple and interactive **Streamlit UI**  
- 🔹 **Fallback TTS (Edge TTS)** to ensure uninterrupted demo  

---

## Purpose of This Demo
This project is designed to demonstrate:
- How LLMs can interact with external tools using MCP  
- Integration of AI models with real-world APIs  
- Building reliable systems with fallback mechanisms  
- Modular architecture for scalable AI applications  

---

##  Note
ElevenLabs free tier restricts API usage for certain voices.  
To ensure a smooth demo experience:

The system automatically falls back to **Edge TTS** if ElevenLabs fails.

---

## How to Run
```bash
venv\Scripts\python.exe -m streamlit run client/streamlit_app.py