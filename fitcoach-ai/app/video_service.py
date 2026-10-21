"""Video generation and Cloud Storage publishing service for FitCoach AI using Google Omni model."""

import base64
import re
import time
from typing import Any

from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-03-5c6554ad3943"
BUCKET_NAME = "fitcoach-ai-assets-5c6554ad3943"
VIDEO_MODEL = "gemini-omni-flash-preview"
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


async def generate_exercise_video(
    prompt: str,
    video_name: str = "exercise_form_demo",
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Generate a short video demonstration or visual form cue for an exercise or fitness movement using Gemini Omni (gemini-omni-flash-preview).

    The video is saved as a session artifact and uploaded to public Cloud Storage.

    Args:
        prompt: Detailed description of the exercise motion, form cues, camera angle, and movement tempo (e.g. 'A clear 5-second video demonstrating proper bodyweight squat form with straight back, neutral spine, knees tracking over toes, smooth continuous movement.').
        video_name: Short identifier or name for the video file (e.g. 'squat_form_demo', 'pushup_technique').
        tool_context: Context supplied automatically by ADK for saving artifacts.

    Returns:
        A dictionary with the public video URL, filename, and status confirmation.
    """
    client = get_genai_client()

    try:
        # gemini-omni-flash-preview is called via the Interactions API
        interaction = await client.aio.interactions.create(
            model=VIDEO_MODEL,
            input=prompt.strip(),
        )
    except Exception as e:
        return {"error": f"Failed to generate video with {VIDEO_MODEL}: {str(e)}"}

    if not hasattr(interaction, "output_video") or not interaction.output_video:
        return {"error": "Video model interaction completed but did not return output_video."}

    raw_data = interaction.output_video.data
    if not raw_data:
        return {"error": "output_video contained empty data."}

    if isinstance(raw_data, str):
        video_bytes = base64.b64decode(raw_data)
    elif isinstance(raw_data, bytes):
        video_bytes = raw_data
    else:
        return {"error": f"Unexpected video data format: {type(raw_data)}"}

    # File naming
    clean_stem = re.sub(r"[^a-zA-Z0-9_-]", "_", video_name).strip("_") or "exercise_video"
    artifact_filename = f"{clean_stem}.mp4"
    timestamp = int(time.time())
    gcs_object_name = f"videos/{clean_stem}_{timestamp}.mp4"
    mime_type = "video/mp4"

    # 1. Save artifact to Playground via tool_context if available
    if tool_context is not None:
        try:
            artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
            await tool_context.save_artifact(filename=artifact_filename, artifact=artifact_part)
        except Exception as e:
            # Non-fatal if tool_context artifact save fails
            print(f"Warning: tool_context.save_artifact failed: {e}")

    # 2. Upload to Cloud Storage bucket and return public URL
    try:
        storage_client = get_storage_client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(gcs_object_name)
        blob.upload_from_string(video_bytes, content_type=mime_type)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{gcs_object_name}"
    except Exception as e:
        return {"error": f"Failed to upload video to Cloud Storage bucket {BUCKET_NAME}: {str(e)}"}

    return {
        "status": "success",
        "video_url": public_url,
        "filename": artifact_filename,
        "mime_type": mime_type,
        "message": f"Video generated successfully and available at {public_url}",
    }
