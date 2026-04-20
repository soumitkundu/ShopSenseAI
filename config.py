import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


class Config:
    # ── Azure OpenAI ──────────────────────────────────
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "shop-sense-openai-gpt-4o-mini")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-07-18")

    # ── Azure Speech ───────────────────────────────────
    AZURE_SPEECH_KEY: str = os.getenv("AZURE_SPEECH_KEY", "")
    AZURE_SPEECH_REGION: str = os.getenv("AZURE_SPEECH_REGION", "eastus")

    # ── Azure Computer Vision ──────────────────────────
    AZURE_VISION_KEY: str = os.getenv("AZURE_VISION_KEY", "")
    AZURE_VISION_ENDPOINT: str = os.getenv("AZURE_VISION_ENDPOINT", "")

    # ── Azure Language ─────────────────────────────────
    AZURE_LANGUAGE_KEY: str = os.getenv("AZURE_LANGUAGE_KEY", "")
    AZURE_LANGUAGE_ENDPOINT: str = os.getenv("AZURE_LANGUAGE_ENDPOINT", "")

    # ── App ────────────────────────────────────────────
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    @classmethod
    def validate(cls) -> None:
        """Raise clearly at startup if any critical key is missing."""
        required = {
            "AZURE_OPENAI_API_KEY": cls.AZURE_OPENAI_API_KEY,
            "AZURE_OPENAI_ENDPOINT": cls.AZURE_OPENAI_ENDPOINT,
            "AZURE_SPEECH_KEY": cls.AZURE_SPEECH_KEY,
            "AZURE_VISION_KEY": cls.AZURE_VISION_KEY,
            "AZURE_VISION_ENDPOINT": cls.AZURE_VISION_ENDPOINT,
            "AZURE_LANGUAGE_KEY": cls.AZURE_LANGUAGE_KEY,
            "AZURE_LANGUAGE_ENDPOINT": cls.AZURE_LANGUAGE_ENDPOINT,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise EnvironmentError(
                f"\n❌ Missing required environment variables:\n"
                + "\n".join(f"   - {k}" for k in missing)
                + "\n\nCheck your .env file."
            )
        print("✅ All Azure credentials loaded successfully.")