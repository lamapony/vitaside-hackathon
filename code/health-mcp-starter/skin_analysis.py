"""
Skin photo ABCDE observation tool for VitaSide.

Local-first, ABCDE-inspired *descriptive* feature extraction. This is explicitly
NOT a risk score, NOT a diagnosis, and NOT medical advice. It only describes
geometric/colour properties of the image so the user can discuss them with a
dermatologist. No "risk", no "flags", no "mole/melanoma" language, no thresholds
that imply likelihood of disease.

Images are processed locally unless the user explicitly consents to external
analysis (currently a stub).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import os

try:
    from PIL import Image, UnidentifiedImageError
    import numpy as np
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    Image = None
    np = None
    UnidentifiedImageError = Exception  # type: ignore[assignment,misc]

DISCLAIMER = (
    "This tool describes basic image features (ABCDE-inspired) only. "
    "It is NOT a medical diagnosis, NOT a risk score, and NOT a substitute for "
    "professional dermatological evaluation. Always consult a doctor for any "
    "skin concerns. Images are processed locally unless you explicitly consent "
    "to external analysis."
)

PHOTO_GUIDE: List[str] = [
    "Use bright, diffuse, natural lighting (avoid harsh shadows and flash).",
    "Photograph the spot straight-on, filling most of the frame.",
    "Place a ruler or coin next to the spot for size reference.",
    "Keep the camera steady and in focus; avoid motion blur.",
    "Use the same lighting and distance if you take comparison photos over time.",
]

# Conservative guard rails for the local toy feature extractor.
_MIN_IMAGE_DIM = 64        # px — smaller images are too low-res to describe
_MAX_IMAGE_DIM = 4096      # px — reject very large images to bound memory/time
_MAX_FILE_BYTES = 15 * 1024 * 1024  # 15 MB upload guard


def _validate_image(path: Path) -> Dict[str, Any]:
    """Check the file is a readable image of reasonable size before processing."""
    if not path.exists():
        return {"ok": False, "reason": "image not found"}
    size = path.stat().st_size
    if size == 0:
        return {"ok": False, "reason": "image file is empty"}
    if size > _MAX_FILE_BYTES:
        return {"ok": False, "reason": f"image exceeds {_MAX_FILE_BYTES // (1024*1024)} MB limit"}
    if not HAS_PIL:
        return {"ok": False, "reason": "Pillow (PIL) not installed — run pip install -r requirements.txt"}
    try:
        with Image.open(path) as probe:
            probe.verify()
    except UnidentifiedImageError:
        return {"ok": False, "reason": "file is not a valid or supported image"}
    except Exception as exc:  # noqa: BLE001 — surface any decode failure to the caller
        return {"ok": False, "reason": f"image decode failed: {exc}"}
    return {"ok": True}


def _describe_abcde(img: Any) -> Dict[str, Any]:
    """Descriptive ABCDE-inspired features. No score, no risk, no flags."""
    width, height = img.size
    # Downscale for stable, fast description.
    img = img.resize((256, 256))
    arr = np.array(img.convert("RGB"))

    # Diameter proxy (raw pixels; depends on photo scale — explicitly noted).
    diameter_px = max(width, height)

    # Asymmetry: mean left/right mirror difference (0..255 scale).
    left = arr[:, : arr.shape[1] // 2]
    right = arr[:, arr.shape[1] // 2 :]
    right_flipped = right[:, ::-1]
    asymmetry = float(np.mean(np.abs(left.astype(float) - right_flipped.astype(float))))

    # Border: crude edge contrast (0..1).
    edges = np.abs(np.diff(arr, axis=1)).mean() + np.abs(np.diff(arr, axis=0)).mean()
    border_contrast = float(edges / 255.0)

    # Colour: number of distinct colours + variance (descriptive only).
    pixels = arr.reshape(-1, 3)
    unique_colors = int(len(np.unique(pixels, axis=0)))
    color_variance = float(np.var(pixels))

    observations: List[str] = []
    if asymmetry > 40:
        observations.append("Left/right halves look noticeably different.")
    else:
        observations.append("Left/right halves look roughly similar.")
    if border_contrast > 0.15:
        observations.append("Edges show relatively high contrast with the surroundings.")
    if unique_colors > 300:
        observations.append("A wide range of colours is present in the region.")
    if diameter_px > 2000:
        observations.append("The subject occupies a large part of the frame — include a size reference for scale.")
    observations.append("Evolution (change over time) cannot be assessed from a single photo.")

    return {
        "diameter_px": diameter_px,
        "diameter_note": "Pixel size depends on photo zoom/distance — use a ruler for real-world size.",
        "asymmetry": round(asymmetry, 1),
        "asymmetry_scale": "0..255 mean mirror difference",
        "border_contrast": round(border_contrast, 3),
        "border_scale": "0..1 edge contrast",
        "distinct_colors": unique_colors,
        "color_variance": round(color_variance, 1),
        "observations": observations,
    }


def analyze_skin_photo(
    image_path: str,
    user_consent: bool = False,
    use_external: bool = False,
    manifest: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Describe basic ABCDE-inspired features of a skin photo locally.

    Returns descriptive observations + a strong disclaimer. Never returns a
    risk score, probability, or diagnostic flag. Requires explicit user_consent.
    External vision is an explicit-consent stub.
    """
    if not user_consent:
        return {
            "error": "user_consent required",
            "disclaimer": DISCLAIMER,
            "photo_guide": PHOTO_GUIDE,
        }

    path = Path(image_path)
    quality = _validate_image(path)
    if not quality.get("ok"):
        return {
            "error": quality.get("reason", "image not acceptable"),
            "disclaimer": DISCLAIMER,
            "photo_guide": PHOTO_GUIDE,
        }

    # Fingerprint for audit (no raw image leaves the machine in local mode).
    with open(path, "rb") as f:
        img_hash = hashlib.sha256(f.read()).hexdigest()[:16]

    abcde: Dict[str, Any]
    if HAS_PIL:
        try:
            with Image.open(path) as img:
                if img.width < _MIN_IMAGE_DIM or img.height < _MIN_IMAGE_DIM:
                    return {
                        "error": f"image too small (min {_MIN_IMAGE_DIM}px on each side)",
                        "disclaimer": DISCLAIMER,
                        "photo_guide": PHOTO_GUIDE,
                        "image_fingerprint": img_hash,
                    }
                if img.width > _MAX_IMAGE_DIM or img.height > _MAX_IMAGE_DIM:
                    return {
                        "error": f"image too large (max {_MAX_IMAGE_DIM}px on each side)",
                        "disclaimer": DISCLAIMER,
                        "photo_guide": PHOTO_GUIDE,
                        "image_fingerprint": img_hash,
                    }
                abcde = _describe_abcde(img)
        except Exception as exc:  # noqa: BLE001
            return {
                "error": f"image processing failed: {exc}",
                "disclaimer": DISCLAIMER,
                "photo_guide": PHOTO_GUIDE,
                "image_fingerprint": img_hash,
            }
    else:
        abcde = {"error": "Pillow (PIL) not installed"}

    result: Dict[str, Any] = {
        "image_fingerprint": img_hash,
        "image_quality": quality,
        "abcde_observations": abcde,
        "observations": abcde.get("observations", []),
        "disclaimer": DISCLAIMER,
        "photo_guide": PHOTO_GUIDE,
        "recommendation": (
            "Descriptive image features only — not a diagnosis or risk score. "
            "Discuss any skin concerns with a dermatologist."
        ),
    }

    if use_external:
        # Stub for external service (similar to azure). In real use, a minimized
        # description/embedding would be sent only with explicit consent.
        result["external"] = {
            "status": "stub",
            "note": "External vision would be called here only with explicit consent. Not active.",
            "would_send": ["image_hash", "abcde_features", "consent_proof"],
        }
        result["recommendation"] += " External analysis requested but running in stub mode."

    result["audit"] = {
        "consent_given": user_consent,
        "external_requested": use_external,
    }

    return result
