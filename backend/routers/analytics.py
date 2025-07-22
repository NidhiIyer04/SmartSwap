from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from models.users import User
from models.responses import AnalyticsResponse, ReportResponse, SystemStatusResponse
from services.auth_service import get_current_user, require_operator

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard", response_model=AnalyticsResponse)
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive dashboard analytics"""
    try:
        # Mock analytics data for demo
        analytics = AnalyticsResponse(
            total_batteries=1247,
            active_stations=156,
            daily_swaps=2834,
            average_health_score=89.3,
            energy_saved_kwh=12450.5,
            carbon_reduced_kg=2340.8,
            health_distribution={
                "excellent": 45,  # SOH > 90%
                "good": 30,       # SOH 70-90%
                "fair": 20,       # SOH 50-70%
                "poor": 5         # SOH < 50%
            },
            station_utilization={
                "STN001": 0.85,
                "STN002": 0.72,
                "STN003": 0.68,
                "STN004": 0.91,
                "STN005": 0.56
            },
            performance_metrics={
                "battery_life_extension_percent": 15.3,
                "range_prediction_accuracy": 92.5,
                "swap_success_rate": 98.7,
                "customer_satisfaction": 4.6,
                "cost_reduction_percent": 23.8,
                "energy_efficiency_improvement": 18.2
            },
            trends={
                "daily_swaps": [2650, 2720, 2834, 2690, 2890, 2834, 2945],  # Last 7 days
                "battery_health": [89.8, 89.6, 89.4, 89.3, 89.3, 89.3, 89.3],
                "energy_consumption": [11200, 11450, 11890, 12100, 12340, 12450, 12650],
                "customer_satisfaction": [4.5, 4.6, 4.5, 4.6, 4.7, 4.6, 4.6]
            }
        )

        logger.info(f"Dashboard analytics retrieved for user {current_user.username}")
        return analytics

    except Exception as e:
        logger.error(f"Error retrieving dashboard analytics: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analytics")

@router.get("/battery-health-summary")
async def get_battery_health_summary(
    current_user: User = Depends(get_current_user)
):
    """Get detailed battery health summary"""
    try:
        summary = {
            "total_batteries": 1247,
            "health_categories": {
                "excellent": {"count": 561, "percentage": 45.0, "avg_soh": 95.2},
                "good": {"count": 374, "percentage": 30.0, "avg_soh": 82.1},
                "fair": {"count": 249, "percentage": 20.0, "avg_soh": 63.5},
                "poor": {"count": 63, "percentage": 5.0, "avg_soh": 42.3}
            },
            "aging_analysis": {
                "avg_age_months": 18.5,
                "avg_cycle_count": 1234,
                "degradation_rate_per_month": 0.8,
                "projected_replacement_timeline": {
                    "next_30_days": 12,
                    "next_90_days": 45,
                    "next_180_days": 89,
                    "next_365_days": 178
                }
            },
            "performance_metrics": {
                "prediction_accuracy": 94.7,
                "health_improvement_actions": 23,
                "preventive_maintenance_alerts": 8,
                "optimization_opportunities": 15
            }
        }

        logger.info(f"Battery health summary retrieved for user {current_user.username}")
        return {"success": True, "data": summary}

    except Exception as e:
        logger.error(f"Error retrieving battery health summary: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving battery health summary")

@router.get("/range-prediction-analytics")
async def get_range_prediction_analytics(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user)
):
    """Get range prediction performance analytics"""
    try:
        # Mock data for the last N days
        daily_data = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-i-1)
            daily_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "total_predictions": 450 + (i * 23),
                "accuracy_percent": 91.5 + (i * 0.2),
                "avg_error_km": 8.2 - (i * 0.1),
                "weather_integration_accuracy": 94.2 + (i * 0.1),
                "terrain_analysis_accuracy": 89.7 + (i * 0.3),
                "user_satisfaction": 4.5 + (i * 0.02)
            })

        analytics = {
            "period_summary": {
                "total_predictions": sum(d["total_predictions"] for d in daily_data),
                "average_accuracy": sum(d["accuracy_percent"] for d in daily_data) / len(daily_data),
                "best_day_accuracy": max(d["accuracy_percent"] for d in daily_data),
                "worst_day_accuracy": min(d["accuracy_percent"] for d in daily_data),
                "improvement_trend": "positive"
            },
            "daily_breakdown": daily_data,
            "factors_analysis": {
                "weather_impact": {"positive": 23, "negative": 12, "neutral": 65},
                "terrain_impact": {"positive": 18, "negative": 15, "neutral": 67},
                "battery_health_correlation": 0.78,
                "user_behavior_correlation": 0.65
            },
            "ml_model_performance": {
                "model_version": "v2.3.1",
                "training_data_points": 125000,
                "last_updated": "2024-01-15T10:30:00Z",
                "confidence_score": 92.5,
                "feature_importance": {
                    "battery_soh": 0.35,
                    "weather_conditions": 0.28,
                    "terrain_difficulty": 0.22,
                    "vehicle_efficiency": 0.15
                }
            }
        }

        logger.info(f"Range prediction analytics retrieved for {days} days")
        return {"success": True, "data": analytics}

    except Exception as e:
        logger.error(f"Error retrieving range prediction analytics: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving range prediction analytics")

@router.get("/circular-economy-metrics")
async def get_circular_economy_metrics(
    current_user: User = Depends(get_current_user)
):
    """Get circular economy tracking metrics"""
    try:
        metrics = {
            "battery_lifecycle": {
                "active_batteries": 1088,
                "second_life_applications": 134,
                "recycling_queue": 25,
                "total_processed": 1247
            },
            "material_recovery": {
                "lithium": {"recovered_kg": 1245.6, "recovery_rate": 78.2, "market_value_usd": 18673.5},
                "cobalt": {"recovered_kg": 892.3, "recovery_rate": 85.1, "market_value_usd": 71384.4},
                "nickel": {"recovered_kg": 2156.7, "recovery_rate": 91.8, "market_value_usd": 34509.2},
                "aluminum": {"recovered_kg": 3421.9, "recovery_rate": 94.6, "market_value_usd": 6155.4},
                "copper": {"recovered_kg": 1876.2, "recovery_rate": 97.3, "market_value_usd": 16885.8}
            },
            "environmental_impact": {
                "co2_saved_tons": 156.7,
                "energy_recovered_mwh": 234.8,
                "waste_diverted_tons": 89.3,
                "water_saved_liters": 45670,
                "carbon_footprint_reduction_percent": 23.4
            },
            "economic_benefits": {
                "material_value_recovered_usd": 147608.3,
                "disposal_costs_avoided_usd": 23456.7,
                "second_life_revenue_usd": 67890.1,
                "total_economic_benefit_usd": 238955.1
            },
            "second_life_applications": {
                "stationary_energy_storage": 78,
                "residential_solar_storage": 34,
                "grid_stabilization": 12,
                "backup_power_systems": 10
            },
            "sustainability_goals": {
                "recycling_target_percent": 85,
                "current_recycling_rate": 78.2,
                "material_recovery_target": 90,
                "current_recovery_rate": 85.1,
                "carbon_neutral_target_year": 2030,
                "progress_percent": 67.3
            }
        }

        logger.info(f"Circular economy metrics retrieved for user {current_user.username}")
        return {"success": True, "data": metrics}

    except Exception as e:
        logger.error(f"Error retrieving circular economy metrics: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving circular economy metrics")

@router.get("/station-performance")
async def get_station_performance_analytics(
    station_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get station performance analytics"""
    try:
        if station_id:
            # Single station analytics
            performance = {
                "station_id": station_id,
                "name": f"Station {station_id}",
                "performance_metrics": {
                    "daily_swaps": 287,
                    "utilization_rate": 0.834,
                    "average_swap_time": 92.3,
                    "customer_satisfaction": 4.7,
                    "uptime_percent": 98.9,
                    "energy_efficiency": 0.892
                },
                "operational_data": {
                    "total_batteries": 20,
                    "healthy_batteries": 18,
                    "batteries_charging": 6,
                    "maintenance_queue": 2,
                    "peak_hours": ["07:00-09:00", "18:00-20:00"],
                    "off_peak_hours": ["23:00-06:00"]
                },
                "financial_metrics": {
                    "daily_revenue": 4305.50,
                    "monthly_target": 125000,
                    "monthly_progress": 0.72,
                    "cost_per_swap": 15.2,
                    "profit_margin": 0.34
                }
            }
        else:
            # Network-wide analytics
            performance = {
                "network_summary": {
                    "total_stations": 156,
                    "active_stations": 152,
                    "maintenance_stations": 3,
                    "offline_stations": 1
                },
                "performance_distribution": {
                    "high_performers": 89,  # >80% utilization
                    "average_performers": 52,  # 50-80% utilization
                    "underperformers": 15   # <50% utilization
                },
                "top_performing_stations": [
                    {"station_id": "STN045", "utilization": 0.94, "daily_swaps": 342},
                    {"station_id": "STN012", "utilization": 0.91, "daily_swaps": 328},
                    {"station_id": "STN078", "utilization": 0.89, "daily_swaps": 315}
                ],
                "improvement_opportunities": [
                    {"station_id": "STN134", "issue": "Low utilization", "recommendation": "Marketing campaign"},
                    {"station_id": "STN089", "issue": "Slow swap times", "recommendation": "Equipment upgrade"},
                    {"station_id": "STN156", "issue": "Battery shortage", "recommendation": "Inventory increase"}
                ],
                "network_metrics": {
                    "total_daily_swaps": 28340,
                    "average_utilization": 0.756,
                    "network_uptime": 0.987,
                    "customer_satisfaction": 4.6
                }
            }

        logger.info(f"Station performance analytics retrieved for {station_id or 'all stations'}")
        return {"success": True, "data": performance}

    except Exception as e:
        logger.error(f"Error retrieving station performance analytics: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving station performance analytics")

