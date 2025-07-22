from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from models.users import User
from models.batteries import (
    Battery, BatteryCreate, BatteryUpdate, BatteryMetrics,
    HealthPredictionRequest, HealthPredictionResponse,
    SwapRequest, SwapResponse, CircularEconomyMetrics,
    BatteryStatus, SwapRecommendation
)
from models.responses import APIResponse, PaginatedResponse
from services.auth_service import get_current_user, require_operator
from services.ml_service import ml_service
from config.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[Battery])
async def get_batteries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    station_id: Optional[str] = None,
    status: Optional[BatteryStatus] = None,
    current_user: User = Depends(get_current_user)
):
    """Get list of batteries with optional filters"""
    try:
        db = await get_database()

        # Build query filter
        query_filter = {}
        if station_id:
            query_filter["station_id"] = station_id
        if status:
            query_filter["metrics.status"] = status

        # Get batteries from database (mock data for now)
        batteries = await get_mock_batteries(query_filter, skip, limit)

        logger.info(f"Retrieved {len(batteries)} batteries for user {current_user.username}")
        return batteries

    except Exception as e:
        logger.error(f"Error retrieving batteries: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving batteries")

@router.get("/{battery_id}", response_model=Battery)
async def get_battery(
    battery_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific battery details"""
    try:
        db = await get_database()

        # Get battery from database (mock for now)
        battery = await get_mock_battery(battery_id)

        if not battery:
            raise HTTPException(status_code=404, detail="Battery not found")

        return battery

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving battery {battery_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving battery")

@router.post("/", response_model=APIResponse)
async def create_battery(
    battery_data: BatteryCreate,
    current_user: User = Depends(require_operator)
):
    """Create new battery record"""
    try:
        db = await get_database()

        # Check if battery already exists
        existing = await db.batteries.find_one({"battery_id": battery_data.battery_id})
        if existing:
            raise HTTPException(status_code=400, detail="Battery already exists")

        # Create battery document
        battery_doc = {
            **battery_data.dict(),
            "metrics": {
                "health": {
                    "soc": 100.0,
                    "soh": 100.0,
                    "voltage": 3.7,
                    "current": 0.0,
                    "temperature": 25.0,
                    "cycle_count": 0,
                    "capacity_remaining": battery_data.capacity_kwh,
                    "internal_resistance": 0.1
                },
                "status": BatteryStatus.HEALTHY,
                "swap_recommendation": SwapRecommendation.RECOMMENDED,
                "confidence_score": 95.0,
                "predicted_range_km": 200.0,
                "estimated_life_remaining_days": 2000
            },
            "maintenance_history": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        await db.batteries.insert_one(battery_doc)

        logger.info(f"Battery {battery_data.battery_id} created by {current_user.username}")

        return APIResponse(
            success=True,
            message="Battery created successfully",
            data={"battery_id": battery_data.battery_id}
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating battery: {e}")
        raise HTTPException(status_code=500, detail="Error creating battery")

@router.put("/{battery_id}", response_model=APIResponse)
async def update_battery(
    battery_id: str,
    battery_data: BatteryUpdate,
    current_user: User = Depends(require_operator)
):
    """Update battery information"""
    try:
        db = await get_database()

        # Check if battery exists
        existing = await db.batteries.find_one({"battery_id": battery_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Battery not found")

        # Prepare update data
        update_data = {k: v for k, v in battery_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()

        # Update battery
        await db.batteries.update_one(
            {"battery_id": battery_id},
            {"$set": update_data}
        )

        logger.info(f"Battery {battery_id} updated by {current_user.username}")

        return APIResponse(
            success=True,
            message="Battery updated successfully"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating battery {battery_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating battery")

@router.post("/{battery_id}/health-prediction", response_model=HealthPredictionResponse)
async def predict_battery_health(
    battery_id: str,
    request: HealthPredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """Predict battery health and degradation"""
    try:
        # Get current battery data
        battery = await get_mock_battery(battery_id)
        if not battery:
            raise HTTPException(status_code=404, detail="Battery not found")

        # Prepare data for ML prediction
        battery_data = {
            "soc": battery.metrics.health.soc,
            "cycle_count": battery.metrics.health.cycle_count,
            "temperature": battery.metrics.health.temperature,
            "age_days": (datetime.utcnow() - battery.manufacturing_date).days,
            "voltage": battery.metrics.health.voltage,
            "capacity_kwh": battery.capacity_kwh
        }

        # Get ML prediction
        prediction = await ml_service.predict_battery_health(battery_data)

        # Prepare response
        response = HealthPredictionResponse(
            battery_id=battery_id,
            current_health=battery.metrics.health,
            predictions=prediction.get("degradation_forecast", []),
            confidence=prediction.get("confidence", 75.0),
            recommendations=[
                f"Current SOH: {prediction.get('current_soh', 85)}%",
                f"Swap recommendation: {prediction.get('swap_recommendation', 'recommended')}",
                "Monitor temperature and charging patterns"
            ]
        )

        logger.info(f"Health prediction generated for battery {battery_id}")
        return response

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error predicting battery health for {battery_id}: {e}")
        raise HTTPException(status_code=500, detail="Error generating health prediction")

@router.post("/swap/analyze", response_model=SwapResponse)
async def analyze_swap_request(
    swap_request: SwapRequest,
    current_user: User = Depends(get_current_user)
):
    """Analyze battery swap request and provide recommendation"""
    try:
        # Get battery data
        old_battery = await get_mock_battery(swap_request.old_battery_id)
        new_battery = await get_mock_battery(swap_request.new_battery_id)

        if not old_battery or not new_battery:
            raise HTTPException(status_code=404, detail="One or both batteries not found")

        # Calculate swap benefits
        old_health = old_battery.metrics.health.soh
        new_health = new_battery.metrics.health.soh
        health_improvement = new_health - old_health

        # Estimate range improvement
        range_improvement = health_improvement * 2  # Rough estimate: 2km per 1% SOH

        # Determine recommendation
        if health_improvement >= 20:
            recommendation = SwapRecommendation.RECOMMENDED
            confidence = 95.0
            warnings = []
        elif health_improvement >= 10:
            recommendation = SwapRecommendation.CAUTION
            confidence = 75.0
            warnings = ["Moderate improvement expected"]
        else:
            recommendation = SwapRecommendation.NOT_RECOMMENDED
            confidence = 60.0
            warnings = ["Minimal improvement expected", "Consider keeping current battery"]

        response = SwapResponse(
            swap_id=f"swap_{int(datetime.utcnow().timestamp())}",
            recommendation=recommendation,
            old_battery_health=old_health,
            new_battery_health=new_health,
            estimated_range_improvement=range_improvement,
            confidence_score=confidence,
            warnings=warnings
        )

        logger.info(f"Swap analysis completed for user {current_user.username}")
        return response

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error analyzing swap request: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing swap request")

@router.get("/analytics/circular-economy", response_model=CircularEconomyMetrics)
async def get_circular_economy_metrics(
    current_user: User = Depends(get_current_user)
):
    """Get circular economy metrics for all batteries"""
    try:
        # Get battery data (mock for now)
        batteries_data = await get_mock_battery_fleet()

        # Analyze circular economy opportunities
        analysis = await ml_service.analyze_circular_economy(batteries_data)

        # Format response
        metrics = CircularEconomyMetrics(
            total_batteries=analysis.get("total_batteries", 0),
            active_batteries=analysis.get("health_distribution", {}).get("healthy", 0),
            batteries_in_second_life=analysis.get("health_distribution", {}).get("degraded", 0),
            batteries_recycled=analysis.get("health_distribution", {}).get("end_of_life", 0),
            material_recovery_rate=analysis.get("recovery_potential", {}),
            carbon_footprint_saved_kg=analysis.get("carbon_impact", {}).get("total_savings_tons", 0) * 1000,
            energy_recovery_efficiency=0.85  # Mock value
        )

        logger.info(f"Circular economy metrics retrieved for user {current_user.username}")
        return metrics

    except Exception as e:
        logger.error(f"Error retrieving circular economy metrics: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving metrics")

# Helper functions for mock data
async def get_mock_batteries(query_filter: dict, skip: int, limit: int) -> List[Battery]:
    """Generate mock battery data"""
    from models.batteries import BatteryHealth, BatteryMetrics

    batteries = []
    battery_ids = ["BAT001", "BAT002", "BAT003", "BAT004", "BAT005"]

    for i, battery_id in enumerate(battery_ids[skip:skip+limit]):
        health = BatteryHealth(
            soc=85.0 + (i * 2),
            soh=90.0 - (i * 3),
            voltage=3.7 + (i * 0.1),
            current=2.5,
            temperature=25.0 + (i * 2),
            cycle_count=500 + (i * 100),
            capacity_remaining=48.0 - (i * 2),
            internal_resistance=0.1 + (i * 0.01)
        )

        metrics = BatteryMetrics(
            health=health,
            status=BatteryStatus.HEALTHY if health.soh > 80 else BatteryStatus.DEGRADED,
            swap_recommendation=SwapRecommendation.RECOMMENDED if health.soh > 80 else SwapRecommendation.CAUTION,
            confidence_score=95.0 - (i * 5),
            predicted_range_km=200.0 - (i * 10),
            estimated_life_remaining_days=2000 - (i * 200)
        )

        battery = Battery(
            battery_id=battery_id,
            station_id=f"STN00{(i % 3) + 1}",
            manufacturer="CATL",
            model=f"LFP-50-{i}",
            chemistry="LiFePO4",
            capacity_kwh=50.0,
            manufacturing_date=datetime.utcnow() - timedelta(days=365 + i*30),
            first_use_date=datetime.utcnow() - timedelta(days=300 + i*20),
            current_location=f"Station {(i % 3) + 1}",
            metrics=metrics,
            maintenance_history=[],
            created_at=datetime.utcnow() - timedelta(days=300),
            updated_at=datetime.utcnow()
        )

        batteries.append(battery)

    return batteries

async def get_mock_battery(battery_id: str) -> Optional[Battery]:
    """Get single mock battery"""
    batteries = await get_mock_batteries({}, 0, 10)
    for battery in batteries:
        if battery.battery_id == battery_id:
            return battery
    return None

async def get_mock_battery_fleet() -> List[dict]:
    """Get mock battery fleet data for analysis"""
    return [
        {"soh": 95.0, "capacity_kwh": 50.0, "age_days": 200},
        {"soh": 87.0, "capacity_kwh": 50.0, "age_days": 400},
        {"soh": 72.0, "capacity_kwh": 50.0, "age_days": 600},
        {"soh": 45.0, "capacity_kwh": 50.0, "age_days": 800},
        {"soh": 88.0, "capacity_kwh": 50.0, "age_days": 350}
    ]
