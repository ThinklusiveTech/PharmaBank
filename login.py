from fastapi import  HTTPException, Depends
from pydantic import BaseModel
from models import Users, ForgotPasswordRequest
from database import db
from jwt_handler import create_access_token
from hashing import get_password_hash
from main import app
from typing import Optional
from jwt_handler import get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from bson import ObjectId
from datetime import timedelta
from hashing import bcrypt



class LoginRequest(BaseModel):
    email: str
    password: str


 
# ---------------- Register User ----------------
@app.post("/register")
async def register_user(user: Users):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = bcrypt.hash(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    result = await db.users.insert_one(user_dict)
    new_user = await db.users.find_one({"_id": result.inserted_id}, {"password": 0})
    new_user["_id"] = str(new_user["_id"])
    return {"message": "User registered successfully", "user_details": new_user}
 
# ---------------- Login ----------------
@app.post("/login")
async def login_for_access_token(form_data: LoginRequest):
    user = await db.users.find_one({"email": form_data.email})
    if not user or not bcrypt.verify(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    user_data = {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "roles": user.get("roles", ["admin"])
    }
    return {"message": "User Login successfully", "access_token": access_token, "token_type": "bearer", "user": user_data}

# # ---------------- USER ROUTES ----------------
# @app.post("/register", response_model=dict)
# async def register_user(user: Users):
#     """Register a new user"""
#     existing_user = await db.users.find_one({"email": user.email})
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")

#     hashed_password = get_password_hash(user.password)
#     user_dict = {"name": user.name, "email": user.email, "password": hashed_password}
#     result = await db.users.insert_one(user_dict)
#     created_user = await db.users.find_one({"_id": result.inserted_id})
#     return {"user": user_helper(created_user), "message": "User registered successfully"}



# @app.post("/login", response_model=dict)
# async def login(request: LoginRequest):
#     """Login user and return JWT"""
#     user = await db.users.find_one({"email": request.email})
#     if not user or not verify_password(request.password, user["password"]):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     access_token = create_access_token({"sub": user["email"]})
#     return {"access_token": access_token, "token_type": "bearer"}

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


# ---------------- Get All Users OR Specific User by ID ----------------
@app.get("/allusers")
async def read_users(user_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    if user_id:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password": 0})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user["_id"] = str(user["_id"])
        return {"message": "User details found", "user": user}
 
    users_cursor = db.users.find({}, {"password": 0})
    all_users = []
    async for usr in users_cursor:
        usr["_id"] = str(usr["_id"])
        all_users.append(usr)
    return {"message": "All registered users", "total_users": len(all_users), "users": all_users}
 
# ---------------- Get User by ID ----------------
@app.get("/user/{user_id}")
async def get_user_by_id(user_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])
    return {"message": "User details found", "user": user}
 
# ---------------- Delete User by ID ----------------
@app.delete("/user/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User with ID {user_id} deleted successfully"}
 



