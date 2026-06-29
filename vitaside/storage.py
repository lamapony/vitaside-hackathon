import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class LocalStore:
    """Local-first storage for lifestyle events. Privacy focused.
    Can export to Notion/Supabase via MCPs in the platform.
    """

    def __init__(self, base_dir: Path = Path("~/vitaside/data").expanduser()):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.events_file = self.base_dir / "lifestyle_events.jsonl"
        self.patterns_file = self.base_dir / "patterns.json"

    def add_event(self, event: Dict):
        with open(self.events_file, "a") as f:
            f.write(json.dumps(event) + "\n")
        print(f"[Storage] Event logged: {event.get('lifestyle_tags')}")

    def get_events(self, limit: int = 100) -> List[Dict]:
        if not self.events_file.exists():
            return []
        events = []
        with open(self.events_file) as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
        return events[-limit:]

    def compute_patterns(self) -> Dict:
        events = self.get_events()
        if not events:
            return {"summary": "No data yet"}

        # Simple aggregation (latest approach: can use agentic summarization)
        tag_counts = {}
        activity_levels = {}
        locations = {}
        for e in events:
            for tag in e.get("lifestyle_tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            lvl = e.get("activity_level", "unknown")
            activity_levels[lvl] = activity_levels.get(lvl, 0) + 1
            loc = e.get("location_type", "unknown")
            locations[loc] = locations.get(loc, 0) + 1

        total = len(events)
        top_tags = sorted(tag_counts.items(), key=lambda x: -x[1])[:5]

        # Dynamic recommendation based on data
        rec = "Review collected lifestyle events for doctor visit."
        if any("low_activity" in str(e.get("activity_level", "")) or "stationary" in str(e.get("lifestyle_tags", [])) for e in events):
            rec = "Frequent low-activity / stationary periods detected. Consider suggesting more movement or outdoor time aligned with goals."
        if any("bright" in str(e.get("lifestyle_tags", [])) or "outdoor" in str(e.get("location_type", "")) for e in events):
            rec = "Good mix of bright/outdoor captures noted. Continue monitoring for balance with indoor routines."

        patterns = {
            "total_captures": total,
            "top_tags": top_tags,
            "activity_distribution": activity_levels,
            "location_distribution": locations,
            "goals_alignment": "Data shows patterns relevant to goals from patient profile.",
            "last_updated": datetime.now().isoformat(),
            "recommendation_for_doctor": rec
        }
        self.patterns_file.write_text(json.dumps(patterns, indent=2))
        return patterns

    def export_for_doctor(self) -> Path:
        """Prepare summary for doctor visit prep."""
        patterns = self.compute_patterns()
        summary_path = self.base_dir / f"doctor_summary_{datetime.now().strftime('%Y%m%d')}.json"
        summary_path.write_text(json.dumps({
            "patient_summary": patterns,
            "raw_events_count": len(self.get_events()),
            "note": "Local-first. Share only approved data."
        }, indent=2))
        return summary_path
