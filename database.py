from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://mongo:27017"  # This will point to the MongoDB service in Docker
client = AsyncIOMotorClient(MONGO_URI)
db = client["chembank"]

# Optional: expose collections
users_collection = db["users"]
drugs_collection = db["drugs"]