"""
PyMongo Migrate Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection string
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "store_visualization_db")

# Migration directory
MIGRATION_DIR = "migrations"

# Migrations collection name (tracks applied migrations)
MIGRATIONS_COLLECTION = "alembic_version"


def get_database():
    """Get MongoDB database connection"""
    from pymongo import MongoClient
    
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db
