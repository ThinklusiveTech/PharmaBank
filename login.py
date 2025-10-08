from fastapi import  HTTPException
from pydantic import BaseModel
from models import Users, ForgotPasswordRequest
from database import db
from jwt_handler import create_access_token
from hashing import get_password_hash, verify_password
from main import app



class LoginRequest(BaseModel):
    email: str
    password: str
    

def user_helper(user) -> dict:
    """Convert MongoDB user to safe response (remove password)"""
    user["_id"] = str(user["_id"])
    user.pop("password", None)
    return user


# ---------------- USER ROUTES ----------------
@app.post("/register", response_model=dict)
async def register_user(user: Users):
    """Register a new user"""
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    user_dict = {"name": user.name, "email": user.email, "password": hashed_password}
    result = await db.users.insert_one(user_dict)
    created_user = await db.users.find_one({"_id": result.inserted_id})
    return {"user": user_helper(created_user), "message": "User registered successfully"}



@app.post("/login", response_model=dict)
async def login(request: LoginRequest):
    """Login user and return JWT"""
    user = await db.users.find_one({"email": request.email})
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/forgot-password", response_model=dict)
async def forgot_password(request: ForgotPasswordRequest):
    # Check if user exists
    user = await db.users.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    #  Hash new password
    hashed_password = get_password_hash(request.new_password)

    #  Update user password in DB
    result = await db.users.update_one(
        {"email": request.email},          # Filter: find the user by email
        {"$set": {"password": hashed_password}}  # Update: set new hashed password
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update password")

    return {"message": "Password updated successfully"}



