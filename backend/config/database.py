import logging
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as aioredis
from typing import Optional

from .settings import settings

logger = logging.getLogger(__name__)

# MongoDB connection
class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

mongodb = MongoDB()

# Redis connection
redis_client: Optional[aioredis.Redis] = None

async def connect_to_mongo():
    """Create database connection"""
    try:
        mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb.database = mongodb.client.get_default_database()

        # Test connection
        await mongodb.client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")

        # Create indexes
        await create_indexes()

    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise

async def connect_to_redis():
    """Create Redis connection"""
    global redis_client
    try:
        redis_client = aioredis.from_url(settings.REDIS_URL)

        # Test connection
        await redis_client.ping()
        logger.info("Connected to Redis successfully")

    except Exception as e:
        logger.error(f"Could not connect to Redis: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("Disconnected from MongoDB")

async def close_redis_connection():
    """Close Redis connection"""
    if redis_client:
        await redis_client.close()
        logger.info("Disconnected from Redis")

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Battery collection indexes
        await mongodb.database.batteries.create_index("battery_id")
        await mongodb.database.batteries.create_index("station_id")
        await mongodb.database.batteries.create_index("last_updated")

        # Station collection indexes  
        await mongodb.database.stations.create_index("station_id")
        await mongodb.database.stations.create_index([("location.coordinates", "2dsphere")])

        # User collection indexes
        await mongodb.database.users.create_index("username", unique=True)
        await mongodb.database.users.create_index("email", unique=True)

        logger.info("Database indexes created successfully")

    except Exception as e:
        logger.warning(f"Could not create indexes: {e}")

# Database connection functions
async def get_database():
    """Get database instance"""
    return mongodb.database

async def get_redis():
    """Get Redis client instance"""
    return redis_client
