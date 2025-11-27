def upgrade(db):
    """
    Create widget_configs and widget_analytics collections with indices.
    """
    # Create widget_configs collection
    try:
        db.create_collection("widget_configs")
        print("✓ Created widget_configs collection")
    except Exception as e:
        print(f"✓ widget_configs collection already exists: {e}")
    
    # Drop old unique index on domain if it exists
    try:
        db.widget_configs.drop_index("domain_1")
        print("✓ Dropped old domain unique index")
    except Exception as e:
        print(f"✓ Old domain index doesn't exist or error: {e}")
    
    # Create new indices for widget_configs
    # Compound unique index on (store_id, domain)
    db.widget_configs.create_index([("store_id", 1), ("domain", 1)], unique=True)
    db.widget_configs.create_index("is_active")
    db.widget_configs.create_index("store_id")
    print("✓ Created indices for widget_configs")
    
    # Create widget_analytics collection
    try:
        db.create_collection("widget_analytics")
        print("✓ Created widget_analytics collection")
    except Exception as e:
        print(f"✓ widget_analytics collection already exists: {e}")
    
    # Create indices for widget_analytics
    db.widget_analytics.create_index([("store_id", -1), ("timestamp", -1)])
    db.widget_analytics.create_index([("domain", -1), ("timestamp", -1)])
    db.widget_analytics.create_index("event_type")
    print("✓ Created indices for widget_analytics")
    
    print("✓ Widget collections and indices created successfully")


def downgrade(db):
    """Revert widget collections"""
    db.widget_configs.drop()
    db.widget_analytics.drop()
    print("✓ Dropped widget_configs and widget_analytics collections")
