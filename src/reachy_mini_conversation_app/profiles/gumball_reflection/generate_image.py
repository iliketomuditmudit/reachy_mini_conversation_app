"""Custom tool: generate an image from a DALL-E prompt and display/save it."""
import logging
import os
from typing import Any, Dict

from openai import AsyncOpenAI

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies

logger = logging.getLogger(__name__)


class GenerateImage(Tool):
    """Generate an image via DALL-E from a prompt derived from the conversation."""

    name = "generate_image"
    description = (
        "Generate an image using DALL-E based on a vivid scene prompt "
        "derived from the visitor's reflection. Call this ONLY once, at the "
        "very end of the coaching session, after delivering your closing reflection."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": (
                    "A vivid, specific DALL-E image prompt that captures the visitor's "
                    "memory, feeling, mood, lighting, setting, and emotion."
                ),
            },
        },
        "required": ["prompt"],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> Dict[str, Any]:
        """Call DALL-E to generate an image, save it locally, and return its path."""
        prompt = (kwargs.get("prompt") or "").strip()
        if not prompt:
            return {"error": "prompt must be a non-empty string"}

        logger.info("Tool call: generate_image prompt=%s", prompt[:120])

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {"error": "OPENAI_API_KEY not set"}

        client = AsyncOpenAI(api_key=api_key)

        try:
            response = await client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
                quality="standard",
                response_format="url",
            )
        except Exception as e:
            logger.exception("DALL-E API call failed: %s", e)
            return {"error": f"DALL-E API error: {e}"}

        image_url = response.data[0].url
        revised_prompt = getattr(response.data[0], "revised_prompt", prompt)
        logger.info("Image generated: %s", image_url)

        # ------------------------------------------------------------------
        # Optionally download and save the image locally next to this file
        # ------------------------------------------------------------------
        save_path: str | None = None
        try:
            import httpx
            import time

            output_dir = os.path.join(os.path.dirname(__file__), "generated_images")
            os.makedirs(output_dir, exist_ok=True)
            filename = f"reflection_{int(time.time())}.png"
            save_path = os.path.join(output_dir, filename)

            async with httpx.AsyncClient(timeout=30) as http:
                img_response = await http.get(image_url)
                img_response.raise_for_status()
                with open(save_path, "wb") as f:
                    f.write(img_response.content)

            logger.info("Image saved to: %s", save_path)
        except ImportError:
            logger.warning("httpx not installed — image not saved locally (pip install httpx)")
        except Exception as e:
            logger.warning("Could not save image locally: %s", e)

        return {
            "status": "generated",
            "image_url": image_url,
            "revised_prompt": revised_prompt,
            "saved_path": save_path,
        }
