"""
Migration: Create users collection
Generated from User model
"""


def upgrade(db):
    """Create users collection with schema"""
    existing = db.list_collection_names()
    
    if "users" not in existing:
        db.create_collection(
            "users",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["username", "password", "display_name"],
                    "properties": {
                        "_id": {"bsonType": "objectId"},
                        "username": {"bsonType": "string"},
                        "password": {"bsonType": "string"},
                        "display_name": {"bsonType": "string"},
                        "created_at": {"bsonType": "date"},
                        "last_login": {"bsonType": ["date", "null"]},
                        "active": {"bsonType": "bool"}
                    }
                }
            }
        )
        print("✓ Created users collection")
    
    # Create indexes
    db.users.create_index("username", unique=True)
    db.users.create_index("created_at")
    print("✓ Created users indexes")


def downgrade(db):
    """Drop users collection"""
    try:
        db.users.drop()
        print("✓ Dropped users collection")
    except:
        pass
