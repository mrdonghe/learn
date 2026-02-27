import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class FeatureManager:
    FEATURE_FILE = "feature_list.json"

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.feature_file = project_path / self.FEATURE_FILE

    def load_features(self) -> List[Dict[str, Any]]:
        if not self.feature_file.exists():
            return []
        with open(self.feature_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_features(self, features: List[Dict[str, Any]]):
        os.makedirs(self.feature_file.parent, exist_ok=True)
        with open(self.feature_file, "w", encoding="utf-8") as f:
            json.dump(features, f, indent=2, ensure_ascii=False)

    def get_pending_features(self) -> List[Dict[str, Any]]:
        features = self.load_features()
        pending = [f for f in features if not f.get("passes", False)]
        priority_order = {"high": 0, "medium": 1, "low": 2}
        pending.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 1))
        return pending

    def get_feature_by_id(self, feature_id: str) -> Optional[Dict[str, Any]]:
        features = self.load_features()
        for f in features:
            if f.get("id") == feature_id:
                return f
        return None

    def mark_feature_complete(self, feature_id: str):
        features = self.load_features()
        for f in features:
            if f.get("id") == feature_id:
                f["passes"] = True
                break
        self.save_features(features)

    def get_completed_count(self) -> int:
        features = self.load_features()
        return sum(1 for f in features if f.get("passes", False))

    def get_total_count(self) -> int:
        return len(self.load_features())

    def are_dependencies_met(self, feature: Dict[str, Any]) -> bool:
        deps = feature.get("dependencies", [])
        if not deps:
            return True
        features = self.load_features()
        completed_ids = {f["id"] for f in features if f.get("passes", False)}
        return all(dep in completed_ids for dep in deps)
