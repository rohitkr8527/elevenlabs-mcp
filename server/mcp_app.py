import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp.server.fastmcp import FastMCP
from server.tools import list_voice_styles_tool, speak_with_style_tool

mcp = FastMCP("Claude ElevenLabs Voice Studio")


@mcp.tool(name="list_voice_styles",description="List the available friendly voice styles for ElevenLabs speech generation.",)
def list_voice_styles():
    return list_voice_styles_tool()


@mcp.tool(
    name="speak_with_style",
    description="""
Generate speech from text using one of these styles:
- interviewer: confident, technical, neutral
- recruiter: warm, friendly, HR tone
- podcast: energetic, expressive
- narrator: calm, explanatory
- preview: fast low-latency preview

Save the audio locally and auto-open it.
""",
)
async def speak_with_style(text: str,style: str,file_name: str | None = None,auto_open: bool = True,):
    return await speak_with_style_tool(
        {
            "text": text,
            "style": style,
            "file_name": file_name,
            "auto_open": auto_open,
        }
    )


if __name__ == "__main__":
    print("Starting ElevenLabs MCP server...", file=sys.stderr)
    mcp.run()