import asyncio
from database import db
from hashing import get_password_hash

async def reset_and_setup_users():
    # 1. Clear users and refresh tokens
    print("Clearing users and refresh_tokens collections...")
    await db.users.delete_many({})
    await db.refresh_tokens.delete_many({})
    
    # 2. Define the three standard users
    standard_users = [
        {
            "name": "Test Admin",
            "email": "admin@chembank.com",
            "password": "admin123",
            "roles": ["admin"]
        },
        {
            "name": "Test Editor",
            "email": "editor@chembank.com",
            "password": "editor123",
            "roles": ["editor"]
        },
        {
            "name": "Test Subscriber",
            "email": "subscriber@chembank.com",
            "password": "subscriber123",
            "roles": ["subscriber"]
        }
    ]

    # 3. Create users in DB
    for user_info in standard_users:
        print(f"Creating user {user_info['email']} with role {user_info['roles']}...")
        hashed_pwd = get_password_hash(user_info["password"])
        user_data = {
            "name": user_info["name"],
            "email": user_info["email"],
            "password": hashed_pwd,
            "roles": user_info["roles"]
        }
        await db.users.insert_one(user_data)
            
    print("Database users collection reset and standard roles setup successfully!")

if __name__ == "__main__":
    asyncio.run(reset_and_setup_users())
