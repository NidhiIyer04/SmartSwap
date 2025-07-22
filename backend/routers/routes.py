from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Tuple
import logging
from datetime import datetime

from models.users import User
from models.routes import (
    RouteOptimizationRequest, RouteOptimizationResponse,
    RangeAnalysisRequest, RangeAnalysisResponse,
    TerrainAnalysisRequest, TerrainAnalysisResponse,
    WeatherData, ElevationPoint, RouteSegment, TerrainType, WeatherCondition,
    OptimizationMetrics
)
from models.responses import APIResponse
from services.auth_service import get_current_user
from services.ml_service import ml_service
from services.api_clients import weather_client, maps_client, elevation_client

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/optimize", response_model=RouteOptimizationResponse)
async def optimize_route(
    request: RouteOptimizationRequest,
    current_user: User = Depends(get_current_user)
):
    """Optimize route with weather and terrain analysis"""
    try:
        logger.info(f"Route optimization requested by {current_user.username}: {request.origin} -> {request.destination}")

        # Get route data from Google Maps
        directions = await maps_client.get_directions(request.origin, request.destination)
        if not directions:
            raise HTTPException(status_code=400, detail="Could not find route between locations")

        # Get weather data for origin
        origin_coords = await maps_client.geocode(request.origin)
        weather_data = []

        if origin_coords:
            weather = await weather_client.get_weather(origin_coords["lat"], origin_coords["lon"])
            if weather:
                weather_data.append(WeatherData(
                    location=request.origin,
                    temperature=weather["temperature"],
                    humidity=weather["humidity"],
                    wind_speed=weather["wind_speed"],
                    wind_direction=weather["wind_direction"],
                    condition=WeatherCondition(weather["condition"]),
                    timestamp=weather["timestamp"]
                ))

        # Generate route segments with terrain analysis
        segments = await generate_route_segments(directions, request)

        # Generate elevation profile
        elevation_profile = await generate_elevation_profile(directions)

        # Use ML service for range prediction
        route_data = {
            "battery_soc": request.battery_soc,
            "battery_soh": request.battery_soh,
            "distance_km": directions["distance_km"],
            "elevation_change": sum(seg.elevation_change for seg in segments),
            "weather_temp": weather_data[0].temperature if weather_data else 25.0,
            "wind_speed": weather_data[0].wind_speed if weather_data else 10.0,
            "vehicle_efficiency": request.vehicle_efficiency
        }

        range_prediction = await ml_service.predict_range(route_data)

        # Determine charging stops if needed
        charging_stops = []
        if range_prediction["predicted_range"] < directions["distance_km"]:
            charging_stops = ["Station midway - coordinates needed"]

        # Generate warnings based on conditions
        warnings = []
        if weather_data and weather_data[0].temperature < 5:
            warnings.append("Cold weather may reduce range by up to 20%")
        if any(seg.elevation_change > 100 for seg in segments):
            warnings.append("Significant elevation changes detected")
        if range_prediction["predicted_range"] < directions["distance_km"] * 1.2:
            warnings.append("Limited range margin - consider charging")

        response = RouteOptimizationResponse(
            route_id=f"route_{int(datetime.utcnow().timestamp())}",
            origin=request.origin,
            destination=request.destination,
            total_distance_km=directions["distance_km"],
            estimated_duration_minutes=directions["duration_minutes"],
            estimated_energy_consumption_kwh=range_prediction["energy_consumption"],
            estimated_range_remaining_km=range_prediction["predicted_range"] - directions["distance_km"],
            confidence_score=range_prediction["confidence"],
            route_polyline=directions["polyline"],
            segments=segments,
            elevation_profile=elevation_profile,
            weather_conditions=weather_data,
            recommended_charging_stops=charging_stops,
            warnings=warnings,
            created_at=datetime.utcnow()
        )

        logger.info(f"Route optimization completed: {directions['distance_km']}km, {range_prediction['predicted_range']}km range")
        return response

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error optimizing route: {e}")
        raise HTTPException(status_code=500, detail=f"Error optimizing route: {str(e)}")

