import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

# ---------------- Configuration ----------------
# Allow full Mongo URL from environment or fallback to host/port style
MONGO_URL = os.getenv("MONGO_URL")  # e.g. "mongodb://mongo:27017"
MONGO_HOST = os.getenv("MONGO_HOST", "chembank-mongo")  # Docker service name
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB = os.getenv("MONGO_DB", "chembank")

# Build final connection string (use MONGO_URL if set)
DB_URL = MONGO_URL or f"mongodb://{MONGO_HOST}:{MONGO_PORT}"

# ---------------- Client Setup ----------------
try:
    # Initialize the MongoDB client
    client = AsyncIOMotorClient(DB_URL, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DB]

    # Optional: expose commonly used collections
    users_collection = db["users"]
    drugs_collection = db["drugs"]

    logging.info(f"✅ Connected to MongoDB at {DB_URL}, database: {MONGO_DB}")

except ServerSelectionTimeoutError as e:
    logging.error(f"❌ Could not connect to MongoDB: {e}")
    raise RuntimeError("Failed to connect to MongoDB") from e
