"""
Pydantic settings for PDF OCR Pipeline.
BaseSettings to load API key, model, prompt, DPI, and language.
"""
from pydantic import BaseSettings, Field, SecretStr


class Settings(BaseSettings):
    # OpenAI API key (supports SecretStr hiding)
    api_key: SecretStr = Field(..., env="OPENAI_API_KEY")

    # Model name for OpenAI
    model: str = Field("gpt-4o", description="Name of the OpenAI model to use")

    # Default prompt for AI summarization
    prompt: str = Field(
        "Extract and summarize the key information from this OCR text. "
        "Include names, dates, locations, and main topics. "
        "If there are tables, extract their data in a structured format.",
        description="Prompt text for AI analysis",
    )

    # OCR defaults
    dpi: int = Field(600, description="Default resolution for OCR (DPI)")
    lang: str = Field("eng", description="Default Tesseract language code")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instantiate global settings
settings = Settings()
