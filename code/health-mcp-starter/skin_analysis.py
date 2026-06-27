"""
Skin photo preliminary analysis for VitaSide.
Local-first, ABCDE-inspired basic features + stub for external.
Strong disclaimers: NOT a diagnosis, not medical advice.
For awareness and to flag for professional review only.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import hashlib
import os

try:
    from PIL import Image
    import numpy as np
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    Image = None
    np = None

DISCLAIMER = (
    "Preliminary pattern matching only — NOT a medical diagnosis. "
    "This is not a substitute for professional dermatological evaluation. "
    "Always consult a doctor for any skin concerns. "
    "Images are processed locally unless you explicitly consent to external analysis."
)

def _compute_basic_features(img: Any) -> Dict[str, Any]:
    """Simple ABCDE-inspired metrics using PIL/numpy."""
    if not HAS_PIL or img is None:
        return {"error": "PIL not available", "features": {}}

    # Resize for speed
    img = img.resize((256, 256))
    arr = np.array(img.convert("RGB"))

    # Size (diameter proxy)
    width, height = img.size
    diameter_px = max(width, height)

    # Asymmetry: compare left/right halves (simple)
    left = arr[:, :arr.shape[1]//2]
    right = arr[:, arr.shape[1]//2:]
    right_flipped = right[:, ::-1]
    asymmetry = float(np.mean(np.abs(left.astype(float) - right_flipped.astype(float))))

    # Border irregularity: edge variance (crude)
    edges = np.abs(np.diff(arr, axis=1)).mean() + np.abs(np.diff(arr, axis=0)).mean()
    border_score = float(edges / 255.0)

    # Color: number of dominant colors + variance
    pixels = arr.reshape(-1, 3)
    unique_colors = len(np.unique(pixels, axis=0))
    color_variance = float(np.var(pixels))

    # Color diversity (more colors = higher for melanoma flag)
    color_diversity = min(1.0, unique_colors / 500.0)

    # Simple risk score (toy, 0-1)
    risk_score = (
        0.3 * min(1.0, asymmetry / 50) +
        0.25 * min(1.0, border_score) +
        0.25 * min(1.0, color_diversity) +
        0.2 * min(1.0, color_variance / 10000)
    )

    flags = []
    if asymmetry > 30:
        flags.append("asymmetry_notable")
    if border_score > 0.15:
        flags.append("border_irregular")
    if color_diversity > 0.6:
        flags.append("color_varied")
    if diameter_px > 200:  # rough, depends on photo scale
        flags.append("size_large")

    return {
        "diameter_px": diameter_px,
        "asymmetry": round(asymmetry, 1),
        "border_score": round(border_score, 3),
        "color_variety": unique_colors,
        "color_variance": round(color_variance, 1),
        "risk_score": round(risk_score, 3),
        "flags": flags,
    }

def analyze_skin_photo(
    image_path: str,
    user_consent: bool = False,
    use_external: bool = False,
    manifest: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Analyze skin photo locally with basic ABCDE features.
    If use_external and consent, would call external vision (stub for now).
    Returns features, preliminary flags, strong disclaimer.
    """
    if not user_consent:
        return {
            "error": "user_consent required",
            "disclaimer": DISCLAIMER,
        }

    path = Path(image_path)
    if not path.exists():
        return {"error": "image not found", "disclaimer": DISCLAIMER}

    # Basic local analysis
    local_features = {"available": False}
    if HAS_PIL:
        try:
            img = Image.open(path)
            local_features = _compute_basic_features(img)
        except Exception as e:
            local_features = {"error": str(e)}

    # Fingerprint for audit
    with open(path, "rb") as f:
        img_hash = hashlib.sha256(f.read()).hexdigest()[:16]

    result = {
        "image_fingerprint": img_hash,
        "local_analysis": local_features,
        "preliminary_flags": local_features.get("flags", []),
        "risk_score": local_features.get("risk_score", 0.0),
        "disclaimer": DISCLAIMER,
        "recommendation": "This is a toy preliminary analysis based on public ABCDE criteria. Consult a dermatologist for any concerns. Do not rely on this for decisions.",
    }

    if use_external:
        # Stub for external service (similar to azure)
        # In real: send minimized description or embedding to vision API
        result["external"] = {
            "status": "stub",
            "note": "External vision would be called here with consent. Example: possible atypical features noted. Full analysis requires doctor.",
            "would_send": ["image_hash", "basic_features", "consent_proof"],
        }
        result["recommendation"] += " External analysis requested but running in stub mode."

    # Audit
    result["audit"] = {
        "consent_given": user_consent,
        "external_requested": use_external,
    }

    return result
