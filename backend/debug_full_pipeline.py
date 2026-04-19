# File: backend/debug_full_pipeline.py
# Run: py debug_full_pipeline.py

import os
import json
import urllib.request
from dotenv import load_dotenv
load_dotenv()

# Add backend/ to path so service imports work
import sys
sys.path.insert(0, os.path.dirname(__file__))

from services.language_service import enrich_prompt
from services.openai_service import get_recommendation
from services.vision_service import analyse_image_bytes

print("═" * 55)
print("  ShopSense AI — Full Pipeline Debug")
print("═" * 55)

# ── Pipeline 1: Text ────────────────────────────────────────────────
print("\n[1] TEXT PIPELINE")
raw_text = "I need a smartwatch under Rs. 3000 with heart rate monitor"
print(f"Input   : {raw_text}")

enriched = enrich_prompt(raw_text)
print(f"Enriched: {enriched}")

recommendation = get_recommendation(enriched, [])
print(f"\nGPT-4 Response:\n{recommendation}")

# ── Pipeline 2: Image → Vision → GPT-4 ─────────────────────────────
print("\n" + "─" * 55)
print("[2] IMAGE PIPELINE")
image_url = "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800"
print(f"Image URL: {image_url}")

with urllib.request.urlopen(image_url) as r:
    image_bytes = r.read()

vision_prompt = analyse_image_bytes(image_bytes)
print(f"Vision summary: {vision_prompt}")

recommendation2 = get_recommendation(vision_prompt, [])
print(f"\nGPT-4 Response:\n{recommendation2}")

print("\n" + "═" * 55)
print("✅ Full pipeline debug complete.")