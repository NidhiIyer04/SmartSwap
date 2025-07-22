from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from config.settings import settings
from routers import auth, batteries, routes, stations, analytics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SmartSwapML Backend",
    description="Advanced EV Battery Swap Intelligence Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(batteries.router, prefix="/api/batteries", tags=["Battery Management"])
app.include_router(routes.router, prefix="/api/routes", tags=["Route Optimization"])
app.include_router(stations.router, prefix="/api/stations", tags=["Station Management"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    return {"message": "SmartSwapML Backend API", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if settings.MONGODB_URL else "not configured",
        "cache": "connected" if settings.REDIS_URL else "not configured",
        "weather_api": "configured" if settings.OPENWEATHER_API_KEY else "not configured",
        "maps_api": "configured" if settings.GOOGLE_MAPS_API_KEY else "not configured"
    }

@app.get("/info")
async def get_info():
    return {
        "app_name": "SmartSwapML",
        "version": "1.0.0",
        "features": [
            "Battery Health Prediction",
            "Terrain-Aware Route Optimization", 
            "Circular Economy Tracking",
            "Smart Station Placement"
        ],
        "api_integrations": {
            "weather": bool(settings.OPENWEATHER_API_KEY),
            "maps": bool(settings.GOOGLE_MAPS_API_KEY),
            "elevation": bool(settings.ELEVATION_API_KEY)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
