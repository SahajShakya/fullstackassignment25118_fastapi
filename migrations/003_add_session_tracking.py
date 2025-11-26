def upgrade(db):
    """
    Add session-based user tracking to stores collection.
    Replace 'active_users' with 'active_sessions' and 'active_user_count'.
    """
    stores_collection = db.stores
    
    # Get all existing stores
    stores = stores_collection.find({})
    
    for store in stores:
        # Initialize new fields if not present
        update_data = {}
        
        # Add active_sessions array if not present
        if "active_sessions" not in store:
            update_data["active_sessions"] = []
        
        # Add active_user_count if not present
        if "active_user_count" not in store:
            update_data["active_user_count"] = 0
        
        # Remove old 'active_users' field (legacy)
        if "active_users" in store:
            update_data["active_users"] = None  # Will be removed with $unset
        
        # Perform update if needed
        if update_data:
            if "active_users" in update_data:
                # Use $unset to remove and $set to add
                stores_collection.update_one(
                    {"_id": store["_id"]},
                    {
                        "$unset": {"active_users": ""},
                        "$set": {
                            k: v for k, v in update_data.items() 
                            if k != "active_users"
                        }
                    }
                )
            else:
                stores_collection.update_one(
                    {"_id": store["_id"]},
                    {"$set": update_data}
                )
    
    # Update schema validation
    db.command({
        "collMod": "stores",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name"],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "name": {"bsonType": "string"},
                    "description": {"bsonType": "string"},
                    "image_url": {"bsonType": "string"},
                    "models": {"bsonType": "array"},
                    "active_sessions": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "properties": {
                                "session_id": {"bsonType": "string"},
                                "user_id": {"bsonType": "string"},
                                "entered_at": {"bsonType": "date"},
                                "last_heartbeat": {"bsonType": "date"}
                            }
                        }
                    },
                    "active_user_count": {"bsonType": "int"},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"}
                }
            }
        }
    })
    
    print("✓ Added session tracking to stores collection")
    print("✓ Updated schema validation")


def downgrade(db):
    """Revert to previous schema (remove session tracking)"""
    stores_collection = db.stores
    
    # Remove new fields
    stores_collection.update_many(
        {},
        {
            "$unset": {
                "active_sessions": "",
                "active_user_count": ""
            }
        }
    )
    
    # Restore old schema
    db.command({
        "collMod": "stores",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name"],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "name": {"bsonType": "string"},
                    "description": {"bsonType": "string"},
                    "image_url": {"bsonType": "string"},
                    "models": {"bsonType": "array"},
                    "active_users": {"bsonType": "array"},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"}
                }
            }
        }
    })
    
    print("✓ Reverted session tracking changes")
