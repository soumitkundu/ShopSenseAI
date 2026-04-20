# File: backend/debug_language.py
# Run: py debug_language.py

import os
from dotenv import load_dotenv
load_dotenv()

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

client = TextAnalyticsClient(
    endpoint=os.getenv("AZURE_LANGUAGE_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_LANGUAGE_KEY")),
)

print("Endpoint:", os.getenv("AZURE_LANGUAGE_ENDPOINT"))
print()

test_texts = [
    "I need wireless noise cancelling headphones under 3000 rupees",
    "Looking for a smartwatch with heart rate monitor and GPS",
    "I want running shoes size 10 for marathon training",
]

try:
    # Test 1: Key phrase extraction
    print("── Key Phrase Extraction ──────────────────────")
    response = client.extract_key_phrases(
        documents=[{"id": str(i), "language": "en", "text": t}
                   for i, t in enumerate(test_texts)]
    )
    for i, result in enumerate(response):
        if not result.is_error:
            print(f"Input : {test_texts[i]}")
            print(f"Phrases: {result.key_phrases}")
        else:
            print(f"❌ Error on doc {i}: {result.error}")
        print()

    # Test 2: Sentiment detection
    print("── Sentiment Detection ────────────────────────")
    response = client.analyze_sentiment(
        documents=[{"id": str(i), "language": "en", "text": t}
                   for i, t in enumerate(test_texts)]
    )
    for i, result in enumerate(response):
        if not result.is_error:
            print(f"Input    : {test_texts[i]}")
            print(f"Sentiment: {result.sentiment} "
                  f"(pos={result.confidence_scores.positive:.2f}, "
                  f"neu={result.confidence_scores.neutral:.2f}, "
                  f"neg={result.confidence_scores.negative:.2f})")
        else:
            print(f"❌ Error on doc {i}: {result.error}")
        print()

    print("✅ Language Service working correctly.")

except Exception as e:
    print(f"❌ Language Service error: {e}")