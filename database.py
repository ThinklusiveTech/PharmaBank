<<<<<<< HEAD

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://chembank-mongo:27017"  # This will point to the MongoDB service in Docker
client = AsyncIOMotorClient(MONGO_URI)
db = client["chembank"]

=======
from motor.motor_asyncio import AsyncIOMotorClient

<<<<<<< HEAD
# Local MongoDB connection (no TLS needed)
DB_URL ="mongodb://chembank-mongo:27017"


client = AsyncIOMotorClient(DB_URL)
db = client["chembank"]  # database name "chembank"
=======
MONGO_URI = "mongodb://mongo:27017"  # This will point to the MongoDB service in Docker
client = AsyncIOMotorClient(MONGO_URI)
db = client["chembank"]

# Optional: expose collections
users_collection = db["users"]
drugs_collection = db["drugs"]
>>>>>>> origin/main
>>>>>>> main
