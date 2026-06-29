import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from PIL import Image
import statistics

def get_image_stats(image_path: Path) -> Dict:
    """Extract basic visual stats from image using pure Pillow (no extra deps)."""
    try:
        img = Image.open(image_path).convert("RGB")
        w, h = img.size
        # Downsample for fast stats
        small = img.resize((64, 64))
        pixels = list(small.getdata())
        if not pixels:
            return {"brightness": 128, "width": w, "height": h, "dominant": "unknown"}
        
        rs = [p[0] for p in pixels]
        gs = [p[1] for p in pixels]
        bs = [p[2] for p in pixels]
        brightness = (sum(rs) + sum(gs) + sum(bs)) / (3 * len(pixels))
        
        # Simple dominant hue proxy
        avg_r, avg_g, avg_b = sum(rs)/len(rs), sum(gs)/len(gs), sum(bs)/len(bs)
        if avg_r > avg_g + 15 and avg_r > avg_b + 15:
            dominant = "warm/reddish (evening/indoor light)"
        elif avg_b > avg_r + 15 and avg_b > avg_g + 15:
            dominant = "cool/blueish (daylight or screen)"
        elif avg_g > avg_r and avg_g > avg_b:
            dominant = "greenish (plants/outdoor)"
        else:
            dominant = "neutral indoor"
        
        # Contrast proxy (std dev of brightness)
        pixel_brights = [(p[0]+p[1]+p[2])/3 for p in pixels]
        contrast = statistics.stdev(pixel_brights) if len(pixel_brights) > 1 else 20
        
        return {
            "brightness": round(brightness, 1),
            "width": w,
            "height": h,
            "dominant": dominant,
            "contrast": round(contrast, 1),
            "size_bytes": image_path.stat().st_size if image_path.exists() else 0
        }
    except Exception as e:
        return {"brightness": 110, "width": 512, "height": 512, "dominant": "unknown", "error": str(e)}

def analyze_lifestyle(image_path: Path, profile: Dict) -> Dict:
    """
    Real (heuristic) analysis of Frame photo for lifestyle patterns.
    Uses Pillow stats for brightness, dominant tone, contrast.
    No cloud / LLM required. Easy to swap for ollama/llava later.
    """
    ts = datetime.now().isoformat()
    stats = get_image_stats(image_path)
    b = stats["brightness"]
    dom = stats.get("dominant", "neutral indoor")
    contrast = stats.get("contrast", 25)
    
    # Dynamic heuristics from real image data
    if b > 155:
        description = f"Bright well-lit scene (b={b}). {dom}. Possible outdoor activity, window light or active area."
        tags = ["bright", "well_lit", "daytime_or_outdoor"]
        activity = "moderate_to_high_activity"
        location = "outdoor_or_bright_room"
        duration = "10-25min"
    elif b > 115:
        description = f"Moderately lit indoor scene (b={b}). {dom}. Typical home/work environment."
        tags = ["indoor", "moderate_light", "daily_routine"]
        activity = "low_to_moderate_activity"
        location = "indoor_home_or_work"
        duration = "15-40min"
    else:
        description = f"Dim / low-light scene (b={b}). {dom}. Evening, night or poorly lit space. Low movement."
        tags = ["dim", "low_light", "evening_or_night", "stationary"]
        activity = "low_activity"
        location = "indoor_dim"
        duration = "20-45min"
    
    # Add contrast-based nuance
    if contrast > 35:
        tags.append("high_contrast_detail")
        description += " High visual detail/variety."
    
    # Basic goal relevance (expandable)
    goals = profile.get("goals", [])
    goals_relevance = []
    for g in goals:
        g_lower = g.lower()
        if any(k in " ".join(tags).lower() for k in ["nutrition", "kitchen", "food", "eat"]) or "nutrition" in g_lower:
            goals_relevance.append(g)
        if any(k in " ".join(tags).lower() for k in ["activity", "outdoor", "bright", "movement"]) or "activity" in g_lower:
            goals_relevance.append(g)
    
    event = {
        "timestamp": ts,
        "image_path": str(image_path),
        "description": description,
        "lifestyle_tags": tags,
        "activity_level": activity,
        "location_type": location,
        "estimated_duration_min": duration,
        "patient_id": profile.get("patient_id"),
        "goals_relevance": list(set(goals_relevance)),
        "image_stats": stats
    }
    
    # Categories for aggregation
    categories = {
        "nutrition": any(x in " ".join(tags + [description.lower()]) for x in ["kitchen", "food", "eat", "nutrition"]),
        "physical_activity": "activity" in activity or "outdoor" in location or "bright" in " ".join(tags),
        "environment": "indoor" in location or "outdoor" in location,
        "habits": True,
        "low_light_routine": "dim" in " ".join(tags) or "low_light" in " ".join(tags)
    }
    event["categories"] = [cat for cat, active in categories.items() if active]
    
    return event
