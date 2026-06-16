from pydantic import Field
from pydantic_settings import BaseSettings


class AgentSettings(BaseSettings):
    enabled: bool = Field(alias="AGENT_ENABLED")

    max_tool_calls: int = Field(
        alias="AGENT_MAX_TOOL_CALLS"
    )

    allow_extraction_tools: bool = Field(
        alias="AGENT_ALLOW_EXTRACTION_TOOLS"
    )

    allow_document_tools: bool = Field(
        alias="AGENT_ALLOW_DOCUMENT_TOOLS"
    )

    allow_retrieval_tools: bool = Field(
        alias="AGENT_ALLOW_RETRIEVAL_TOOLS"
    )

    class Config:
        env_file = ".env"
        