@router.post("/range-analysis", response_model=RangeAnalysisResponse)
async def analyze_range(
    request: RangeAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """Analyze range based on battery state and route conditions"""
    try:
        # Prepare data for ML prediction
        route_data = {
            "battery_soc": request.battery_soc,
            "battery_soh": request.battery_soh,
            "distance_km": request.route_distance_km,
            "elevation_change": sum(terrain.get("elevation_change", 0) for terrain in request.terrain_data),
            "weather_temp": request.weather_data.get("temperature", 25.0) if request.weather_data else 25.0,
            "wind_speed": request.weather_data.get("wind_speed", 10.0) if request.weather_data else 10.0,
            "vehicle_efficiency": request.vehicle_efficiency
        }

        # Get ML prediction
        prediction = await ml_service.predict_range(route_data)

        # Calculate confidence interval (±10% of predicted range)
        predicted_range = prediction["predicted_range"]
        confidence_margin = predicted_range * 0.1
        confidence_interval = (predicted_range - confidence_margin, predicted_range + confidence_margin)

        # Energy consumption breakdown
        base_consumption = request.route_distance_km * request.vehicle_efficiency
        weather_impact = base_consumption * prediction["range_factors"].get("temperature_impact", 0) / 100
        terrain_impact = base_consumption * prediction["range_factors"].get("elevation_impact", 0) / 100

        energy_breakdown = {
            "base_driving": base_consumption,
            "weather_impact": weather_impact,
            "terrain_impact": terrain_impact,
            "total_estimated": prediction["energy_consumption"]
        }

        response = RangeAnalysisResponse(
            predicted_range_km=predicted_range,
            confidence_interval=confidence_interval,
            energy_consumption_breakdown=energy_breakdown,
            range_factors=prediction["range_factors"],
            recommendations=prediction["recommendations"]
        )

        logger.info(f"Range analysis completed for user {current_user.username}: {predicted_range}km predicted")
        return response

    except Exception as e:
        logger.error(f"Error analyzing range: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing range")

@router.post("/terrain-analysis", response_model=TerrainAnalysisResponse)
async def analyze_terrain(
    request: TerrainAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """Analyze terrain profile for route points"""
    try:
        # Get elevation data
        elevations = await elevation_client.get_elevation(request.route_points)

        # Convert to elevation points
        elevation_profile = []
        total_distance = 0

        for i, elev_data in enumerate(elevations):
            if i > 0:
                # Calculate distance from previous point (rough estimate)
                prev_point = elevations[i-1]
                distance_diff = ((elev_data["lat"] - prev_point["lat"])**2 + 
                               (elev_data["lon"] - prev_point["lon"])**2)**0.5 * 111  # km
                total_distance += distance_diff

            elevation_profile.append(ElevationPoint(
                lat=elev_data["lat"],
                lon=elev_data["lon"],
                elevation=elev_data["elevation"],
                distance_from_start=total_distance
            ))

        # Calculate terrain statistics
        elevations_only = [point.elevation for point in elevation_profile]
        total_elevation_gain = sum(max(0, elevations_only[i] - elevations_only[i-1]) 
                                 for i in range(1, len(elevations_only)))
        total_elevation_loss = sum(max(0, elevations_only[i-1] - elevations_only[i]) 
                                 for i in range(1, len(elevations_only)))

        # Calculate grades
        grades = []
        for i in range(1, len(elevation_profile)):
            elevation_diff = elevation_profile[i].elevation - elevation_profile[i-1].elevation
            distance_diff = elevation_profile[i].distance_from_start - elevation_profile[i-1].distance_from_start
            if distance_diff > 0:
                grade = (elevation_diff / (distance_diff * 1000)) * 100  # Percentage
                grades.append(abs(grade))

        max_grade = max(grades) if grades else 0
        avg_grade = sum(grades) / len(grades) if grades else 0

        # Terrain difficulty score (0-10)
        difficulty_score = min(10, (max_grade * 0.5) + (avg_grade * 0.3) + 
                              (total_elevation_gain / 1000))

        response = TerrainAnalysisResponse(
            elevation_profile=elevation_profile,
            total_elevation_gain=total_elevation_gain,
            total_elevation_loss=total_elevation_loss,
            max_grade=max_grade,
            avg_grade=avg_grade,
            terrain_difficulty_score=difficulty_score
        )

        logger.info(f"Terrain analysis completed: {len(elevation_profile)} points, difficulty {difficulty_score}/10")
        return response

    except Exception as e:
        logger.error(f"Error analyzing terrain: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing terrain")

@router.get("/demo/weather")
async def demo_weather_integration():
    """Demo endpoint to test weather API integration"""
    try:
        # Test weather API with Mumbai coordinates
        weather = await weather_client.get_weather(19.0760, 72.8777)

        return APIResponse(
            success=True,
            message="Weather API integration test",
            data={
                "location": "Mumbai (19.0760, 72.8777)",
                "weather": weather,
                "api_configured": bool(weather and not weather.get("mock_data", False))
            }
        )

    except Exception as e:
        logger.error(f"Error testing weather API: {e}")
        return APIResponse(
            success=False,
            message="Weather API test failed",
            data={"error": str(e)}
        )

@router.get("/metrics/optimization", response_model=OptimizationMetrics)
async def get_optimization_metrics(
    current_user: User = Depends(get_current_user)
):
    """Get route optimization performance metrics"""
    # Mock metrics for demo
    return OptimizationMetrics(
        standard_prediction_accuracy=70.2,
        ml_enhanced_accuracy=92.5,
        energy_saving_percentage=15.3,
        route_optimization_improvement=23.7,
        user_satisfaction_score=4.6
    )

# Helper functions
async def generate_route_segments(directions: dict, request: RouteOptimizationRequest) -> List[RouteSegment]:
    """Generate route segments with terrain analysis"""
    segments = []
    total_distance = directions["distance_km"]
    num_segments = min(10, max(3, int(total_distance / 20)))  # 1 segment per ~20km

    for i in range(num_segments):
        segment_distance = total_distance / num_segments
        start_progress = i / num_segments
        end_progress = (i + 1) / num_segments

        # Mock coordinates (would use actual route geometry)
        start_lat = 19.0760 + (start_progress * (18.5204 - 19.0760))
        start_lon = 72.8777 + (start_progress * (73.8567 - 72.8777))
        end_lat = 19.0760 + (end_progress * (18.5204 - 19.0760))
        end_lon = 72.8777 + (end_progress * (73.8567 - 72.8777))

        # Mock elevation change and terrain type
        elevation_change = (-50 + (i * 20)) if i < num_segments/2 else (50 - (i * 10))
        terrain_type = TerrainType.URBAN if i < 2 else (TerrainType.HIGHWAY if i < num_segments-2 else TerrainType.URBAN)

        # Estimate energy consumption for segment
        base_consumption = segment_distance * request.vehicle_efficiency
        terrain_factor = 1.2 if abs(elevation_change) > 50 else 1.0
        segment_consumption = base_consumption * terrain_factor

        segment = RouteSegment(
            start_lat=start_lat,
            start_lon=start_lon,
            end_lat=end_lat,
            end_lon=end_lon,
            distance_km=segment_distance,
            terrain_type=terrain_type,
            elevation_change=elevation_change,
            estimated_energy_consumption=segment_consumption,
            confidence_score=85.0 + (i * 2)
        )

        segments.append(segment)

    return segments

async def generate_elevation_profile(directions: dict) -> List[ElevationPoint]:
    """Generate elevation profile for route"""
    # Mock elevation profile (would use actual route geometry and elevation API)
    profile_points = 20
    total_distance = directions["distance_km"]

    elevation_profile = []
    for i in range(profile_points):
        progress = i / (profile_points - 1)

        # Mock coordinates along route
        lat = 19.0760 + (progress * (18.5204 - 19.0760))
        lon = 72.8777 + (progress * (73.8567 - 72.8777))

        # Mock elevation (simulate hills)
        base_elevation = 500
        hill_factor = abs(progress - 0.5) * 200  # Hill in middle of route
        elevation = base_elevation + hill_factor

        point = ElevationPoint(
            lat=lat,
            lon=lon,
            elevation=elevation,
            distance_from_start=total_distance * progress
        )

        elevation_profile.append(point)

    return elevation_profile
