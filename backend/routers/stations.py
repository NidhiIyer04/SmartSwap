from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Tuple, Optional, Union
import logging
from datetime import datetime, timedelta

from models.users import User
from models.stations import (
    Station, StationCreate, StationUpdate, StationSearch, StationSearchResult,
    StationAnalytics, StationPlacementRequest, StationPlacementResponse,
    Location, StationCapacity, OperationalMetrics, StationStatus, StationType,
    GridIntegration
)
from models.responses import APIResponse
from services.auth_service import get_current_user, require_operator, require_admin
from services.ml_service import ml_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[Station])
async def get_stations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    station_type: Optional[StationType] = None,
    status: Optional[StationStatus] = None,
    city: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get list of stations with optional filters"""
    try:
        # Mock data for now - would query database in production
        stations = await get_mock_stations()

        # Apply filters
        filtered_stations = stations
        if station_type:
            filtered_stations = [s for s in filtered_stations if s.station_type == station_type]
        if status:
            filtered_stations = [s for s in filtered_stations if s.status == status]
        if city:
            filtered_stations = [s for s in filtered_stations if s.location.city.lower() == city.lower()]

        # Apply pagination
        paginated_stations = filtered_stations[skip:skip+limit]

        logger.info(f"Retrieved {len(paginated_stations)} stations for user {current_user.username}")
        return paginated_stations

    except Exception as e:
        logger.error(f"Error retrieving stations: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving stations")

@router.get("/{station_id}", response_model=Station)
async def get_station(
    station_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific station details"""
    try:
        station = await get_mock_station(station_id)

        if not station:
            raise HTTPException(status_code=404, detail="Station not found")

        return station

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving station {station_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving station")

@router.post("/", response_model=APIResponse)
async def create_station(
    station_data: StationCreate,
    current_user: User = Depends(require_admin)
):
    """Create new station"""
    try:
        # Create station document with default values
        station = Station(
            station_id=station_data.station_id,
            name=station_data.name,
            location=station_data.location,
            station_type=station_data.station_type,
            status=StationStatus.PLANNED,
            capacity=StationCapacity(
                total_slots=station_data.total_slots,
                available_slots=station_data.total_slots,
                charging_slots=int(station_data.total_slots * 0.3),
                maintenance_slots=2,
                battery_inventory=station_data.total_slots,
                healthy_batteries=station_data.total_slots,
                degraded_batteries=0
            ),
            metrics=OperationalMetrics(
                daily_swaps=0,
                monthly_swaps=0,
                average_swap_time_seconds=120.0,
                utilization_rate=0.0,
                customer_satisfaction=5.0,
                uptime_percentage=100.0,
                energy_consumption_kwh=0.0,
                carbon_footprint_kg=0.0
            ),
            amenities=[],
            operating_hours={},
            contact_info={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # In production, save to database
        # await db.stations.insert_one(station.dict())

        logger.info(f"Station {station_data.station_id} created by {current_user.username}")

        return APIResponse(
            success=True,
            message="Station created successfully",
            data={"station_id": station_data.station_id}
        )

    except Exception as e:
        logger.error(f"Error creating station: {e}")
        raise HTTPException(status_code=500, detail="Error creating station")

@router.put("/{station_id}", response_model=APIResponse)
async def update_station(
    station_id: str,
    station_data: StationUpdate,
    current_user: User = Depends(require_operator)
):
    """Update station information"""
    try:
        # Check if station exists
        station = await get_mock_station(station_id)
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")

        # In production, update database
        # update_data = {k: v for k, v in station_data.dict().items() if v is not None}
        # await db.stations.update_one({"station_id": station_id}, {"$set": update_data})

        logger.info(f"Station {station_id} updated by {current_user.username}")

        return APIResponse(
            success=True,
            message="Station updated successfully"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating station {station_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating station")

@router.post("/search", response_model=List[StationSearchResult])
async def search_nearby_stations(
    search: StationSearch,
    current_user: User = Depends(get_current_user)
):
    """Search for nearby stations"""
    try:
        stations = await get_mock_stations()

        results = []
        for station in stations:
            # Calculate distance (simplified haversine formula)
            lat_diff = abs(station.location.lat - search.lat)
            lon_diff = abs(station.location.lon - search.lon)
            distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111  # Rough km conversion

            # Apply filters
            if distance > search.radius_km:
                continue
            if search.station_type and station.station_type != search.station_type:
                continue
            if station.capacity.available_slots < search.min_available_slots:
                continue

            # Calculate availability score
            availability_score = station.capacity.available_slots / station.capacity.total_slots

            # Estimate travel time (rough: 50 km/h average)
            travel_time = distance / 50 * 60  # minutes

            result = StationSearchResult(
                station=station,
                distance_km=round(distance, 2),
                estimated_travel_time_minutes=round(travel_time, 1),
                availability_score=round(availability_score, 2),
                current_wait_time_minutes=5.0 if availability_score < 0.3 else 0.0
            )

            results.append(result)

        # Sort by distance
        results.sort(key=lambda x: x.distance_km)

        logger.info(f"Found {len(results)} stations within {search.radius_km}km for user {current_user.username}")
        return results

    except Exception as e:
        logger.error(f"Error searching stations: {e}")
        raise HTTPException(status_code=500, detail="Error searching stations")

@router.get("/{station_id}/analytics", response_model=StationAnalytics)
async def get_station_analytics(
    station_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed analytics for a specific station"""
    try:
        station = await get_mock_station(station_id)
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")

        # Mock demand forecast (24 hours)
        demand_forecast = {}
        for hour in range(24):
            if 6 <= hour <= 10 or 17 <= hour <= 20:  # Peak hours
                demand_forecast[str(hour)] = 0.8 + (hour % 3 * 0.1)
            else:  # Off-peak
                demand_forecast[str(hour)] = 0.3 + (hour % 4 * 0.05)

        # Mock optimization recommendations
        recommendations = [
            "Consider adding 2 more charging slots during peak hours",
            "Battery inventory is optimal for current demand",
            "Upgrade to faster charging equipment could reduce wait times",
            "Install solar panels to reduce grid dependency"
        ]

        # Mock ROI metrics
        roi_metrics = {
            "monthly_revenue": 45000.0,
            "operating_costs": 32000.0,
            "profit_margin": 0.29,
            "payback_period_months": 18.5,
            "roi_percentage": 156.3
        }

        analytics = StationAnalytics(
            station_id=station_id,
            performance_metrics=station.metrics,
            demand_forecast=demand_forecast,
            optimization_recommendations=recommendations,
            roi_metrics=roi_metrics
        )

        logger.info(f"Analytics retrieved for station {station_id}")
        return analytics

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving station analytics: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analytics")

@router.post("/placement/optimize", response_model=StationPlacementResponse)
async def optimize_station_placement(
    request: StationPlacementRequest,
    current_user: User = Depends(require_admin)
):
    """Optimize station placement for a region"""
    try:
        # Calculate region characteristics
        region_area = calculate_polygon_area(request.region_bounds)

        region_data = {
            "area_km2": region_area,
            "population_density": request.population_data.get("density", 100) if request.population_data else 100,
            "traffic_volume": request.traffic_data.get("daily_volume", 5000) if request.traffic_data else 5000,
            "existing_stations": 0  # Would query from database
        }

        # Use ML service for optimization
        optimization = await ml_service.optimize_station_placement(region_data)

        # Generate recommended locations (mock coordinates)
        recommended_locations = []
        num_recommendations = min(request.max_stations, optimization["analysis"]["recommended_new"])

        for i in range(num_recommendations):
            # Generate location within region bounds
            lat = request.region_bounds[0][0] + (i * 0.01)
            lon = request.region_bounds[0][1] + (i * 0.01)

            location = Location(
                lat=lat,
                lon=lon,
                address=f"Optimal Location {i+1}",
                city="Region City",
                state="Region State",
                country="India"
            )

            recommended_locations.append(location)

        # Mock analysis data
        coverage_analysis = {
            "current_coverage_percent": 45.2,
            "projected_coverage_percent": optimization["projections"]["coverage_improvement_percent"],
            "population_served": 125000,
            "underserved_areas": 3
        }

        demand_predictions = [150.5, 89.3, 203.7, 156.8, 178.2][:num_recommendations]
        investment_requirements = [250000] * num_recommendations
        roi_projections = [optimization["projections"]["roi_payback_years"]] * num_recommendations

        response = StationPlacementResponse(
            recommended_locations=recommended_locations,
            coverage_analysis=coverage_analysis,
            demand_predictions=demand_predictions,
            investment_requirements=investment_requirements,
            roi_projections=roi_projections,
            optimization_score=85.7
        )

        logger.info(f"Station placement optimization completed for {num_recommendations} locations")
        return response

    except Exception as e:
        logger.error(f"Error optimizing station placement: {e}")
        raise HTTPException(status_code=500, detail="Error optimizing station placement")

@router.get("/{station_id}/grid-integration", response_model=GridIntegration)
async def get_grid_integration_status(
    station_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get grid integration status for station"""
    try:
        station = await get_mock_station(station_id)
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")

        # Mock grid integration data
        grid_integration = GridIntegration(
            renewable_energy_percentage=65.3,
            grid_stability_score=8.7,
            peak_load_management=True,
            v2g_capability=True,
            carbon_intensity=0.45  # kg CO2/kWh
        )

        return grid_integration

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving grid integration status: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving grid integration status")

# Helper functions
async def get_mock_stations() -> List[Station]:
    """Generate mock station data"""
    stations = []

    station_data = [
        {
            "station_id": "STN001",
            "name": "Mumbai Central Swap Hub",
            "location": Location(
                lat=19.0760, lon=72.8777, 
                address="Mumbai Central Railway Station, Mumbai",
                city="Mumbai", state="Maharashtra", country="India"
            ),
            "station_type": StationType.URBAN,
            "capacity": {"total": 20, "available": 12, "healthy": 18}
        },
        {
            "station_id": "STN002",
            "name": "Pune Tech Park Station",
            "location": Location(
                lat=18.5204, lon=73.8567,
                address="Hinjewadi IT Park, Pune",
                city="Pune", state="Maharashtra", country="India"
            ),
            "station_type": StationType.COMMERCIAL,
            "capacity": {"total": 15, "available": 8, "healthy": 13}
        },
        {
            "station_id": "STN003",
            "name": "Highway Express Charging",
            "location": Location(
                lat=18.8000, lon=73.2000,
                address="Mumbai-Pune Expressway, Lonavala",
                city="Lonavala", state="Maharashtra", country="India"
            ),
            "station_type": StationType.HIGHWAY,
            "capacity": {"total": 12, "available": 9, "healthy": 11}
        }
    ]

    for i, data in enumerate(station_data):
        capacity = StationCapacity(
            total_slots=data["capacity"]["total"],
            available_slots=data["capacity"]["available"],
            charging_slots=int(data["capacity"]["total"] * 0.3),
            maintenance_slots=2,
            battery_inventory=data["capacity"]["total"],
            healthy_batteries=data["capacity"]["healthy"],
            degraded_batteries=data["capacity"]["total"] - data["capacity"]["healthy"]
        )

        metrics = OperationalMetrics(
            daily_swaps=150 + (i * 30),
            monthly_swaps=4500 + (i * 900),
            average_swap_time_seconds=90.0 + (i * 15),
            utilization_rate=0.75 - (i * 0.1),
            customer_satisfaction=4.5 + (i * 0.1),
            uptime_percentage=98.5 - (i * 0.5),
            energy_consumption_kwh=1200.0 + (i * 200),
            carbon_footprint_kg=540.0 + (i * 90)
        )

        station = Station(
            station_id=data["station_id"],
            name=data["name"],
            location=data["location"],
            station_type=data["station_type"],
            status=StationStatus.ACTIVE,
            capacity=capacity,
            metrics=metrics,
            amenities=["WiFi", "Restroom", "Cafe"] if i == 0 else ["WiFi"],
            operating_hours={"monday": "24/7", "tuesday": "24/7"},
            contact_info={"phone": f"+91-9876543{i}0", "email": f"station{i+1}@smartswapml.com"},
            created_at=datetime.utcnow() - timedelta(days=365 - i*30),
            updated_at=datetime.utcnow()
        )

        stations.append(station)

    return stations

async def get_mock_station(station_id: str) -> Optional[Station]:
    """Get single mock station"""
    stations = await get_mock_stations()
    for station in stations:
        if station.station_id == station_id:
            return station
    return None

def calculate_polygon_area(bounds: List[Tuple[float, float]]) -> float:
    """Calculate approximate area of polygon in km²"""
    if len(bounds) < 3:
        return 100.0  # Default area

    # Simplified area calculation (for demo purposes)
    lat_range = max(point[0] for point in bounds) - min(point[0] for point in bounds)
    lon_range = max(point[1] for point in bounds) - min(point[1] for point in bounds)

    # Rough conversion to km² (1 degree ≈ 111 km)
    area = lat_range * lon_range * 111 * 111
    return area
