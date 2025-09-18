from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, validator
from typing import List
import re
from passlib.context import CryptContext

app = FastAPI()

# In-memory storage
users_db: List[dict] = []

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- User Models ---
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

    @validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value

class UserLogin(BaseModel):
    username_or_email: str
    password: str

# --- Helper functions ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- Endpoints ---
@app.post("/register")
def register_user(user: UserRegister):
    # Check if email already exists
    for u in users_db:
        if u["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    users_db.append({"name": user.name, "email": user.email, "password": hashed_pw})
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserLogin):
    for u in users_db:
        if u["email"] == user.username_or_email or u["name"] == user.username_or_email:
            if verify_password(user.password, u["password"]):
                return {
                    "message": "Login successful",
                    "user": {"name": u["name"], "email": u["email"]}
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid username/email or password")
    raise HTTPException(status_code=401, detail="Invalid username/email or password")
