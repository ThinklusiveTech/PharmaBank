from motor.motor_asyncio import AsyncIOMotorClient

# Local MongoDB connection (no TLS needed)
DB_URL ="mongodb://chembank-mongo:27017"


client = AsyncIOMotorClient(DB_URL)
db = client["chembank"]  # database name "chembank"
