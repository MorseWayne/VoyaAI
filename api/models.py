from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class TransportMode(str, Enum):
    FLIGHT = "flight"
    TRAIN = "train"
    DRIVING = "driving"
    CYCLING = "cycling"
    WALKING = "walking"
    TRANSIT = "transit"

class Location(BaseModel):
    name: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    departure_time: Optional[str] = None  # ISO format YYYY-MM-DD HH:MM
    arrival_time: Optional[str] = None    # ISO format YYYY-MM-DD HH:MM

class Segment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: TransportMode
    origin: Location
    destination: Location
    distance_km: Optional[float] = None
    duration_minutes: Optional[float] = None
    cost_estimate: Optional[float] = None
    currency: str = "CNY"
    details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    # details can contain: flight_no, train_no, seat_type, etc.

class DayPlan(BaseModel):
    day_index: int
    date: Optional[str] = None  # YYYY-MM-DD
    city: Optional[str] = None
    segments: List[Segment] = Field(default_factory=list)
    start_time_hm: Optional[str] = None  # 当日出发时间，如 "08:00"
    location_stay_minutes: Optional[List[int]] = None  # 各地点停留分钟数，长度 = len(segments)+1

class Itinerary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    days: List[DayPlan] = Field(default_factory=list)
    start_location: Optional[Location] = None  # 创建行程时设置的起点
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
