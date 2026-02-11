import json
import logging
from pathlib import Path
from typing import List, Optional
from api.models import Itinerary, Guide

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.plans_file = self.data_dir / "plans.json"
        self.guides_file = self.data_dir / "guides.json"
        self._ensure_files()

    def _ensure_files(self):
        for fpath in [self.plans_file, self.guides_file]:
            if not fpath.exists():
                with open(fpath, "w", encoding="utf-8") as f:
                    json.dump({}, f)

    def _load_json(self, file_path: Path) -> dict:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return {}

    def _save_json(self, file_path: Path, data: dict):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")

    # Plans
    def save_plan(self, plan: Itinerary) -> Itinerary:
        data = self._load_json(self.plans_file)
        plan_dict = json.loads(plan.model_dump_json())
        data[plan.id] = plan_dict
        self._save_json(self.plans_file, data)
        return plan

    def get_plan(self, plan_id: str) -> Optional[Itinerary]:
        data = self._load_json(self.plans_file)
        plan_data = data.get(plan_id)
        if plan_data:
            return Itinerary.model_validate(plan_data)
        return None

    def list_plans(self) -> List[Itinerary]:
        data = self._load_json(self.plans_file)
        return [Itinerary.model_validate(p) for p in data.values()]

    def delete_plan(self, plan_id: str) -> bool:
        data = self._load_json(self.plans_file)
        if plan_id in data:
            del data[plan_id]
            self._save_json(self.plans_file, data)
            return True
        return False

    # Guides
    def save_guide(self, guide: Guide) -> Guide:
        data = self._load_json(self.guides_file)
        guide_dict = json.loads(guide.model_dump_json())
        data[guide.id] = guide_dict
        self._save_json(self.guides_file, data)
        return guide

    def get_guide(self, guide_id: str) -> Optional[Guide]:
        data = self._load_json(self.guides_file)
        guide_data = data.get(guide_id)
        if guide_data:
            return Guide.model_validate(guide_data)
        return None

    def list_guides(self) -> List[Guide]:
        data = self._load_json(self.guides_file)
        return [Guide.model_validate(g) for g in data.values()]
    
    def delete_guide(self, guide_id: str) -> bool:
        data = self._load_json(self.guides_file)
        if guide_id in data:
            del data[guide_id]
            self._save_json(self.guides_file, data)
            return True
        return False
