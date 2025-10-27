from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from models import Users, ForgotPasswordRequest
from database import db
from jwt_handler import create_access_token
from hashing import get_password_hash, verify_password
from typing import Optional
from jwt_handler import get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from bson import ObjectId
from datetime import timedelta

login_router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

# ---------------- Register User ----------------
@login_router.post("/register")
async def register_user(user: Users):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    result = await db.users.insert_one(user_dict)
    new_user = await db.users.find_one({"_id": result.inserted_id}, {"password": 0})
    new_user["_id"] = str(new_user["_id"])
    return {"message": "User registered successfully", "data": new_user}

# ---------------- Login ----------------
@login_router.post("/login")
async def login_for_access_token(form_data: LoginRequest):
    user = await db.users.find_one({"email": form_data.email})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(
        data={"sub": str(user["_id"])},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    user_data = {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "roles": user.get("roles", ["admin"])
    }
    return {"message": "User Login successfully", "access_token": access_token,  "data": user_data}

@login_router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    # Check if user exists
    user = await db.users.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Hash new password
    hashed_password = get_password_hash(request.new_password)

    # Update user password in DB
    result = await db.users.update_one(
        {"email": request.email},          # Filter: find the user by email
        {"$set": {"password": hashed_password}}  # Update: set new hashed password
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update password")

    return {"message": "Password updated successfully"}

# ---------------- Get All Users OR Specific User by ID ----------------
@login_router.get("/allusers")
async def read_users(user_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    if user_id:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password": 0})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user["_id"] = str(user["_id"])
        return {"message": "User details found", "data": user}

    users_cursor = db.users.find({}, {"password": 0})
    all_users = []
    async for usr in users_cursor:
        usr["_id"] = str(usr["_id"])
        all_users.append(usr)
    return {"message": "All registered users", "total_users": len(all_users), "data": all_users}

# ---------------- Get User by ID ----------------
@login_router.get("/user/{user_id}")
async def get_user_by_id(user_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])
    return {"message": "User details found", "data": user}

# ---------------- Delete User by ID ----------------
@login_router.delete("/user/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User with ID {user_id} deleted successfully"}

