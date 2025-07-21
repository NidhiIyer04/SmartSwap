from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import redis
import motor.motor_asyncio
from datetime import datetime, timedelta
import jwt
import bcrypt
import json
import asyncio
import random
from contextlib import asynccontextmanager

# Configuration
SECRET_KEY = "smartswapml-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# MongoDB Configuration
MONGODB_URL = "mongodb://mongodb:27017"
DATABASE_NAME = "smartswapml"

# Redis Configuration  
REDIS_URL = "redis://redis:6379"

# Pydantic Models
class Battery(BaseModel):
    id: str
    health: float
    soc: float
    cycles: int
    temp: float
    location: str
    status: str
    timestamp: datetime = datetime.now()

class Station(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    batteries: int
    utilization: float
    status: str = "active"

class Route(BaseModel):
    id: str
    from_location: str
    to_location: str
    distance: float
    elevation_gain: float
    predicted_range: float
    confidence: float
    weather_impact: float

class User(BaseModel):
    id: str
    username: str
    role: str
    language: str = "en"

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str

# Global variables for connections
redis_client = None
mongo_client = None
database = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global redis_client, mongo_client, database
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
        database = mongo_client[DATABASE_NAME]

        # Initialize sample data
        await initialize_sample_data()

        print("Connected to MongoDB and Redis successfully")
    except Exception as e:
        print(f"Failed to connect to databases: {e}")

    yield

    # Shutdown
    if redis_client:
        redis_client.close()
    if mongo_client:
        mongo_client.close()

async def initialize_sample_data():
    """Initialize the database with sample data"""
    try:
        # Sample batteries data
        sample_batteries = [
            {"id": "BAT001", "health": 95, "soc": 87, "cycles": 245, "temp": 32, "location": "Mumbai", "status": "active", "timestamp": datetime.now()},
            {"id": "BAT002", "health": 87, "soc": 72, "cycles": 567, "temp": 28, "location": "Pune", "status": "active", "timestamp": datetime.now()},
            {"id": "BAT003", "health": 92, "soc": 91, "cycles": 123, "temp": 30, "location": "Bangalore", "status": "charging", "timestamp": datetime.now()},
            {"id": "BAT004", "health": 78, "soc": 45, "cycles": 892, "temp": 35, "location": "Chennai", "status": "maintenance", "timestamp": datetime.now()}
        ]

        # Sample stations data
        sample_stations = [
            {"id": "ST001", "name": "Mumbai Central", "lat": 19.0760, "lng": 72.8777, "batteries": 24, "utilization": 85, "status": "active"},
            {"id": "ST002", "name": "Pune Highway", "lat": 18.5204, "lng": 73.8567, "batteries": 18, "utilization": 72, "status": "active"},
            {"id": "ST003", "name": "Bangalore Tech Park", "lat": 12.9716, "lng": 77.5946, "batteries": 32, "utilization": 91, "status": "active"}
        ]

        # Clear existing collections
        await database.batteries.delete_many({})
        await database.stations.delete_many({})

        # Insert sample data
        await database.batteries.insert_many(sample_batteries)
        await database.stations.insert_many(sample_stations)

        print("Sample data initialized successfully")
    except Exception as e:
        print(f"Failed to initialize sample data: {e}")

app = FastAPI(
    title="SmartSwapML API",
    description="Intelligent Battery Management System API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Helper Functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# API Routes
@app.get("/")
async def root():
    return {"message": "SmartSwapML API is running", "version": "1.0.0"}

@app.post("/auth/login", response_model=Token)
async def login(login_request: LoginRequest):
    # Simple demo authentication - replace with real user validation
    if login_request.username == "demo" and login_request.password == "demo123":
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": login_request.username, "role": "admin"}, 
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/batteries", response_model=List[Battery])
async def get_batteries(token_data: dict = Depends(verify_token)):
    try:
        # Try to get from cache first
        cached_data = redis_client.get("batteries_cache")
        if cached_data:
            batteries_data = json.loads(cached_data)
            return [Battery(**battery) for battery in batteries_data]

        # If not in cache, get from MongoDB
        cursor = database.batteries.find({})
        batteries = []
        async for document in cursor:
            document['_id'] = str(document['_id'])
            batteries.append(Battery(**document))

        # Cache for 30 seconds
        redis_client.setex("batteries_cache", 30, json.dumps([battery.dict() for battery in batteries], default=str))

        return batteries
    except Exception as e:
        print(f"Error fetching batteries: {e}")
        return []

@app.get("/api/batteries/{battery_id}", response_model=Battery)
async def get_battery(battery_id: str, token_data: dict = Depends(verify_token)):
    try:
        # Check cache first
        cached_data = redis_client.get(f"battery_{battery_id}")
        if cached_data:
            battery_data = json.loads(cached_data)
            return Battery(**battery_data)

        # Get from MongoDB
        document = await database.batteries.find_one({"id": battery_id})
        if not document:
            raise HTTPException(status_code=404, detail="Battery not found")

        document['_id'] = str(document['_id'])
        battery = Battery(**document)

        # Cache for 30 seconds
        redis_client.setex(f"battery_{battery_id}", 30, json.dumps(battery.dict(), default=str))

        return battery
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching battery {battery_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/stations", response_model=List[Station])
async def get_stations(token_data: dict = Depends(verify_token)):
    try:
        cached_data = redis_client.get("stations_cache")
        if cached_data:
            stations_data = json.loads(cached_data)
            return [Station(**station) for station in stations_data]

        cursor = database.stations.find({})
        stations = []
        async for document in cursor:
            document['_id'] = str(document['_id'])
            stations.append(Station(**document))

        redis_client.setex("stations_cache", 60, json.dumps([station.dict() for station in stations]))
        return stations
    except Exception as e:
        print(f"Error fetching stations: {e}")
        return []

@app.get("/api/route-optimization")
async def get_route_optimization(
    from_loc: str, 
    to_loc: str, 
    battery_id: Optional[str] = None,
    token_data: dict = Depends(verify_token)
):
    try:
        # Simulate route optimization with ML predictions
        distance = random.randint(50, 500)
        elevation_gain = random.randint(100, 1000)
        predicted_range = distance * 0.95 + random.randint(-20, 10)
        confidence = random.randint(85, 98)
        weather_impact = random.randint(-15, 5)

        route_data = {
            "id": f"ROUTE_{from_loc}_{to_loc}",
            "from_location": from_loc,
            "to_location": to_loc,
            "distance": distance,
            "elevation_gain": elevation_gain,
            "predicted_range": predicted_range,
            "confidence": confidence,
            "weather_impact": weather_impact,
            "recommendations": [
                "Consider charging at intermediate station",
                "Weather conditions are favorable",
                "Terrain difficulty: Moderate"
            ]
        }

        return route_data
    except Exception as e:
        print(f"Error in route optimization: {e}")
        raise HTTPException(status_code=500, detail="Route optimization failed")

@app.get("/api/analytics/circular-economy")
async def get_circular_economy_data(token_data: dict = Depends(verify_token)):
    try:
        data = {
            "materials": {
                "lithium": {"recovered": 78, "target": 85, "trend": "up"},
                "cobalt": {"recovered": 85, "target": 90, "trend": "stable"},
                "nickel": {"recovered": 92, "target": 95, "trend": "up"}
            },
            "carbon_savings": {
                "total_co2_reduced": 2.3,
                "energy_recovered": 1247,
                "waste_diverted": 89.4
            },
            "second_life_applications": [
                {"application": "Home Energy Storage", "percentage": 45},
                {"application": "Grid Stabilization", "percentage": 30},
                {"application": "Commercial Backup", "percentage": 25}
            ]
        }
        return data
    except Exception as e:
        print(f"Error fetching circular economy data: {e}")
        return {}

@app.get("/api/analytics/ml-performance")
async def get_ml_performance(token_data: dict = Depends(verify_token)):
    try:
        data = {
            "models": {
                "battery_health_prediction": {
                    "accuracy": 94.7,
                    "mape": 3.2,
                    "last_updated": datetime.now().isoformat()
                },
                "range_optimization": {
                    "accuracy": 92.1,
                    "mape": 5.8,
                    "last_updated": datetime.now().isoformat()
                },
                "demand_forecasting": {
                    "accuracy": 87.3,
                    "mape": 8.4,
                    "last_updated": datetime.now().isoformat()
                }
            },
            "data_quality": {
                "completeness": 96.2,
                "accuracy": 94.1,
                "freshness": 98.7
            }
        }
        return data
    except Exception as e:
        print(f"Error fetching ML performance data: {e}")
        return {}

@app.get("/api/weather/{location}")
async def get_weather(location: str, token_data: dict = Depends(verify_token)):
    try:
        # Mock weather data - replace with real weather API
        weather_data = {
            "location": location,
            "temperature": random.randint(20, 35),
            "humidity": random.randint(40, 90),
            "wind_speed": random.randint(5, 25),
            "condition": random.choice(["sunny", "cloudy", "rainy"]),
            "range_impact": random.randint(-15, 5)
        }
        return weather_data
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return {}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
