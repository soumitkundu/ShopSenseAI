from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from config import Config

_client = TextAnalyticsClient(
    endpoint=Config.AZURE_LANGUAGE_ENDPOINT,
    credential=AzureKeyCredential(Config.AZURE_LANGUAGE_KEY),
)


def extract_key_phrases(text: str) -> list[str]:
    """
    Extract key phrases from user text to surface product attributes,
    budget hints, and category signals before sending to GPT-4o-mini.
    e.g. "wireless headphones under 2000 rupees" → ["wireless headphones", "2000 rupees"]
    """
    try:
        response = _client.extract_key_phrases(
            documents=[{"id": "1", "language": "en", "text": text}]
        )
        result = response[0]
        if not result.is_error:
            return result.key_phrases
        return []
    except Exception as e:
        print(f"[language_service] Key phrase error: {e}")
        return []


def detect_sentiment(text: str) -> str:
    """
    Detect user sentiment to adapt the bot's tone.
    Returns: 'positive', 'neutral', or 'negative'
    """
    try:
        response = _client.analyze_sentiment(
            documents=[{"id": "1", "language": "en", "text": text}]
        )
        result = response[0]
        if not result.is_error:
            return result.sentiment
        return "neutral"
    except Exception as e:
        print(f"[language_service] Sentiment error: {e}")
        return "neutral"


def enrich_prompt(user_text: str) -> str:
    """
    Append extracted key phrases to the raw user message so GPT-4o-mini
    has explicit signal about product requirements and budget.
    Falls back to raw text if the Language service fails.
    """
    phrases = extract_key_phrases(user_text)
    if phrases:
        return (
            f"{user_text}\n"
            f"[Detected requirements: {', '.join(phrases)}]"
        )
    return user_text