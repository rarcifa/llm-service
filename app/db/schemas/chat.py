from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    input: str = Field(
        ...,
        description="The user's input prompt.",
        example="What's the weather like today?",
    )
    session_id: str | None = Field(
        None, description="Optional session ID for conversation continuity."
    )
