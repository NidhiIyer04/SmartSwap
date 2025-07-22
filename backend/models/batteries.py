from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class BatteryStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"

class SwapRecommendation(str, Enum):
    RECOMMENDED = "recommended"
    CAUTION = "caution"
    NOT_RECOMMENDED = "not_recommended"

class BatteryHealth(BaseModel):
    soc: float  # State of Charge (0-100%)
    soh: float  # State of Health (0-100%)
    voltage: float
    current: float
    temperature: float
    cycle_count: int
    capacity_remaining: float
    internal_resistance: float

class BatteryMetrics(BaseModel):
    health: BatteryHealth
    status: BatteryStatus
    swap_recommendation: SwapRecommendation
    confidence_score: float
    predicted_range_km: float
    estimated_life_remaining_days: int

class Battery(BaseModel):
    battery_id: str
    station_id: str
    manufacturer: str
    model: str
    chemistry: str = "LiFePO4"
    capacity_kwh: float
    manufacturing_date: datetime
    first_use_date: Optional[datetime] = None
    current_location: Optional[str] = None
    metrics: BatteryMetrics
    maintenance_history: List[Dict] = []
    created_at: datetime
    updated_at: datetime

class BatteryCreate(BaseModel):
    battery_id: str
    station_id: str
    manufacturer: str
    model: str
    chemistry: str = "LiFePO4"
    capacity_kwh: float
    manufacturing_date: datetime

class BatteryUpdate(BaseModel):
    station_id: Optional[str] = None
    current_location: Optional[str] = None
    metrics: Optional[BatteryMetrics] = None

class HealthPredictionRequest(BaseModel):
    battery_id: str
    prediction_days: int = 7

class HealthPredictionResponse(BaseModel):
    battery_id: str
    current_health: BatteryHealth
    predictions: List[Dict]  # Daily predictions
    confidence: float
    recommendations: List[str]

class SwapRequest(BaseModel):
    old_battery_id: str
    new_battery_id: str
    station_id: str
    user_id: str
    requested_at: datetime

class SwapResponse(BaseModel):
    swap_id: str
    recommendation: SwapRecommendation
    old_battery_health: float
    new_battery_health: float
    estimated_range_improvement: float
    confidence_score: float
    warnings: List[str] = []

class CircularEconomyMetrics(BaseModel):
    total_batteries: int
    active_batteries: int
    batteries_in_second_life: int
    batteries_recycled: int
    material_recovery_rate: Dict[str, float]  # Material: recovery percentage
    carbon_footprint_saved_kg: float
    energy_recovery_efficiency: float
