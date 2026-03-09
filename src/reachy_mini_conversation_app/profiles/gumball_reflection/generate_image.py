"""Custom tool: generate a coloring-book image via Gemini and display/save it."""
import base64
import logging
import os
import random
import time
from typing import Any, Dict

from google import genai
from google.genai import types

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies

# Dances that look good during a ~10-20 s wait (calming / dreamy feel)
_GENERATION_DANCES = [
    "groovy_sway_and_roll",
    "pendulum_swing",
    "dizzy_spin",
    "interwoven_spirals",
    "side_to_side_sway",
]

logger = logging.getLogger(__name__)


class GenerateImage(Tool):
    """Generate a coloring-book image via Gemini from a scene description."""

    name = "generate_image"
    description = (
        "Generate a coloring-book image using Gemini based on a scene description "
        "derived from the visitor's reflection. Call this ONLY once, at the "
        "very end of the coaching session, after delivering your closing reflection."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": (
                    "Describe only the SCENE CONTENT: who is in the image (person description), "
                    "what they are doing, and the simple setting (2-3 objects max). "
                    "Do NOT include any style words -- the tool automatically applies "
                    "the coloring book style. Example: "
                    "'A bearded man in a striped shirt running through a field with two dogs and a big sun.'"
                ),
            },
        },
        "required": ["prompt"],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> Dict[str, Any]:
        """Call Gemini to generate a coloring-book image, save it, and return its data URI."""
        prompt = (kwargs.get("prompt") or "").strip()
        if not prompt:
            return {"error": "prompt must be a non-empty string"}

        # Prepend mandatory coloring book style prefix so the model's scene
        # description is always rendered as a printable coloring page.
        style_prefix = (
            "Children's coloring book page. Thick bold black outlines only. "
            "Pure white background. No color, no shading, no gradients, no texture. "
            "Maximum 6 large simple objects. Simple circle eyes and curved line smile for faces. "
            "Flat 2D line art. No numbers, no letters, no words, no labels, no text of any kind anywhere in the image. "
            "Scene: "
        )
        full_prompt = style_prefix + prompt
        logger.info("Tool call: generate_image scene=%s", prompt[:120])
        logger.debug("Full Gemini prompt: %s", full_prompt[:300])

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {"error": "GEMINI_API_KEY (or GOOGLE_API_KEY) not set"}

        # While Gemini churns (~10-20 s), make Reachy dance so the visitor
        # has something fun to watch instead of silence.
        try:
            from reachy_mini_dances_library.collection.dance import AVAILABLE_MOVES
            from reachy_mini_conversation_app.dance_emotion_moves import DanceQueueMove

            dance_name = random.choice(
                [d for d in _GENERATION_DANCES if d in AVAILABLE_MOVES] or list(AVAILABLE_MOVES.keys())
            )
            # Queue the move twice so it fills the typical wait window
            for _ in range(2):
                deps.movement_manager.queue_move(DanceQueueMove(dance_name))
            logger.info("Queued generation dance: %s x2", dance_name)
        except Exception as dance_err:
            logger.warning("Could not queue generation dance: %s", dance_err)

        client = genai.Client(api_key=api_key)

        try:
            response = await client.aio.models.generate_content(
                model="gemini-3.1-flash-image-preview",
                contents=[full_prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )
        except Exception as e:
            logger.exception("Gemini API call failed: %s", e)
            return {"error": f"Gemini API error: {e}"}

        # Extract the first image part from the response
        image_bytes: bytes | None = None
        mime_type = "image/png"
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or "image/png"
                break

        if image_bytes is None:
            logger.error("Gemini returned no image part. Full response: %s", response)
            return {"error": "Gemini returned no image in the response"}

        logger.info("Image generated (%d bytes, %s)", len(image_bytes), mime_type)

        # Save locally next to this file
        save_path: str | None = None
        try:
            output_dir = os.path.join(os.path.dirname(__file__), "generated_images")
            os.makedirs(output_dir, exist_ok=True)
            ext = mime_type.split("/")[-1].split(";")[0]  # e.g. "png" from "image/png"
            filename = f"reflection_{int(time.time())}.{ext}"
            save_path = os.path.join(output_dir, filename)
            with open(save_path, "wb") as f:
                f.write(image_bytes)
            logger.info("Image saved to: %s", save_path)
        except Exception as e:
            logger.warning("Could not save image locally: %s", e)

        # Build a data URI so the TV display (browser) can render it directly
        # without needing to serve the local file over HTTP.
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_uri = f"data:{mime_type};base64,{b64}"

        return {
            "status": "generated",
            "image_url": data_uri,
            "saved_path": save_path,
        }
