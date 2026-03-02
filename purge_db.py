import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "chembank"

async def purge_data():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print(f"Connecting to {MONGO_URL}...")
    
    # List collections before purge
    collections = await db.list_collection_names()
    print(f"Collections found: {collections}")
    
    if "drugs" in collections:
        count = await db.drugs.count_documents({})
        print(f"Purging {count} records from 'drugs' collection...")
        await db.drugs.delete_many({})
        print("Drugs collection cleared.")
        
    if "bookmarks" in collections:
        count = await db.bookmarks.count_documents({})
        print(f"Purging {count} records from 'bookmarks' collection...")
        await db.bookmarks.delete_many({})
        print("Bookmarks collection cleared.")
        
    print("Purge complete. You can now start with a clean Slate!")

if __name__ == "__main__":
    asyncio.run(purge_data())
