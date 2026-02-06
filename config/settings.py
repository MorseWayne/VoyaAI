"""
Application settings and configuration.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Configuration (OpenAI Compatible Proxy)
    llm_base_url: str = Field(
        default="http://127.0.0.1:8045/v1",
        description="OpenAI compatible API base URL"
    )
    llm_api_key: str = Field(
        default="",
        description="API key for the LLM service"
    )
    llm_model: str = Field(
        default="gemini-3-flash",
        description="Model name to use"
    )
    
    # MCP Services
    amap_mcp_url: str = Field(default="", description="Amap MCP URL")
    weather_mcp_url: str = Field(default="http://localhost:8083/sse", description="Weather MCP URL")
    xhs_cookie: str = Field(default="", description="Xiaohongshu Cookie")
    xhs_mcp_dir: str = Field(default="", description="Directory for jobsonlook-xhs-mcp")
    xhs_mcp_url: str = Field(default="http://192.168.31.121:18060/mcp", description="Xiaohongshu MCP Streamable HTTP URL")
    
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
