from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime

class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool = True
    message: str = "Success"
    data: Optional[Any] = None
    timestamp: datetime = datetime.utcnow()

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error_code: str
    message: str
    details: Optional[Dict] = None
    timestamp: datetime = datetime.utcnow()

class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    success: bool = True
    data: List[Any]
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool

class AnalyticsResponse(BaseModel):
    """Dashboard analytics response"""
    total_batteries: int
    active_stations: int
    daily_swaps: int
    average_health_score: float
    energy_saved_kwh: float
    carbon_reduced_kg: float
    health_distribution: Dict[str, int]  # Status: count
    station_utilization: Dict[str, float]  # Station: utilization
    performance_metrics: Dict[str, float]
    trends: Dict[str, List[float]]  # Metric: daily values

class SystemStatusResponse(BaseModel):
    """System health status"""
    status: str  # healthy, degraded, critical
    uptime_seconds: int
    database_status: str
    cache_status: str
    api_status: Dict[str, str]  # Service: status
    last_updated: datetime
    active_users: int
    requests_per_minute: float

class BulkOperationResponse(BaseModel):
    """Bulk operation results"""
    total_processed: int
    successful_operations: int
    failed_operations: int
    errors: List[Dict[str, str]] = []
    processing_time_seconds: float

class ReportResponse(BaseModel):
    """Generated report response"""
    report_id: str
    title: str
    generated_at: datetime
    data: Dict[str, Any]
    charts: List[Dict[str, Any]] = []
    summary: Dict[str, Any]
    recommendations: List[str] = []

class ConfigurationResponse(BaseModel):
    """Application configuration"""
    version: str
    environment: str
    features_enabled: List[str]
    api_limits: Dict[str, int]
    maintenance_window: Optional[Dict[str, str]] = None
    supported_languages: List[str] = ["en", "es", "fr", "de", "zh"]
