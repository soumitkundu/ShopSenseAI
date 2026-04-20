from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from config import Config

_client = ImageAnalysisClient(
    endpoint=Config.AZURE_VISION_ENDPOINT,
    credential=AzureKeyCredential(Config.AZURE_VISION_KEY),
)

# VisualFeatures.COLOR does not exist in azure-ai-vision-imageanalysis v1.0.0
# Valid features: CAPTION, DENSE_CAPTIONS, TAGS, OBJECTS, PEOPLE, READ, SMART_CROPS
_FEATURES = [
    VisualFeatures.CAPTION,
    VisualFeatures.DENSE_CAPTIONS,
    VisualFeatures.TAGS,
    VisualFeatures.OBJECTS,
]


def analyse_image_bytes(image_bytes: bytes) -> str:
    """
    Analyse raw image bytes uploaded by the user.
    Returns a structured natural-language description for the GPT-4 prompt.
    """
    try:
        result = _client.analyze(image_data=image_bytes, visual_features=_FEATURES)
        return _build_description(result)
    except Exception as e:
        return f"Image analysis failed: {str(e)}"


def analyse_image_url(image_url: str) -> str:
    """
    Analyse a product image from a public URL.
    """
    try:
        result = _client.analyze_from_url(
            image_url=image_url, visual_features=_FEATURES
        )
        return _build_description(result)
    except Exception as e:
        return f"Image analysis failed: {str(e)}"


def _build_description(result) -> str:
    """
    Convert raw Azure Vision result into a GPT-4o-mini friendly prompt segment.
    Only includes fields with confident results.
    """
    parts = []

    # Primary caption — overall image description
    if result.caption and result.caption.confidence > 0.5:
        parts.append(f"Image shows: {result.caption.text}")

    # Dense captions — detailed descriptions of individual regions
    # Gives richer product attribute detail than the removed COLOR feature
    if result.dense_captions:
        top_captions = [
            c.text
            for c in result.dense_captions.list[:3]  # top 3 region captions
            if c.confidence > 0.6
        ]
        if top_captions:
            parts.append(f"Detailed attributes: {'; '.join(top_captions)}")

    # Tags — product keywords with confidence filter
    if result.tags:
        confident_tags = [
            t.name for t in result.tags.list if t.confidence > 0.75
        ]
        if confident_tags:
            parts.append(f"Product tags: {', '.join(confident_tags)}")

    # Detected objects — physical items in the image
    if result.objects:
        object_names = list({o.tags[0].name for o in result.objects.list})
        if object_names:
            parts.append(f"Detected items: {', '.join(object_names)}")

    if not parts:
        return (
            "The user uploaded a product image but no clear attributes were detected. "
            "Please ask the user to describe what they are looking for."
        )

    summary = " | ".join(parts)
    return (
        f"The user uploaded a product image for reference. "
        f"Analysis: {summary}. "
        f"Please recommend similar products based on these visual attributes."
    )