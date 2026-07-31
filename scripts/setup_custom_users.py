import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import db
from app.hashing import get_password_hash

async def seed_custom_users():
    custom_users = [
        {
            "name": "ChemBank Admin",
            "email": "admin@chembank.com",
            "password": "admin123",
            "roles": ["admin"],
            "status": "active",
            "isActive": True
        },
        {
            "name": "ChemBank Editor",
            "email": "editor@chembank.com",
            "password": "editor123",
            "roles": ["editor"],
            "status": "active",
            "isActive": True
        },
        {
            "name": "ChemBank Subscriber",
            "email": "subscriber@chembank.com",
            "password": "subscriber123",
            "roles": ["subscriber"],
            "status": "active",
            "isActive": True
        }
    ]


    print("Seeding custom users into MongoDB...")
    for user_info in custom_users:
        existing = await db.users.find_one({"email": user_info["email"]})
        if existing:
            print(f"User {user_info['email']} already exists. Updating password, roles, and status...")
            hashed_pwd = get_password_hash(user_info["password"])
            await db.users.update_one(
                {"email": user_info["email"]},
                {"$set": {
                    "password": hashed_pwd,
                    "roles": user_info["roles"],
                    "name": user_info["name"],
                    "status": user_info["status"],
                    "isActive": user_info["isActive"]
                }}
            )
        else:
            print(f"Creating user {user_info['email']}...")
            hashed_pwd = get_password_hash(user_info["password"])
            user_data = {
                "name": user_info["name"],
                "email": user_info["email"],
                "password": hashed_pwd,
                "roles": user_info["roles"],
                "status": user_info["status"],
                "isActive": user_info["isActive"]
            }
            await db.users.insert_one(user_data)
            
    print("Seeding complete! You can now log in with these credentials.")

if __name__ == "__main__":
    asyncio.run(seed_custom_users())

