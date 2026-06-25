import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import db
from app.hashing import get_password_hash

async def seed_rbac_users():
    test_users = [
        {
            "name": "Test Subscriber",
            "email": "subscriber@chembank.com",
            "password": "subscriber123",
            "roles": ["subscriber"]
        },
        {
            "name": "Test Editor",
            "email": "editor@chembank.com",
            "password": "editor123",
            "roles": ["editor"]
        },
        {
            "name": "Test Admin",
            "email": "admin@chembank.com",
            "password": "admin123",
            "roles": ["admin"]
        }
    ]

    print("Seeding test_rbac users into MongoDB...")
    for user_info in test_users:
        existing = await db.users.find_one({"email": user_info["email"]})
        if existing:
            print(f"User {user_info['email']} already exists. Updating password and roles...")
            hashed_pwd = get_password_hash(user_info["password"])
            await db.users.update_one(
                {"email": user_info["email"]},
                {"$set": {"password": hashed_pwd, "roles": user_info["roles"], "name": user_info["name"]}}
            )
        else:
            print(f"Creating user {user_info['email']}...")
            hashed_pwd = get_password_hash(user_info["password"])
            user_data = {
                "name": user_info["name"],
                "email": user_info["email"],
                "password": hashed_pwd,
                "roles": user_info["roles"]
            }
            await db.users.insert_one(user_data)
            
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_rbac_users())


