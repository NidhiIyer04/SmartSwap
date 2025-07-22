import logging
import httpx
from typing import Optional, Dict, List, Tuple
import json
from datetime import datetime

from config.settings import settings

logger = logging.getLogger(__name__)

class WeatherAPIClient:
    """Client for OpenWeatherMap API integration"""

    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"

    async def get_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """Get current weather data for coordinates"""
        if not self.api_key:
            logger.warning("OpenWeather API key not configured, using mock data")
            return self._get_mock_weather(lat, lon)

        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "location": f"{lat},{lon}",
                        "temperature": data["main"]["temp"],
                        "humidity": data["main"]["humidity"],
                        "wind_speed": data["wind"]["speed"],
                        "wind_direction": data["wind"].get("deg", 0),
                        "condition": data["weather"][0]["main"].lower(),
                        "description": data["weather"][0]["description"],
                        "pressure": data["main"]["pressure"],
                        "visibility": data.get("visibility", 10000),
                        "timestamp": datetime.utcnow()
                    }
                else:
                    logger.error(f"Weather API error: {response.status_code}")
                    return self._get_mock_weather(lat, lon)

        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return self._get_mock_weather(lat, lon)

    async def get_weather_forecast(self, lat: float, lon: float, days: int = 5) -> List[Dict]:
        """Get weather forecast for multiple days"""
        if not self.api_key:
            return self._get_mock_forecast(lat, lon, days)

        try:
            url = f"{self.base_url}/forecast"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    forecasts = []

                    for item in data["list"][:days]:
                        forecasts.append({
                            "date": item["dt_txt"],
                            "temperature": item["main"]["temp"],
                            "condition": item["weather"][0]["main"].lower(),
                            "wind_speed": item["wind"]["speed"],
                            "humidity": item["main"]["humidity"]
                        })

                    return forecasts
                else:
                    return self._get_mock_forecast(lat, lon, days)

        except Exception as e:
            logger.error(f"Error fetching weather forecast: {e}")
            return self._get_mock_forecast(lat, lon, days)

    def _get_mock_weather(self, lat: float, lon: float) -> Dict:
        """Return mock weather data when API is unavailable"""
        return {
            "location": f"{lat},{lon}",
            "temperature": 25.0,
            "humidity": 60,
            "wind_speed": 10.0,
            "wind_direction": 180,
            "condition": "clear",
            "description": "clear sky",
            "pressure": 1013,
            "visibility": 10000,
            "timestamp": datetime.utcnow(),
            "mock_data": True
        }

    def _get_mock_forecast(self, lat: float, lon: float, days: int) -> List[Dict]:
        """Return mock forecast data"""
        forecasts = []
        for i in range(days):
            forecasts.append({
                "date": (datetime.utcnow().replace(hour=12) + timedelta(days=i)).isoformat(),
                "temperature": 25.0 + (i * 2),
                "condition": "clear" if i % 2 == 0 else "cloudy",
                "wind_speed": 10.0,
                "humidity": 60,
                "mock_data": True
            })
        return forecasts

