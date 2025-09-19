
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://chembank-mongo:27017"  # This will point to the MongoDB service in Docker
client = AsyncIOMotorClient(MONGO_URI)
db = client["chembank"]

