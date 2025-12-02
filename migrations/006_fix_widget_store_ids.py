"""
Migration to fix widget store_ids that are still 'default'.
This updates any widgets with store_id='default' to use the first available store.
"""


def upgrade(db):
    """Update widgets with default store_id to use first store ID"""
    # Get first store
    first_store = db.stores.find_one()
    if not first_store:
        print("❌ No stores found in database")
        return
    
    store_id = str(first_store["_id"])
    print(f"✓ Using store ID: {store_id} ({first_store.get('name', 'Unknown')})")
    
    # Find all widgets with default store_id
    widgets_with_default = list(db.widget_configs.find({"store_id": "default"}))
    print(f"✓ Found {len(widgets_with_default)} widgets with store_id='default'")
    
    if len(widgets_with_default) > 0:
        # Update them
        result = db.widget_configs.update_many(
            {"store_id": "default"},
            {"$set": {"store_id": store_id}}
        )
        print(f"✓ Updated {result.modified_count} widgets")
        
        # Also update analytics events
        analytics_with_default = list(db.widget_analytics.find({"store_id": "default"}))
        print(f"✓ Found {len(analytics_with_default)} analytics events with store_id='default'")
        
        if len(analytics_with_default) > 0:
            result = db.widget_analytics.update_many(
                {"store_id": "default"},
                {"$set": {"store_id": store_id}}
            )
            print(f"✓ Updated {result.modified_count} analytics events")
    else:
        print("✓ No widgets with store_id='default' found")
    
    print("✓ Migration complete!")


def downgrade(db):
    """Revert migration - update store_id back to 'default'"""
    # This is just a safety function; in practice you wouldn't want to revert this
    print("⚠ Downgrade not recommended for this migration")
