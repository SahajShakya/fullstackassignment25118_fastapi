"""
  python manage.py migrate        - Run all pending migrations
  python manage.py migrate:status - Show migration status
  python manage.py status         - Check database status
"""
import asyncio
import sys
import logging
from pathlib import Path
import os
import datetime
import time
import importlib.util
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))
os.chdir(Path(__file__).parent)

from app.db.mongo import db  # async db client for seeding/reset

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_mongo_client(retries=10, delay=3):
    """Return a MongoClient and wait for MongoDB to be ready."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:sahaj1@mongo:27017/assignment")
    for attempt in range(retries):
        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            client.admin.command("ping")  # test connection
            return client
        except ServerSelectionTimeoutError:
            logger.warning(f"MongoDB not ready, retrying in {delay}s... ({attempt + 1}/{retries})")
            time.sleep(delay)
    logger.error("Cannot connect to MongoDB after multiple attempts")
    sys.exit(1)


def run_migrations():
    logger.info("=" * 60)
    logger.info("Running MongoDB Migrations (pymongo-migrate)")
    logger.info("=" * 60)
    try:
        db_name = os.getenv("DB_NAME", "assignment")
        client = get_mongo_client()
        db_connection = client[db_name]

        migrations_dir = Path("migrations")
        migration_files = sorted(migrations_dir.glob("*.py"))

        migrations_collection = db_connection.alembic_version

        for migration_file in migration_files:
            if migration_file.name.startswith("__"):
                continue

            migration_name = migration_file.stem

            if migrations_collection.find_one({"version": migration_name}):
                logger.info(f"⊘ Already applied: {migration_name}")
                continue

            spec = importlib.util.spec_from_file_location(migration_name, migration_file)
            migration_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration_module)

            logger.info(f"↻ Running: {migration_name}")
            migration_module.upgrade(db_connection)

            migrations_collection.insert_one({
                "version": migration_name,
                "applied_at": datetime.datetime.utcnow()
            })

            logger.info(f"✓ Applied: {migration_name}")

        logger.info("=" * 60)
        logger.info("✓ Migrations completed successfully")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"✗ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def migration_status():
    logger.info("=" * 60)
    logger.info("Migration Status")
    logger.info("=" * 60)
    try:
        db_name = os.getenv("DB_NAME", "assignment")
        client = get_mongo_client()
        db_connection = client[db_name]

        migrations = list(db_connection.alembic_version.find({}))

        if not migrations:
            logger.info("No migrations have been run yet")
        else:
            logger.info(f"Applied migrations ({len(migrations)}):")
            for i, migration in enumerate(migrations, 1):
                logger.info(f"  {i}. {migration.get('version', 'unknown')}")

        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"✗ Status check failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def seed_database():
    logger.info("=" * 60)
    logger.info("Seeding sample data...")
    logger.info("=" * 60)
    try:
        await seed_sample_data(db)
        logger.info("=" * 60)
        logger.info("✓ Sample data seeded successfully")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"✗ Seeding failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def reset_database():
    logger.info("=" * 60)
    logger.warning("RESETTING DATABASE - All data will be deleted!")
    logger.info("=" * 60)

    confirm = input("Type 'yes' to confirm: ")
    if confirm.lower() != "yes":
        logger.info("Reset cancelled")
        return

    try:
        collections = await db.list_collection_names()
        for collection_name in collections:
            await db[collection_name].drop()
        logger.info("✓ All collections dropped")

        run_migrations()

        logger.info("=" * 60)
        logger.info("✓ Database reset completed")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"✗ Reset failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def check_status():
    logger.info("=" * 60)
    logger.info("Database Status")
    logger.info("=" * 60)
    try:
        db_name = os.getenv("DB_NAME", "assignment")
        client = get_mongo_client()
        db_connection = client[db_name]

        collections = db_connection.list_collection_names()
        logger.info(f"Collections ({len(collections)}):")
        for collection_name in collections:
            collection = db_connection[collection_name]
            count = collection.count_documents({})
            logger.info(f"  - {collection_name}: {count} documents")

        if "stores" in collections:
            stores_count = db_connection.stores.count_documents({})
            logger.info(f"\nStores collection:")
            logger.info(f"  - Total stores: {stores_count}")

            sample_store = db_connection.stores.find_one({})
            if sample_store:
                logger.info(f"  - Sample store: {sample_store.get('name')}")
                models = sample_store.get("models", [])
                logger.info(f"  - Models in sample: {len(models)}")

        if "sessions" in collections:
            sessions_count = db_connection.sessions.count_documents({})
            logger.info(f"\nSessions collection:")
            logger.info(f"  - Active sessions: {sessions_count}")

        if "users" in collections:
            users_count = db_connection.users.count_documents({})
            logger.info(f"\nUsers collection:")
            logger.info(f"  - Total users: {users_count}")

        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"✗ Status check failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        logger.info("Usage: python manage.py <command>")
        logger.info("Commands:")
        logger.info("  migrate        - Run all pending migrations")
        logger.info("  migrate:status - Show migration history")
        logger.info("  status         - Check database status")
        sys.exit(1)

    command = sys.argv[1]

    if command == "migrate":
        run_migrations()
    elif command == "migrate:status":
        migration_status()
    elif command == "seed":
        asyncio.run(seed_database())
    elif command == "reset":
        asyncio.run(reset_database())
    elif command == "status":
        check_status()
    else:
        logger.error(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
