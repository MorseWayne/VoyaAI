import json
import logging
from pathlib import Path
from typing import List, Optional
from api.models import Itinerary

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.file_path = self.data_dir / "plans.json"
        self._ensure_file()

    def _ensure_file(self):
        if not self.file_path.exists():
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load_data(self) -> dict:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading plans: {e}")
            return {}

    def _save_data(self, data: dict):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving plans: {e}")

    def save_plan(self, plan: Itinerary) -> Itinerary:
        data = self._load_data()
        # Convert pydantic model to dict, handling datetime serialization if needed
        # model_dump_json -> json.loads is a safe way to get basic types
        plan_dict = json.loads(plan.model_dump_json())
        data[plan.id] = plan_dict
        self._save_data(data)
        return plan

    def get_plan(self, plan_id: str) -> Optional[Itinerary]:
        data = self._load_data()
        plan_data = data.get(plan_id)
        if plan_data:
            return Itinerary.model_validate(plan_data)
        return None

    def list_plans(self) -> List[Itinerary]:
        data = self._load_data()
        return [Itinerary.model_validate(p) for p in data.values()]

    def delete_plan(self, plan_id: str) -> bool:
        data = self._load_data()
        if plan_id in data:
            del data[plan_id]
            self._save_data(data)
            return True
        return False