class GoogleMapsAPIClient:
    """Client for Google Maps API integration"""

    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api"

    async def get_directions(self, origin: str, destination: str, mode: str = "driving") -> Optional[Dict]:
        """Get route directions from Google Maps"""
        if not self.api_key:
            logger.warning("Google Maps API key not configured, using mock data")
            return self._get_mock_directions(origin, destination)

        try:
            url = f"{self.base_url}/directions/json"
            params = {
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "key": self.api_key,
                "alternatives": "true",
                "avoid": "tolls"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=15)

                if response.status_code == 200:
                    data = response.json()

                    if data["status"] == "OK" and data["routes"]:
                        route = data["routes"][0]
                        leg = route["legs"][0]

                        return {
                            "distance_km": leg["distance"]["value"] / 1000,
                            "distance_text": leg["distance"]["text"],
                            "duration_minutes": leg["duration"]["value"] / 60,
                            "duration_text": leg["duration"]["text"],
                            "start_address": leg["start_address"],
                            "end_address": leg["end_address"],
                            "polyline": route["overview_polyline"]["points"],
                            "bounds": route["bounds"],
                            "steps": len(leg["steps"]),
                            "warnings": route.get("warnings", []),
                            "timestamp": datetime.utcnow()
                        }
                    else:
                        logger.error(f"Google Maps API status: {data.get('status')}")
                        return self._get_mock_directions(origin, destination)
                else:
                    logger.error(f"Google Maps API error: {response.status_code}")
                    return self._get_mock_directions(origin, destination)

        except Exception as e:
            logger.error(f"Error fetching directions: {e}")
            return self._get_mock_directions(origin, destination)

    async def get_elevation_profile(self, path_points: List[Tuple[float, float]]) -> List[Dict]:
        """Get elevation profile for route points"""
        if not self.api_key:
            return self._get_mock_elevation(path_points)

        try:
            url = f"{self.base_url}/elevation/json"

            # Format path points for API
            path_str = "|".join([f"{lat},{lon}" for lat, lon in path_points])
            params = {
                "path": path_str,
                "samples": min(512, len(path_points)),
                "key": self.api_key
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=15)

                if response.status_code == 200:
                    data = response.json()

                    if data["status"] == "OK":
                        elevations = []
                        for i, result in enumerate(data["results"]):
                            elevations.append({
                                "lat": result["location"]["lat"],
                                "lon": result["location"]["lng"],
                                "elevation": result["elevation"],
                                "resolution": result.get("resolution", 1.0),
                                "distance_from_start": i * 1000 / len(data["results"])  # Rough estimate
                            })
                        return elevations
                    else:
                        return self._get_mock_elevation(path_points)
                else:
                    return self._get_mock_elevation(path_points)

        except Exception as e:
            logger.error(f"Error fetching elevation data: {e}")
            return self._get_mock_elevation(path_points)

    async def geocode(self, address: str) -> Optional[Dict]:
        """Geocode an address to get coordinates"""
        if not self.api_key:
            return self._get_mock_geocode(address)

        try:
            url = f"{self.base_url}/geocode/json"
            params = {
                "address": address,
                "key": self.api_key
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    if data["status"] == "OK" and data["results"]:
                        result = data["results"][0]
                        location = result["geometry"]["location"]

                        return {
                            "address": result["formatted_address"],
                            "lat": location["lat"],
                            "lon": location["lng"],
                            "place_id": result["place_id"],
                            "types": result["types"]
                        }
                    else:
                        return self._get_mock_geocode(address)
                else:
                    return self._get_mock_geocode(address)

        except Exception as e:
            logger.error(f"Error geocoding address: {e}")
            return self._get_mock_geocode(address)

    def _get_mock_directions(self, origin: str, destination: str) -> Dict:
        """Mock directions data"""
        # Mock data for Mumbai to Pune route
        return {
            "distance_km": 148.5,
            "distance_text": "149 km",
            "duration_minutes": 180,
            "duration_text": "3 hours",
            "start_address": origin,
            "end_address": destination,
            "polyline": "mock_polyline_encoded_string",
            "bounds": {"northeast": {"lat": 19.0760, "lng": 73.8567}, "southwest": {"lat": 18.5204, "lng": 72.8777}},
            "steps": 25,
            "warnings": [],
            "timestamp": datetime.utcnow(),
            "mock_data": True
        }

    def _get_mock_elevation(self, path_points: List[Tuple[float, float]]) -> List[Dict]:
        """Mock elevation data"""
        elevations = []
        for i, (lat, lon) in enumerate(path_points):
            elevations.append({
                "lat": lat,
                "lon": lon,
                "elevation": 500 + (i * 10) - (i * i * 0.5),  # Simulated elevation profile
                "resolution": 1.0,
                "distance_from_start": i * 1000,
                "mock_data": True
            })
        return elevations

    def _get_mock_geocode(self, address: str) -> Dict:
        """Mock geocoding data"""
        return {
            "address": f"Mock location for {address}",
            "lat": 19.0760,
            "lon": 72.8777,
            "place_id": "mock_place_id",
            "types": ["locality", "political"],
            "mock_data": True
        }

class ElevationAPIClient:
    """Alternative elevation API client (Open-Elevation)"""

    def __init__(self):
        self.base_url = "https://api.open-elevation.com/api/v1"

    async def get_elevation(self, coordinates: List[Tuple[float, float]]) -> List[Dict]:
        """Get elevation for list of coordinates"""
        try:
            locations = [{"latitude": lat, "longitude": lon} for lat, lon in coordinates]

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/lookup",
                    json={"locations": locations[:100]},  # API limit
                    timeout=15
                )

                if response.status_code == 200:
                    data = response.json()

                    elevations = []
                    for i, result in enumerate(data["results"]):
                        elevations.append({
                            "lat": result["latitude"],
                            "lon": result["longitude"], 
                            "elevation": result["elevation"],
                            "distance_from_start": i * 1000,
                            "source": "open-elevation"
                        })
                    return elevations
                else:
                    return self._get_mock_elevation(coordinates)

        except Exception as e:
            logger.error(f"Error fetching elevation from Open-Elevation: {e}")
            return self._get_mock_elevation(coordinates)

    def _get_mock_elevation(self, coordinates: List[Tuple[float, float]]) -> List[Dict]:
        """Mock elevation data"""
        elevations = []
        for i, (lat, lon) in enumerate(coordinates):
            elevations.append({
                "lat": lat,
                "lon": lon,
                "elevation": 300 + (i * 5),
                "distance_from_start": i * 1000,
                "source": "mock",
                "mock_data": True
            })
        return elevations

# Initialize client instances
weather_client = WeatherAPIClient()
maps_client = GoogleMapsAPIClient()
elevation_client = ElevationAPIClient()
