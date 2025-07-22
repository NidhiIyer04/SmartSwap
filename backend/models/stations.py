from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from enum import Enum

class StationStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    PLANNED = "planned"

class StationType(str, Enum):
    URBAN = "urban"
    HIGHWAY = "highway"
    RURAL = "rural"
    COMMERCIAL = "commercial"

class Location(BaseModel):
    lat: float
    lon: float
    address: str
    city: str
    state: str
    country: str
    postal_code: Optional[str] = None

class StationCapacity(BaseModel):
    total_slots: int
    available_slots: int
    charging_slots: int
    maintenance_slots: int
    battery_inventory: int
    healthy_batteries: int
    degraded_batteries: int

class OperationalMetrics(BaseModel):
    daily_swaps: int
    monthly_swaps: int
    average_swap_time_seconds: float
    utilization_rate: float  # 0-1
    customer_satisfaction: float  # 0-5
    uptime_percentage: float
    energy_consumption_kwh: float
    carbon_footprint_kg: float

class Station(BaseModel):
    station_id: str
    name: str
    location: Location
    station_type: StationType
    status: StationStatus
    capacity: StationCapacity
    metrics: OperationalMetrics
    amenities: List[str] = []  # WiFi, restrooms, cafe, etc.
    operating_hours: Dict[str, str] = {}  # Day: hours
    contact_info: Optional[Dict] = {}
    created_at: datetime
    updated_at: datetime

class StationCreate(BaseModel):
    station_id: str
    name: str
    location: Location
    station_type: StationType
    total_slots: int

class StationUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[StationStatus] = None
    capacity: Optional[StationCapacity] = None
    amenities: Optional[List[str]] = None
    operating_hours: Optional[Dict[str, str]] = None

class StationSearch(BaseModel):
    lat: float
    lon: float
    radius_km: float = 10.0
    station_type: Optional[StationType] = None
    min_available_slots: int = 1

class StationSearchResult(BaseModel):
    station: Station
    distance_km: float
    estimated_travel_time_minutes: float
    availability_score: float  # 0-1
    current_wait_time_minutes: Optional[float] = None

class StationAnalytics(BaseModel):
    station_id: str
    performance_metrics: OperationalMetrics
    demand_forecast: Dict[str, float]  # Hour: predicted demand
    optimization_recommendations: List[str]
    roi_metrics: Dict[str, float]

class StationPlacementRequest(BaseModel):
    region_bounds: List[Tuple[float, float]]  # [(lat, lon), ...]
    target_coverage_km: float = 50.0
    min_stations: int = 1
    max_stations: int = 10
    population_data: Optional[Dict] = None
    traffic_data: Optional[Dict] = None

class StationPlacementResponse(BaseModel):
    recommended_locations: List[Location]
    coverage_analysis: Dict[str, float]
    demand_predictions: List[float]
    investment_requirements: List[float]
    roi_projections: List[float]
    optimization_score: float

class GridIntegration(BaseModel):
    renewable_energy_percentage: float
    grid_stability_score: float  # 0-10
    peak_load_management: bool
    v2g_capability: bool
    carbon_intensity: float  # kg CO2/kWh