@router.get("/system-status", response_model=SystemStatusResponse)
async def get_system_status(
    current_user: User = Depends(require_operator)
):
    """Get system health and status"""
    try:
        status = SystemStatusResponse(
            status="healthy",
            uptime_seconds=2847360,  # ~33 days
            database_status="connected",
            cache_status="connected",
            api_status={
                "weather_api": "connected",
                "maps_api": "connected",
                "elevation_api": "connected",
                "payment_gateway": "connected"
            },
            last_updated=datetime.utcnow(),
            active_users=1247,
            requests_per_minute=145.7
        )

        return status

    except Exception as e:
        logger.error(f"Error retrieving system status: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving system status")

@router.post("/generate-report", response_model=ReportResponse)
async def generate_custom_report(
    report_type: str = Query(..., regex="^(battery|station|circular|performance)$"),
    date_from: Optional[str] = Query(None, regex=r"^\d{4}-\d{2}-\d{2}$"),
    date_to: Optional[str] = Query(None, regex=r"^\d{4}-\d{2}-\d{2}$"),
    current_user: User = Depends(get_current_user)
):
    """Generate custom analytics report"""
    try:
        report_id = f"report_{int(datetime.utcnow().timestamp())}"

        # Mock report data based on type
        if report_type == "battery":
            data = {
                "total_batteries_analyzed": 1247,
                "health_trends": "Improving",
                "degradation_analysis": "Within expected parameters",
                "replacement_schedule": "23 batteries due for replacement in Q2"
            }
            title = "Battery Health Analysis Report"
        elif report_type == "station":
            data = {
                "stations_analyzed": 156,
                "performance_summary": "Above target",
                "utilization_trends": "Increasing",
                "expansion_recommendations": "5 new locations identified"
            }
            title = "Station Performance Report"
        elif report_type == "circular":
            data = {
                "materials_recovered": "2.3 tons",
                "environmental_impact": "156.7 tons CO2 saved",
                "economic_value": "$238,955",
                "sustainability_progress": "67% towards 2030 goals"
            }
            title = "Circular Economy Impact Report"
        else:  # performance
            data = {
                "overall_efficiency": "92.5%",
                "customer_satisfaction": "4.6/5.0",
                "cost_optimization": "23.8% reduction achieved",
                "innovation_impact": "15.3% battery life extension"
            }
            title = "System Performance Report"

        report = ReportResponse(
            report_id=report_id,
            title=title,
            generated_at=datetime.utcnow(),
            data=data,
            charts=[
                {"type": "line", "title": "Trend Analysis", "data": []},
                {"type": "bar", "title": "Performance Metrics", "data": []}
            ],
            summary={
                "key_findings": 3,
                "recommendations": 5,
                "data_points_analyzed": 125000,
                "confidence_score": 94.7
            },
            recommendations=[
                "Continue current optimization strategies",
                "Invest in predictive maintenance capabilities",
                "Expand circular economy programs",
                "Focus on rural station deployment"
            ]
        )

        logger.info(f"Report {report_id} generated for user {current_user.username}")
        return report

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail="Error generating report")
