from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from enum import Enum

class WeatherCondition(str, Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    SNOW = "snow"
    STORM = "storm"

class TerrainType(str, Enum):
    FLAT = "flat"
    HILLY = "hilly"
    MOUNTAINOUS = "mountainous"
    URBAN = "urban"
    HIGHWAY = "highway"

class RouteOptimizationRequest(BaseModel):
    origin: str
    destination: str
    battery_soc: float  # Current state of charge (0-100%)
    battery_soh: float = 90.0  # State of health (0-100%)
    vehicle_efficiency: float = 0.2  # kWh per km
    user_id: Optional[str] = None
    preferences: Optional[Dict] = {}

class WeatherData(BaseModel):
    location: str
    temperature: float
    humidity: float
    wind_speed: float
    wind_direction: float
    condition: WeatherCondition
    timestamp: datetime

class ElevationPoint(BaseModel):
    lat: float
    lon: float
    elevation: float
    distance_from_start: float

class RouteSegment(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    distance_km: float
    terrain_type: TerrainType
    elevation_change: float
    estimated_energy_consumption: float
    confidence_score: float

class RouteOptimizationResponse(BaseModel):
    route_id: str
    origin: str
    destination: str
    total_distance_km: float
    estimated_duration_minutes: float
    estimated_energy_consumption_kwh: float
    estimated_range_remaining_km: float
    confidence_score: float
    route_polyline: str  # Encoded polyline
    segments: List[RouteSegment]
    elevation_profile: List[ElevationPoint]
    weather_conditions: List[WeatherData]
    recommended_charging_stops: List[str] = []
    warnings: List[str] = []
    created_at: datetime

class RangeAnalysisRequest(BaseModel):
    battery_soc: float
    battery_soh: float
    route_distance_km: float
    terrain_data: List[Dict]
    weather_data: Optional[Dict] = None
    vehicle_efficiency: float = 0.2

class RangeAnalysisResponse(BaseModel):
    predicted_range_km: float
    confidence_interval: Tuple[float, float]  # Min, Max range
    energy_consumption_breakdown: Dict[str, float]
    range_factors: Dict[str, float]  # Factor impacts on range
    recommendations: List[str]

class TerrainAnalysisRequest(BaseModel):
    route_points: List[Tuple[float, float]]  # (lat, lon) pairs

class TerrainAnalysisResponse(BaseModel):
    elevation_profile: List[ElevationPoint]
    total_elevation_gain: float
    total_elevation_loss: float
    max_grade: float
    avg_grade: float
    terrain_difficulty_score: float  # 0-10 scale

class OptimizationMetrics(BaseModel):
    standard_prediction_accuracy: float
    ml_enhanced_accuracy: float
    energy_saving_percentage: float
    route_optimization_improvement: float
    user_satisfaction_score: float
