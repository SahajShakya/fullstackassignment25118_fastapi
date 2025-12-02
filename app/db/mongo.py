from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection settings
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:sahaj1@mongo:27017")
DB_NAME = os.getenv("DB_NAME", "assignment")

# Global Mongo client and database
client = None
db: AsyncIOMotorDatabase = None


async def connect_to_mongo():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DB_NAME]
        await db.command("ping")
        print(f"✓ Connected to MongoDB: {DB_NAME}")
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("✓ Closed MongoDB connection")


def get_collection(name: str):
    if db is None:
        raise RuntimeError("Database not connected. Call connect_to_mongo() first.")
    return db[name]
