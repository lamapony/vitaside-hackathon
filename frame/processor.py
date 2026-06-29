from __future__ import annotations
import asyncio
from typing import Any, Dict

# This is a STUB.
# Replace the implementation with a real local vision model for VitaSide.
#
# Recommended options (local-first):
# - Ollama + Llava / Moondream
# - Apple MLX or CoreML
# - HuggingFace transformers (quantized)
# - Your existing vision pipeline

async def process_photo(image_bytes: bytes) -> Dict[str, Any]:
    """
    Analyze a photo and return structured lifestyle data.

    Returns something like:
    {
        "caption": "Patient is preparing food in the kitchen",
        "activities": ["cooking", "standing"],
        "location_hint": "kitchen",
        "confidence": 0.82,
        "tags": ["indoor", "food_prep"]
    }
    """
    # TODO: plug real model here
    # For now return a placeholder so the pipeline works end-to-end.

    # Fake analysis based on filename/time would be better in real code,
    # but we simulate a call.
    await asyncio.sleep(0.1)  # simulate model inference time

    return {
        "caption": "Patient appears to be in an indoor environment, possibly kitchen or living area.",
        "activities": ["indoor_activity", "standing"],
        "location_hint": "indoor",
        "confidence": 0.65,
        "model": "stub-vision-v1",
        "raw_length": len(image_bytes),
    }


# Example of how you would call a real model (Ollama example):
#
# import ollama
# async def process_photo(image_bytes: bytes):
#     response = await ollama.async_generate(
#         model='llava',
#         prompt='Describe what the person is doing in this photo in one sentence. Also list 2-3 activities.',
#         images=[image_bytes],
#     )
#     # parse response.text ...
#     return {"caption": ..., "activities": ...}
