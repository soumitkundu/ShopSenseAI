# File: backend/debug_vision.py
# Run: py debug_vision.py

import os
import urllib.request
from dotenv import load_dotenv
load_dotenv()

from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

client = ImageAnalysisClient(
    endpoint=os.getenv("AZURE_VISION_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_VISION_KEY")),
)

print("Endpoint:", os.getenv("AZURE_VISION_ENDPOINT"))
print()

# Use a real product image (public URL — a pair of sneakers)
TEST_IMAGE_URL = "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800"

# ── Test 1: Analyse from URL ────────────────────────────────────────
print("── Analyse from URL ───────────────────────────")
try:
    result = client.analyze_from_url(
        image_url=TEST_IMAGE_URL,
        visual_features=[
            VisualFeatures.CAPTION,
            VisualFeatures.DENSE_CAPTIONS,
            VisualFeatures.TAGS,
            VisualFeatures.OBJECTS,
        ],
    )

    if result.caption:
        print(f"Caption : {result.caption.text} "
              f"(confidence: {result.caption.confidence:.2f})")

    if result.dense_captions:
        print("Dense captions:")
        for cap in result.dense_captions.list[:3]:
            print(f"  - {cap.text} (conf: {cap.confidence:.2f})")

    if result.tags:
        top_tags = [t.name for t in result.tags.list if t.confidence > 0.75]
        print(f"Tags    : {', '.join(top_tags)}")

    if result.objects:
        objects = [o.tags[0].name for o in result.objects.list]
        print(f"Objects : {', '.join(set(objects))}")

    print("✅ Vision URL analysis working correctly.")

except Exception as e:
    print(f"❌ Vision URL error: {e}")

print()

# ── Test 2: Analyse from bytes (simulates file upload) ─────────────
print("── Analyse from bytes (file upload simulation) ─")
try:
    # Download image to bytes
    with urllib.request.urlopen(TEST_IMAGE_URL) as r:
        image_bytes = r.read()

    print(f"Downloaded {len(image_bytes) / 1024:.1f} KB")

    result2 = client.analyze(
        image_data=image_bytes,
        visual_features=[VisualFeatures.CAPTION, VisualFeatures.TAGS],
    )

    if result2.caption:
        print(f"Caption : {result2.caption.text}")

    if result2.tags:
        top_tags = [t.name for t in result2.tags.list if t.confidence > 0.75]
        print(f"Tags    : {', '.join(top_tags)}")

    print("✅ Vision bytes analysis working correctly.")

except Exception as e:
    print(f"❌ Vision bytes error: {e}")