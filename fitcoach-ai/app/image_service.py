"""Image generation and Cloud Storage publishing service for FitCoach AI."""

import re
import time
from typing import Any

from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-03-5c6554ad3943"
BUCKET_NAME = "fitcoach-ai-assets-5c6554ad3943"
IMAGE_MODEL = "gemini-3.1-flash-lite-image"
LOCATION = "global"

_genai_client = None
_storage_client = None


def get_genai_client() -> genai.Client:
    """Lazy initialize GenAI client for global region."""
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    return _genai_client


def get_storage_client() -> storage.Client:
    """Lazy initialize Storage client."""
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=PROJECT_ID)
    return _storage_client


MODERN_FLAT_STYLE_MODIFIER = (
    "modern flat design style, clean minimalist vector illustration, "
    "vibrant contemporary colors, smooth gradients, crisp outlines, "
    "sleek geometric aesthetics, high quality digital graphic, isolated on clean background"
)


async def generate_fitness_image(
    prompt: str,
    image_name: str = "fitness_visual",
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Generate a modern, flat-style fitness visual, milestone badge, or post-workout meal image using Gemini image generation.

    The image is saved as a session artifact and uploaded to public Cloud Storage.

    Args:
        prompt: Detailed visual prompt describing the fitness image in modern flat design (e.g. 'Modern flat vector milestone badge for completing 50 workouts with minimalist laurel wreath and barbell icon, vibrant teal and gold accents', 'Sleek modern flat illustration of a colorful high-protein bowl with grilled chicken, avocado, and quinoa, clean minimalist graphic').
        image_name: Short identifier or name for the image file (e.g. 'gold_workout_badge', 'post_workout_meal').
        tool_context: Context supplied automatically by ADK for saving artifacts.

    Returns:
        A dictionary with the public image URL, filename, and confirmation status.
    """
    client = get_genai_client()

    # Enhance prompt with modern flat style guidance
    styled_prompt = f"{prompt.strip()}, {MODERN_FLAT_STYLE_MODIFIER}"

    try:
        response = await client.aio.models.generate_content(
            model=IMAGE_MODEL,
            contents=styled_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )
    except Exception as e:
        return {"error": f"Failed to generate image with {IMAGE_MODEL}: {str(e)}"}

    if not response.candidates or not response.candidates[0].content.parts:
        return {"error": "Image model did not return any image candidates."}

    # Find the image part in response
    image_bytes = None
    mime_type = "image/jpeg"
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            image_bytes = part.inline_data.data
            mime_type = part.inline_data.mime_type or "image/jpeg"
            break

    if not image_bytes:
        return {"error": "No image data found in candidate parts."}

    # Clean filename
    clean_stem = re.sub(r"[^a-zA-Z0-9_-]", "_", image_name).strip("_") or "fitness_image"
    ext = "png" if "png" in mime_type.lower() else "jpg"
    artifact_filename = f"{clean_stem}.{ext}"
    timestamp = int(time.time())
    gcs_object_name = f"images/{clean_stem}_{timestamp}.{ext}"

    # 1. Save artifact to Playground via tool_context if available
    if tool_context is not None:
        try:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            await tool_context.save_artifact(filename=artifact_filename, artifact=artifact_part)
        except Exception as e:
            # Non-fatal if context save fails
            print(f"Warning: tool_context.save_artifact failed: {e}")

    # 2. Upload to Cloud Storage bucket and return public URL
    try:
        storage_client = get_storage_client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(gcs_object_name)
        blob.upload_from_string(image_bytes, content_type=mime_type)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{gcs_object_name}"
    except Exception as e:
        return {"error": f"Failed to upload image to Cloud Storage bucket {BUCKET_NAME}: {str(e)}"}

    return {
        "status": "success",
        "image_url": public_url,
        "filename": artifact_filename,
        "mime_type": mime_type,
        "message": f"Image generated successfully and available at {public_url}",
    }
