from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import motor.motor_asyncio
import redis.asyncio as aioredis
from datetime import datetime, timedelta
import jwt
import bcrypt
import json
import random
from contextlib import asynccontextmanager

# ===================== CONFIGURATION =====================
SECRET_KEY = "smartswapml-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

MONGODB_URL = "mongodb://mongodb:27017"
DATABASE_NAME = "smartswapml"
REDIS_URL = "redis://redis:6379"

# ===================== PYDANTIC MODELS =====================
class Battery(BaseModel):
    id: str
    health: float
    soc: float
    cycles: int
    temp: float
    location: str
    status: str
    timestamp: datetime = datetime.utcnow()

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
    username: str
    password: str
    role: str = "user"

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str

# ===================== GLOBALS =====================
redis_client = None
mongo_client = None
database = None

# ===================== STARTUP / SHUTDOWN =====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client, mongo_client, database
    try:
        redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
        database = mongo_client[DATABASE_NAME]
        await initialize_sample_data()
        await ensure_demo_user()
        print("Connected to MongoDB and Redis successfully")
    except Exception as e:
        print(f"Startup error: {e}")
    yield
    if redis_client:
        await redis_client.close()
    if mongo_client:
        mongo_client.close()

async def initialize_sample_data():
    """Insert sample batteries and stations if collections are empty."""
    if await database.batteries.count_documents({}) == 0:
        sample_batteries = [
            {"id": "BAT001", "health": 95, "soc": 87, "cycles": 245, "temp": 32, "location": "Mumbai", "status": "active", "timestamp": datetime.utcnow()},
            {"id": "BAT002", "health": 87, "soc": 72, "cycles": 567, "temp": 28, "location": "Pune", "status": "active", "timestamp": datetime.utcnow()},
            {"id": "BAT003", "health": 92, "soc": 91, "cycles": 123, "temp": 30, "location": "Bangalore", "status": "charging", "timestamp": datetime.utcnow()},
            {"id": "BAT004", "health": 78, "soc": 45, "cycles": 892, "temp": 35, "location": "Chennai", "status": "maintenance", "timestamp": datetime.utcnow()}
        ]
        await database.batteries.insert_many(sample_batteries)

    if await database.stations.count_documents({}) == 0:
        sample_stations = [
            {"id": "ST001", "name": "Mumbai Central", "lat": 19.0760, "lng": 72.8777, "batteries": 24, "utilization": 85, "status": "active"},
            {"id": "ST002", "name": "Pune Highway", "lat": 18.5204, "lng": 73.8567, "batteries": 18, "utilization": 72, "status": "active"},
            {"id": "ST003", "name": "Bangalore Tech Park", "lat": 12.9716, "lng": 77.5946, "batteries": 32, "utilization": 91, "status": "active"}
        ]
        await database.stations.insert_many(sample_stations)

async def ensure_demo_user():
    """Ensure demo user exists in users collection."""
    existing_user = await database.users.find_one({"username": "demo"})
    if not existing_user:
        hashed_password = bcrypt.hashpw("demo123".encode(), bcrypt.gensalt()).decode()
        await database.users.insert_one({"username": "demo", "password": hashed_password, "role": "admin"})
        print("Demo user created: demo/demo123")

# ===================== FASTAPI APP =====================
app = FastAPI(
    title="SmartSwapML API",
    description="Intelligent Battery Management System API",
    version="1.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# ===================== AUTH HELPERS =====================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"):
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ===================== ROUTES =====================
@app.get("/")
async def root():
    return {"message": "SmartSwapML API running", "version": "1.1.0"}

@app.post("/auth/login", response_model=Token)
async def login(login_request: LoginRequest):
    user = await database.users.find_one({"username": login_request.username})
    if user and bcrypt.checkpw(login_request.password.encode(), user["password"].encode()):
        token = create_access_token(data={"sub": user["username"], "role": user.get("role", "user")})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/batteries", response_model=List[Battery])
async def get_batteries(token_data: dict = Depends(verify_token)):
    cached = await redis_client.get("batteries_cache")
    if cached:
        return [Battery(**b) for b in json.loads(cached)]
    batteries = []
    async for doc in database.batteries.find({}):
        doc.pop("_id", None)
        batteries.append(Battery(**doc))
    await redis_client.setex("batteries_cache", 30, json.dumps([b.dict() for b in batteries], default=str))
    return batteries

@app.get("/api/stations", response_model=List[Station])
async def get_stations(token_data: dict = Depends(verify_token)):
    cached = await redis_client.get("stations_cache")
    if cached:
        return [Station(**s) for s in json.loads(cached)]
    stations = []
    async for doc in database.stations.find({}):
        doc.pop("_id", None)
        stations.append(Station(**doc))
    await redis_client.setex("stations_cache", 60, json.dumps([s.dict() for s in stations], default=str))
    return stations

@app.post("/api/routes", response_model=Route)
async def create_route(route: Route, token_data: dict = Depends(verify_token)):
    await database.routes.insert_one(route.dict())
    return route

@app.get("/api/routes", response_model=List[Route])
async def get_routes(token_data: dict = Depends(verify_token)):
    routes = []
    async for doc in database.routes.find({}):
        doc.pop("_id", None)
        routes.append(Route(**doc))
    return routes

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)