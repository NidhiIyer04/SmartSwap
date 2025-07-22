import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import json

logger = logging.getLogger(__name__)

class MLService:
    """Machine Learning service for battery health and range prediction"""

    def __init__(self):
        self.battery_health_model = None
        self.range_prediction_model = None
        self.scaler = StandardScaler()
        self._initialize_models()

    def _initialize_models(self):
        """Initialize ML models with mock training data"""
        try:
            # Initialize battery health prediction model
            self.battery_health_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )

            # Initialize range prediction model
            self.range_prediction_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                random_state=42
            )

            # Train models with synthetic data for demo purposes
            self._train_demo_models()

            logger.info("ML models initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")
            raise

    def _train_demo_models(self):
        """Train models with synthetic demo data"""
        # Generate synthetic battery health data
        np.random.seed(42)
        n_samples = 1000

        # Battery health features: [SOC, cycles, temp, age_days, voltage]
        X_health = np.random.rand(n_samples, 5)
        X_health[:, 0] *= 100  # SOC 0-100%
        X_health[:, 1] *= 3000  # Cycles 0-3000
        X_health[:, 2] = X_health[:, 2] * 60 + 10  # Temp 10-70°C
        X_health[:, 3] *= 1000  # Age 0-1000 days
        X_health[:, 4] = X_health[:, 4] * 1.5 + 3.0  # Voltage 3.0-4.5V

        # Simulate SOH based on cycles and age (inverse relationship)
        y_health = 100 - (X_health[:, 1] / 30 + X_health[:, 3] / 20) + np.random.normal(0, 5, n_samples)
        y_health = np.clip(y_health, 20, 100)  # SOH 20-100%

        self.battery_health_model.fit(X_health, y_health)

        # Range prediction features: [SOC, SOH, distance, elevation_change, temp, wind_speed]
        X_range = np.random.rand(n_samples, 6)
        X_range[:, 0] *= 100  # SOC 0-100%
        X_range[:, 1] *= 100  # SOH 0-100%
        X_range[:, 2] *= 500  # Distance 0-500km
        X_range[:, 3] = (X_range[:, 3] - 0.5) * 1000  # Elevation -500 to +500m
        X_range[:, 4] = X_range[:, 4] * 40 - 10  # Temp -10 to 30°C
        X_range[:, 5] *= 30  # Wind speed 0-30 km/h

        # Simulate range based on SOC, SOH, and conditions
        base_range = X_range[:, 0] * X_range[:, 1] / 100 * 3  # Base range from battery state
        temp_factor = 1 - np.abs(X_range[:, 4] - 20) / 100  # Temperature impact
        elevation_factor = 1 - np.abs(X_range[:, 3]) / 2000  # Elevation impact
        wind_factor = 1 - X_range[:, 5] / 100  # Wind resistance

        y_range = base_range * temp_factor * elevation_factor * wind_factor
        y_range += np.random.normal(0, 10, n_samples)  # Add noise
        y_range = np.clip(y_range, 10, 400)  # Range 10-400km

        self.range_prediction_model.fit(X_range, y_range)

    async def predict_battery_health(self, battery_data: Dict) -> Dict:
        """Predict battery health and degradation"""
        try:
            # Extract features from battery data
            features = [
                battery_data.get('soc', 80.0),
                battery_data.get('cycle_count', 500),
                battery_data.get('temperature', 25.0),
                battery_data.get('age_days', 365),
                battery_data.get('voltage', 3.7)
            ]

            # Make prediction
            features_array = np.array([features])
            predicted_soh = self.battery_health_model.predict(features_array)[0]

            # Calculate confidence based on feature stability
            confidence = min(100 - abs(features[1] - 1000) / 50, 95)  # Based on cycles

            # Generate 7-day degradation forecast
            forecast = []
            for i in range(7):
                future_features = features.copy()
                future_features[3] += i  # Increase age
                future_soh = self.battery_health_model.predict([future_features])[0]
                forecast.append({
                    "day": i + 1,
                    "predicted_soh": round(max(future_soh, 20), 2),
                    "confidence": round(confidence - i, 2)
                })

            # Determine swap recommendation
            if predicted_soh >= 80:
                recommendation = "recommended"
            elif predicted_soh >= 60:
                recommendation = "caution"
            else:
                recommendation = "not_recommended"

            return {
                "current_soh": round(predicted_soh, 2),
                "confidence": round(confidence, 2),
                "swap_recommendation": recommendation,
                "degradation_forecast": forecast,
                "health_factors": {
                    "cycle_impact": round(features[1] / 3000 * 100, 1),
                    "temperature_impact": round(abs(features[2] - 25) * 2, 1),
                    "age_impact": round(features[3] / 1000 * 100, 1)
                }
            }

        except Exception as e:
            logger.error(f"Error predicting battery health: {e}")
            return {
                "current_soh": 85.0,
                "confidence": 75.0,
                "swap_recommendation": "recommended",
                "error": str(e)
            }

    async def predict_range(self, route_data: Dict) -> Dict:
        """Predict vehicle range with ML model"""
        try:
            # Extract features from route data
            features = [
                route_data.get('battery_soc', 80.0),
                route_data.get('battery_soh', 90.0),
                route_data.get('distance_km', 100.0),
                route_data.get('elevation_change', 0.0),
                route_data.get('weather_temp', 25.0),
                route_data.get('wind_speed', 10.0)
            ]

            # Make prediction
            features_array = np.array([features])
            predicted_range = self.range_prediction_model.predict(features_array)[0]

            # Calculate energy consumption
            battery_capacity = route_data.get('battery_capacity_kwh', 50.0)
            energy_consumption = battery_capacity * (100 - features[0]) / 100
            energy_per_km = energy_consumption / max(predicted_range, 1)

            # Calculate confidence based on feature reliability
            confidence = 95.0
            if abs(features[4] - 20) > 15:  # Temperature extreme
                confidence -= 10
            if abs(features[3]) > 500:  # High elevation change
                confidence -= 10
            if features[5] > 20:  # High wind speed
                confidence -= 5

            # Range factors analysis
            temp_impact = max(0, abs(features[4] - 20) * 0.02)  # 2% per degree from 20°C
            elevation_impact = abs(features[3]) / 1000 * 0.1  # 10% per 1000m elevation
            wind_impact = features[5] / 100 * 0.15  # 15% impact at 100 km/h wind

            return {
                "predicted_range": round(predicted_range, 2),
                "energy_consumption": round(energy_consumption, 2),
                "energy_per_km": round(energy_per_km, 3),
                "confidence": round(confidence, 2),
                "range_factors": {
                    "battery_state": round(features[1], 1),  # SOH impact
                    "temperature_impact": round(temp_impact * 100, 1),
                    "elevation_impact": round(elevation_impact * 100, 1),
                    "wind_impact": round(wind_impact * 100, 1)
                },
                "recommendations": self._generate_range_recommendations(features, predicted_range)
            }

        except Exception as e:
            logger.error(f"Error predicting range: {e}")
            return {
                "predicted_range": 150.0,
                "energy_consumption": 15.0,
                "confidence": 75.0,
                "error": str(e)
            }

    def _generate_range_recommendations(self, features: List, predicted_range: float) -> List[str]:
        """Generate range optimization recommendations"""
        recommendations = []

        soc, soh, distance, elevation, temp, wind = features

        if soc < 30:
            recommendations.append("Consider charging before long trips")

        if temp < 0 or temp > 35:
            recommendations.append("Extreme temperature may reduce range by up to 20%")

        if elevation > 200:
            recommendations.append("Significant uphill driving detected - reduce speed to conserve energy")

        if wind > 20:
            recommendations.append("High wind conditions - consider alternative route if available")

        if soh < 80:
            recommendations.append("Battery health below optimal - consider replacement soon")

        if predicted_range < distance:
            recommendations.append("Insufficient range for destination - charging stop required")

        if not recommendations:
            recommendations.append("Route optimized for maximum efficiency")

        return recommendations

    async def analyze_circular_economy(self, battery_data: List[Dict]) -> Dict:
        """Analyze batteries for circular economy opportunities"""
        try:
            total_batteries = len(battery_data)
            if total_batteries == 0:
                return {"error": "No battery data provided"}

            # Categorize batteries by health status
            healthy = sum(1 for b in battery_data if b.get('soh', 0) >= 80)
            degraded = sum(1 for b in battery_data if 50 <= b.get('soh', 0) < 80)
            end_of_life = sum(1 for b in battery_data if b.get('soh', 0) < 50)

            # Calculate material recovery potential
            avg_capacity = np.mean([b.get('capacity_kwh', 50) for b in battery_data])
            total_capacity = total_batteries * avg_capacity

            # Mock material composition (typical Li-ion battery)
            materials = {
                "lithium": total_capacity * 0.02,  # kg
                "cobalt": total_capacity * 0.15,
                "nickel": total_capacity * 0.35,
                "aluminum": total_capacity * 0.25,
                "copper": total_capacity * 0.15
            }

            # Recovery rates (industry average)
            recovery_rates = {
                "lithium": 0.78,
                "cobalt": 0.85,
                "nickel": 0.92,
                "aluminum": 0.95,
                "copper": 0.98
            }

            # Calculate carbon savings (typical values)
            carbon_per_battery = 2.5  # tons CO2 per battery lifecycle
            carbon_saved_second_life = degraded * carbon_per_battery * 0.3  # 30% extension
            carbon_saved_recycling = end_of_life * carbon_per_battery * 0.2  # 20% recovery

            return {
                "total_batteries": total_batteries,
                "health_distribution": {
                    "healthy": healthy,
                    "degraded": degraded,
                    "end_of_life": end_of_life
                },
                "material_inventory": materials,
                "recovery_potential": {
                    material: round(amount * recovery_rates[material], 2)
                    for material, amount in materials.items()
                },
                "carbon_impact": {
                    "second_life_savings_tons": round(carbon_saved_second_life, 2),
                    "recycling_savings_tons": round(carbon_saved_recycling, 2),
                    "total_savings_tons": round(carbon_saved_second_life + carbon_saved_recycling, 2)
                },
                "recommendations": [
                    f"{degraded} batteries suitable for second-life applications",
                    f"{end_of_life} batteries ready for material recovery",
                    f"Potential to recover {materials['lithium'] * recovery_rates['lithium']:.1f}kg lithium"
                ]
            }

        except Exception as e:
            logger.error(f"Error in circular economy analysis: {e}")
            return {"error": str(e)}

    async def optimize_station_placement(self, region_data: Dict) -> Dict:
        """Optimize station placement using ML analysis"""
        try:
            # Mock analysis based on region characteristics
            population_density = region_data.get('population_density', 100)  # per km²
            traffic_volume = region_data.get('traffic_volume', 1000)  # vehicles/day
            existing_stations = region_data.get('existing_stations', 0)
            area_km2 = region_data.get('area_km2', 100)

            # Calculate optimal station density
            base_demand = population_density * 0.01 + traffic_volume * 0.0001  # Demand score
            optimal_stations = max(1, int(area_km2 * base_demand / 1000))

            # Adjust for existing infrastructure
            recommended_new_stations = max(0, optimal_stations - existing_stations)

            # Calculate coverage and ROI projections
            coverage_improvement = min(100, recommended_new_stations * 15)  # 15% per station
            investment_per_station = 250000  # $250k per station
            daily_swaps_per_station = min(50, base_demand * 10)
            annual_revenue_per_station = daily_swaps_per_station * 365 * 5  # $5 per swap
            roi_years = investment_per_station / annual_revenue_per_station if annual_revenue_per_station > 0 else 10

            return {
                "analysis": {
                    "current_stations": existing_stations,
                    "optimal_stations": optimal_stations,
                    "recommended_new": recommended_new_stations,
                    "demand_score": round(base_demand, 2)
                },
                "projections": {
                    "coverage_improvement_percent": round(coverage_improvement, 1),
                    "investment_required": recommended_new_stations * investment_per_station,
                    "annual_revenue_projection": round(recommended_new_stations * annual_revenue_per_station),
                    "roi_payback_years": round(roi_years, 1)
                },
                "recommendations": [
                    f"Deploy {recommended_new_stations} new stations for optimal coverage",
                    f"Focus on areas with population density > {population_density} per km²",
                    f"Expected {daily_swaps_per_station:.0f} daily swaps per station",
                    f"Payback period: {roi_years:.1f} years"
                ]
            }

        except Exception as e:
            logger.error(f"Error in station placement optimization: {e}")
            return {"error": str(e)}

# Global ML service instance
ml_service = MLService()
