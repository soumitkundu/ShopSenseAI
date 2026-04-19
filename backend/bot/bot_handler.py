from services.openai_service import get_recommendation
from services.language_service import enrich_prompt
from services.vision_service import analyse_image_bytes
from services.speech_service import speech_to_text_from_file


class ShopSenseBot:
    """
    Stateless bot logic class.
    Receives structured input from the FastAPI router and returns a response.
    Session history is managed externally (in app.py) and passed in per request.
    """

    async def handle_text(
        self,
        user_text: str,
        conversation_history: list[dict],
    ) -> str:
        """Process a plain text message through Language enrichment → GPT-4o-mini."""
        enriched = enrich_prompt(user_text)
        return get_recommendation(enriched, conversation_history)

    async def handle_voice(
        self,
        audio_bytes: bytes,
        conversation_history: list[dict],
    ) -> dict:
        """
        Transcribe voice input → enrich → GPT-4o-mini.
        Returns both transcript and recommendation so the frontend
        can show the user what was understood.
        """
        transcript = speech_to_text_from_file(audio_bytes)
        enriched = enrich_prompt(transcript)
        recommendation = get_recommendation(enriched, conversation_history)
        return {"transcript": transcript, "recommendation": recommendation}

    async def handle_image(
        self,
        image_bytes: bytes,
        conversation_history: list[dict],
    ) -> dict:
        """
        Analyse product image → build vision prompt → GPT-4o-mini.
        Returns both the vision analysis and the recommendation.
        """
        vision_prompt = analyse_image_bytes(image_bytes)
        recommendation = get_recommendation(vision_prompt, conversation_history)
        return {"vision_summary": vision_prompt, "recommendation": recommendation}