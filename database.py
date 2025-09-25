from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
import logging
import os

# ---------------- Configuration ----------------
MONGO_HOST = os.getenv("MONGO_HOST", "chembank-mongo")  # Docker service name
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB = os.getenv("MONGO_DB", "chembank")

DB_URL = f"mongodb://{MONGO_HOST}:{MONGO_PORT}"

# ---------------- Client Setup ----------------
try:
    client = AsyncIOMotorClient(DB_URL, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DB]

    # Optional: expose collections
    users_collection = db["users"]
    drugs_collection = db["drugs"]

    logging.info(f"✅ Connected to MongoDB at {DB_URL}, database: {MONGO_DB}")

except ServerSelectionTimeoutError as e:
    logging.error(f"❌ Could not connect to MongoDB: {e}")
    raise
