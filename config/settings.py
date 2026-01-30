"""
Application settings and configuration.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Configuration
    llm_provider: Literal["anthropic", "openai", "google"] = Field(
        default="anthropic",
        description="LLM provider to use"
    )
    
    # Anthropic
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", description="Anthropic model name")
    
    # OpenAI
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model name")
    
    # Google
    google_api_key: str = Field(default="", description="Google API key")
    google_model: str = Field(default="gemini-2.0-flash", description="Google model name")
    
    # MCP Services
    amap_mcp_url: str = Field(default="", description="Amap MCP SSE URL")
    weather_mcp_url: str = Field(default="http://localhost:8083/sse", description="Weather MCP URL")
    xhs_smithery_key: str = Field(default="", description="Xiaohongshu Smithery key")
    xhs_profile: str = Field(default="", description="Xiaohongshu profile ID")
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8182, description="Server port")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
