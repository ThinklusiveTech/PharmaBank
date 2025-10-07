from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.hash import bcrypt
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from bson.errors import InvalidId


# ---------------- Config ----------------
SECRET_KEY = "super_secret_key_change_me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
MONGO_URI = "mongodb://chembank-mongo:27017"

# ---------------- MongoDB Setup ----------------
client = AsyncIOMotorClient(MONGO_URI)
db = client["chembank"]
users_collection = db["users"]

# ---------------- FastAPI App ----------------
app = FastAPI(title="ChemBank API")

# ---------------- Startup Event ----------------
async def test_connection():
    try:
        await client.admin.command("ping")
        print("MongoDB connection successful!")
    except Exception as e:
        print("MongoDB connection failed:", e)
        raise e

@app.on_event("startup")
async def startup_event():
    await test_connection()

# ---------------- JWT & Auth Helpers ----------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await users_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        user["_id"] = str(user["_id"])
        user.pop("password", None)
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_admin(user: dict = Depends(get_current_user)):
    if "roles" not in user or "admin" not in user["roles"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ---------------- Pydantic Models ----------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Users(BaseModel):
    name: str
    email: EmailStr
    password: str
    roles: Optional[List[str]] = ["user"]  # default role is "user"

# ---------------- Root ----------------
@app.get("/")
async def root():
    return {"message": "MongoDB is connected"}

# ---------------- Register User ----------------
@app.post("/register")
async def register_user(user: Users):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = bcrypt.hash(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    result = await users_collection.insert_one(user_dict)

    new_user = await users_collection.find_one({"_id": result.inserted_id}, {"password": 0})
    new_user["_id"] = str(new_user["_id"])

    return {
        "message": "User registered successfully",
        "user_details": new_user
    }

# ---------------- Login ----------------
@app.post("/login")
async def login_for_access_token(form_data: LoginRequest):
    user = await users_collection.find_one({"email": form_data.email})
    if not user or not bcrypt.verify(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user["email"]})

    user_data = {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "roles": user.get("roles", ["user"])
    }

    return {
        "message": " User Login successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

# ---------------- Get All Users OR Specific User by ID ----------------
@app.get("/allusersdetails")
async def read_users(user_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    # If a specific user ID is provided
    if user_id:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        user = await users_collection.find_one({"_id": ObjectId(user_id)}, {"password": 0})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user["_id"] = str(user["_id"])
        return {
            "message": "User details found",
            "user": user
        }

    # Otherwise return all users
    users_cursor = users_collection.find({}, {"password": 0})
    all_users = []
    async for usr in users_cursor:
        usr["_id"] = str(usr["_id"])
        all_users.append(usr)

    return {
        "message": "All registered users",
        "total_users": len(all_users),
        "users": all_users
    }

# ---------------- Get User by ID ----------------
@app.get("/users/{user_id}")
async def get_user_by_id(user_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user = await users_collection.find_one({"_id": ObjectId(user_id)}, {"password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user["_id"] = str(user["_id"])
    return {
        "message": "User details found",
        "user": user
    }
# ---------------- Delete User by ID ----------------
@app.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    result = await users_collection.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User with ID {user_id} deleted successfully"}
