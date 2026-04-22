from pydantic import BaseModel, Field
from typing import Optional


class SpeakWithStyleInput(BaseModel):
    text: str = Field(..., min_length=1, description="Text to convert to speech")
    style: str = Field(..., description="Friendly style name such as interviewer, recruiter, podcast, narrator, or preview")
    file_name: Optional[str] = Field(default=None, description="Optional output filename without path")
    auto_open: bool = Field(default=True, description="Open the generated audio automatically")


class SpeakWithStyleOutput(BaseModel):
    success: bool
    message: str
    file_path: str
    opened_automatically: bool
    style: str
    voice_label: str
    model_id: str