import asyncio
from database import db
from hashing import get_password_hash

async def seed_custom_users():
    custom_users = [
        {
            "name": "ChemBank Admin",
            "email": "admin@chembank.com",
            "password": "Admin123!",
            "roles": ["admin"]
        },
        {
            "name": "ChemBank Editorial",
            "email": "editorial@chembank.com",
            "password": "Editorial123!",
            "roles": ["editor"]
        },
        {
            "name": "ChemBank Developer",
            "email": "developer@chembank.com",
            "password": "Develop123!",
            "roles": ["subscriber"]
        }
    ]

    print("Seeding custom users into MongoDB...")
    for user_info in custom_users:
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
            
    print("Seeding complete! You can now log in with these credentials.")

if __name__ == "__main__":
    asyncio.run(seed_custom_users())
