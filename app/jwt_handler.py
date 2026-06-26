import os
from fastapi import HTTPException, Header, Depends
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from app.database import db
from app.handlers.helpers import user_helper
from bson import ObjectId


# ---------------- Security Config ----------------
SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_key_here")  # 🔐 Use env var in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ---------------- Auth Dependency ----------------
async def get_current_user(authorization: str = Header(None)):
    """Extract and validate JWT from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user_helper(user)


# ---------------- Role-Based Access Control ----------------
def require_roles(allowed_roles: list):
    async def dependency(current_user: dict = Depends(get_current_user)):
        user_roles = current_user.get("roles", [])
        normalized_roles = [r.lower() for r in user_roles]
        
        # Expand user's roles based on hierarchy: Admin > Editor > Subscriber/User
        expanded_roles = set(normalized_roles)
        if "admin" in expanded_roles:
            expanded_roles.update(["editor", "subscriber", "user"])
        if "editor" in expanded_roles:
            expanded_roles.update(["subscriber", "user"])
        if "user" in expanded_roles or "subscriber" in expanded_roles:
            expanded_roles.update(["subscriber", "user"])
            
        check_roles = {r.lower() for r in allowed_roles}
        if "subscriber" in check_roles or "user" in check_roles:
            check_roles.update(["subscriber", "user"])
            
        if not check_roles.intersection(expanded_roles):
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource"
            )
        return current_user
    return dependency


