"""
Migration to fix widget store_ids that are still 'default'.
This updates any widgets with store_id='default' to use the first available store.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB_NAME", "assignment")


async def migrate():
    """Update widgets with default store_id to use first store ID"""
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Get first store
    first_store = await db.stores.find_one()
    if not first_store:
        print("❌ No stores found in database")
        return
    
    store_id = str(first_store["_id"])
    print(f"✓ Using store ID: {store_id} ({first_store.get('name', 'Unknown')})")
    
    # Find all widgets with default store_id
    widgets_with_default = await db.widget_configs.find({"store_id": "default"}).to_list(None)
    print(f"✓ Found {len(widgets_with_default)} widgets with store_id='default'")
    
    if len(widgets_with_default) > 0:
        # Update them
        result = await db.widget_configs.update_many(
            {"store_id": "default"},
            {"$set": {"store_id": store_id}}
        )
        print(f"✓ Updated {result.modified_count} widgets")
        
        # Also update analytics events
        analytics_with_default = await db.widget_analytics.find({"store_id": "default"}).to_list(None)
        print(f"✓ Found {len(analytics_with_default)} analytics events with store_id='default'")
        
        if len(analytics_with_default) > 0:
            result = await db.widget_analytics.update_many(
                {"store_id": "default"},
                {"$set": {"store_id": store_id}}
            )
            print(f"✓ Updated {result.modified_count} analytics events")
    else:
        print("✓ No widgets with store_id='default' found")
    
    client.close()
    print("✓ Migration complete!")


if __name__ == "__main__":
    asyncio.run(migrate())
