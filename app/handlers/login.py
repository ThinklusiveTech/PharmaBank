from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.models import Users, ForgotPasswordRequest
from app.database import db
from app.jwt_handler import create_access_token, get_current_user, require_roles, ACCESS_TOKEN_EXPIRE_MINUTES, create_refresh_token, decode_token
from app.hashing import get_password_hash, verify_password
from typing import Optional, List
from bson import ObjectId
from datetime import timedelta

login_router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class UserUpdate(BaseModel):
    roles: Optional[List[str]] = None
    status: Optional[str] = None
    isActive: Optional[bool] = None
    is_active: Optional[bool] = None

# ---------------- Register User ----------------
@login_router.post("/register")
async def register_user(user: Users):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    user_dict["roles"] = ["subscriber"]
    user_dict["status"] = "active"
    user_dict["isActive"] = True
    result = await db.users.insert_one(user_dict)
    new_user = await db.users.find_one({"_id": result.inserted_id}, {"password": 0})
    new_user["_id"] = str(new_user["_id"])
    return {"message": "User registered successfully", "data": new_user}

# ---------------- Login ----------------
@login_router.post("/login")
async def login_for_access_token(form_data: LoginRequest):
    try:
        user = await db.users.find_one({"email": form_data.email})
        if not user or "password" not in user or not verify_password(form_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Active / Inactive check
        raw_status = user.get("status")
        raw_is_active = user.get("isActive", user.get("is_active"))
        is_active = (
            raw_status.lower() == "active" if isinstance(raw_status, str)
            else bool(raw_is_active) if raw_is_active is not None
            else True
        )
        if not is_active:
            raise HTTPException(status_code=403, detail="Your account is inactive. Please contact administrator.")
        
        access_token = create_access_token(
            data={"sub": str(user["_id"])},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user["_id"])}
        )

        # Store refresh token in DB
        from datetime import datetime
        await db.refresh_tokens.insert_one({
            "user_id": str(user["_id"]),
            "token": refresh_token,
            "created_at": datetime.utcnow()
        })

        user_data = {
            "id": str(user["_id"]),
            "name": user.get("name") or user.get("username") or (user.get("email") or "").split("@")[0],
            "email": user.get("email", ""),
            "roles": user.get("roles", ["subscriber"]),
            "status": user.get("status", "active"),
            "isActive": user.get("isActive", True)
        }
        return {
            "message": "User Login successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "data": user_data
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in login: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@login_router.post("/refresh")
async def refresh_access_token(request: RefreshRequest):
    payload = decode_token(request.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token payload")

    # Verify refresh token in DB
    token_in_db = await db.refresh_tokens.find_one({
        "user_id": user_id,
        "token": request.refresh_token
    })
    if not token_in_db:
        raise HTTPException(status_code=401, detail="Refresh token not found or revoked")

    # Generate new access token
    new_access_token = create_access_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@login_router.post("/logout")
async def logout(request: RefreshRequest, current_user: dict = Depends(get_current_user)):
    # Remove specific refresh token from DB
    result = await db.refresh_tokens.delete_one({
        "user_id": current_user["_id"],
        "token": request.refresh_token
    })
    if result.deleted_count == 0:
         raise HTTPException(status_code=404, detail="Refresh token not found")

    return {"message": "Logged out successfully"}

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
async def read_users(user_id: Optional[str] = None, current_user: dict = Depends(require_roles(["admin"]))):
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

    # Allow if user is admin, OR if the user is fetching their own profile
    user_roles = current_user.get("roles", [])
    is_admin = "admin" in [r.lower() for r in user_roles]
    if not is_admin and current_user.get("_id") != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource")

    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])
    return {"message": "User details found", "data": user}

# ---------------- Delete User by ID ----------------
@login_router.delete("/user/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(require_roles(["admin"]))):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User with ID {user_id} deleted successfully"}

# ---------------- Update User Details by ID ----------------
@login_router.put("/user/{user_id}")
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: dict = Depends(require_roles(["admin"]))
):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    update_data = {}
    if user_update.roles is not None:
        update_data["roles"] = user_update.roles
    if user_update.status is not None:
        update_data["status"] = user_update.status
    if user_update.isActive is not None:
        update_data["isActive"] = user_update.isActive
    if user_update.is_active is not None:
        update_data["is_active"] = user_update.is_active

    if update_data:
        update_result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        if update_result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password": 0})
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user["_id"] = str(updated_user["_id"])
    return {"message": "User updated successfully", "data": updated_user}


