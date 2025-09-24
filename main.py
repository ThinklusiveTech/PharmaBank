<<<<<<< HEAD
# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, validator
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
import re
from typing import Optional

# --- App setup ---
app = FastAPI(title="ChemBank Auth API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database setup ---
MONGO_URL = "mongodb://chembank-mongo:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client["chembank"]

# --- Password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- JWT configuration ---
SECRET_KEY = "your_secret_key_here"  # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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
    email: EmailStr
    password: str

# --- OAuth2 setup ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# --- Endpoints ---
@app.post("/register")
async def register_user(user: UserRegister):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_dict = {
        "name": user.name,
        "email": user.email,
        "password": hash_password(user.password)
    }
    await db.users.insert_one(user_dict)
    return {"message": "User registered successfully"}

@app.post("/login")
async def login_user(user: UserLogin):
    db_user = await db.users.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": db_user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return {"name": current_user["name"], "email": current_user["email"]}
=======
from fastapi import FastAPI, HTTPException
from bson import ObjectId
from models import DrugRecord, Users
from database import db
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

# ---------------- Helpers ----------------
def drug_helper(drug) -> dict:
    drug["_id"] = str(drug["_id"])
    return drug


# ---------------- Root ----------------
@app.get("/")
async def root():
    return {"message": "MongoDB is connected"}


# ---------------- DRUGS ----------------

# Create (requires full schema)
@app.post("/drugs/")
async def create_drug(drug: DrugRecord):
    result = await db.drugs.insert_one(drug.dict())
    return {"inserted_id": str(result.inserted_id)}


# Read All
@app.get("/drugs/")
async def get_all_drugs():
    drugs = []
    async for drug in db.drugs.find():
        drugs.append(drug_helper(drug))
    return drugs


# Read One
@app.get("/drugs/{drug_id}")
async def get_drug(drug_id: str):
    if not ObjectId.is_valid(drug_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    drug = await db.drugs.find_one({"_id": ObjectId(drug_id)})
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    return drug_helper(drug)


# Update (allows partial updates)
class DrugRecordUpdate(BaseModel):
    MarketInformation: Optional[dict] = None
    DrugSubstance: Optional[dict] = None
    DrugProduct: Optional[dict] = None
    References: Optional[list] = None


@app.put("/drugs/{drug_id}")
async def update_drug(drug_id: str, updated_drug: DrugRecordUpdate):
    if not ObjectId.is_valid(drug_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    update_data = {
        k: v for k, v in updated_drug.dict(exclude_unset=True).items() if v is not None
    }

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    result = await db.drugs.update_one(
        {"_id": ObjectId(drug_id)}, {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")

    return {"message": "Drug updated successfully"}


# Delete
@app.delete("/drugs/{drug_id}")
async def delete_drug(drug_id: str):
    if not ObjectId.is_valid(drug_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.drugs.delete_one({"_id": ObjectId(drug_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")
    return {"message": "Drug deleted successfully"}
>>>>>>> main
