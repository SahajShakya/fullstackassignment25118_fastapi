from pymongo import MongoClient
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.config import settings

MONGO_URI = settings.MONGO_URI
DB_NAME = settings.DB_NAME

stores_data = [
    {
        "name": "Electronics Store",
        "description": "A store with laptops, mice, and keyboards",
        "image_url": "../media/stores/electronics_store.jpg",
        "models": [
            {
                "name": "Laptop",
                "glb_url": "/media/models/laptop.glb",
                "position": [50, 120],
                "size": [0.5, 0.5, 0.5],
                "entrance_order": 1
            },
            {
                "name": "Mouse",
                "glb_url": "../media/models/mouse.glb",
                "position": [200, 180],
                "size": [0.3, 0.3, 0.3],
                "entrance_order": 2
            },
            {
                "name": "Keyboard",
                "glb_url": "../media/models/keyboard.glb",
                "position": [350, 150],
                "size": [0.4, 0.4, 0.4],
                "entrance_order": 3
            }
        ],
        "active_sessions": [],
        "active_user_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "name": "Gadget World",
        "description": "Store with smartphones, headphones, and cameras",
        "image_url": "../media/stores/gadget_store.jpg",
        "models": [
            {
                "name": "Smartphone",
                "glb_url": "../media/models/smartphone.glb",
                "position": [60, 100],
                "size": [0.4, 0.4, 0.4],
                "entrance_order": 1
            },
            {
                "name": "Headphones",
                "glb_url": "../media/models/headphones.glb",
                "position": [220, 140],
                "size": [0.3, 0.3, 0.3],
                "entrance_order": 2
            },
            {
                "name": "Camera",
                "glb_url": "../media/models/camera.glb",
                "position": [320, 180],
                "size": [0.5, 0.5, 0.5],
                "entrance_order": 3
            }
        ],
        "active_sessions": [],
        "active_user_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]


def seed_stores():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    for store in stores_data:
        if db.stores.find_one({"name": store["name"]}) is None:
            db.stores.insert_one(store)
            print(f"✓ Inserted store: {store['name']}")
        else:
            print(f"⚠ Store already exists: {store['name']}")

    print("Seeding completed!")


if __name__ == "__main__":
    seed_stores()
