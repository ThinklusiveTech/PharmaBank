from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from typing import Optional, List
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.responses import JSONResponse

from models import DrugData, Users
from database import db

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# Allow frontend origins
origins = [
    "http://localhost:3004",          # local React dev
    "http://127.0.0.1:3000",
    "https://cmcintel.com",           # your frontend production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],              # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],              # Allow all headers
)


# ---------------- Security Config ----------------
SECRET_KEY = "super_secret_key_change_me"  # 🔐 Use env var in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Passlib bcrypt context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------- Helpers ----------------
def drug_helper(drug) -> dict:
    """Convert MongoDB _id to str for response"""
    drug["_id"] = str(drug["_id"])
    return drug

def user_helper(user) -> dict:
    """Convert MongoDB user to safe response (remove password)"""
    user["_id"] = str(user["_id"])
    user.pop("password", None)
    return user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ---------------- Auth Dependency ----------------
async def get_current_user(authorization: str = Header(None)):
    """Extract and validate JWT from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]
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

    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user_helper(user)

# ---------------- Root ----------------
@app.get("/")
async def root():
    return {"message": "MongoDB is connected"}


# Import routes so FastAPI registers them
import login
import drug




