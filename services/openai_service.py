from openai import OpenAI
from config import Config

client = OpenAI(
    api_key=Config.AZURE_OPENAI_API_KEY,
    base_url=Config.AZURE_OPENAI_ENDPOINT,
)

SYSTEM_PROMPT = """You are ShopSense AI, an intelligent e-commerce product 
recommendation assistant helping general consumers find the right products.

Given a user query (from text, a voice transcript, or image analysis output), you must:
1. Clearly understand the user's intent, category, and budget
2. If budget or category is ambiguous, ask one concise clarifying question
3. Recommend exactly 3 products with the following structure for each:
   - Product name and brand
   - Estimated price range
   - 3 key features
   - Why it suits this specific user
4. End with a short follow-up question to refine further

Be conversational, specific, and helpful. Never recommend vague categories — 
always name real product types with concrete specifications."""


def get_recommendation(user_message: str, conversation_history: list[dict]) -> str:
    """
    Call Azure OpenAI GPT-4o-mini and return a product recommendation.

    Args:
        user_message: Processed input from any modality (text / voice / image)
        conversation_history: Previous turns as list of {role, content} dicts

    Returns:
        GPT-4o-mini response string
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=messages,
            max_tokens=800,
            temperature=0.7,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ Recommendation error: {str(e)}"