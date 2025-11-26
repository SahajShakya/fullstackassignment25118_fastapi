

def upgrade(db):
    """Create stores collection with schema"""
    existing = db.list_collection_names()
    
    if "stores" not in existing:
        db.create_collection(
            "stores",
            validator={
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
        )
        print("✓ Created stores collection")
    
    # Create indexes
    db.stores.create_index("name")
    db.stores.create_index("created_at")
    print("✓ Created stores indexes")


def downgrade(db):
    """Drop stores collection"""
    try:
        db.stores.drop()
        print("✓ Dropped stores collection")
    except:
        pass