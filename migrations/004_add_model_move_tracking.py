from datetime import datetime

def upgrade(db):
    """
    Add move tracking to model documents.
    Adds 'last_moved_by' (user_id) and 'last_moved_at' (timestamp) to track who moved what and when.
    """
    stores_collection = db.stores
    
    # Get all stores
    stores = stores_collection.find({})
    
    for store in stores:
        models = store.get("models", [])
        
        # Update each model to add tracking fields if not present
        for i, model in enumerate(models):
            if "last_moved_by" not in model or "last_moved_at" not in model:
                stores_collection.update_one(
                    {"_id": store["_id"]},
                    {
                        "$set": {
                            f"models.{i}.last_moved_by": "system",
                            f"models.{i}.last_moved_at": datetime.utcnow()
                        }
                    }
                )
    
    print("✓ Added model move tracking fields (last_moved_by, last_moved_at)")


def downgrade(db):
    """Revert to previous schema (remove model tracking fields)"""
    stores_collection = db.stores
    
    # Remove tracking fields from all models
    stores_collection.update_many(
        {},
        {
            "$unset": {
                "models[].last_moved_by": "",
                "models[].last_moved_at": ""
            }
        }
    )
    
    print("✓ Removed model move tracking fields")
