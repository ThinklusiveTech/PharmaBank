from fastapi import FastAPI, HTTPException, Depends, Header
from bson import ObjectId
from typing import Optional, List
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr

from database import db
from models import DrugData, Users

app = FastAPI()

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


async def get_current_user(authorization: str = Header(None)):
    """Extract and validate JWT from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user_helper(user)


# ---------------- Root ----------------
@app.get("/", response_model=dict)
async def root():
    return {"message": "MongoDB is connected"}


# ---------------- USER ROUTES ----------------
class UserCreate(BaseModel):
    name: str
    email: str
    password: str


@app.post("/register", response_model=dict)
async def register_user(user: UserCreate):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    user_dict = {"name": user.name, "email": user.email, "password": hashed_password}
    result = await db.users.insert_one(user_dict)
    created_user = await db.users.find_one({"_id": result.inserted_id})
    return {"user": user_helper(created_user), "message": "User registered successfully"}


# ---------------- LOGIN (JSON-based) ----------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@app.post("/login", response_model=dict)
async def login(request: LoginRequest):
    user = await db.users.find_one({"email": request.email})
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

# ---------------- DRUG ROUTES ----------------
class DrugResponse(BaseModel):
    id: str = Field(..., alias="_id")
    MarketInformation: Optional[dict] = None
    DrugSubstance: Optional[dict] = None
    DrugProduct: Optional[dict] = None
    References: Optional[List[dict]] = None


class MessageResponse(BaseModel):
    message: str


@app.post("/drugs/", response_model=DrugResponse)
async def create_drug(drug: DrugData, user: dict = Depends(get_current_user)):
    result = await db.drugs.insert_one(drug.dict())
    created_drug = await db.drugs.find_one({"_id": result.inserted_id})
    return drug_helper(created_drug)


@app.get("/drugs/", response_model=List[DrugResponse])
async def get_all_drugs(skip: int = 0, limit: int = 10, user: dict = Depends(get_current_user)):
    drugs = []
    cursor = db.drugs.find().skip(skip).limit(limit)
    async for drug in cursor:
        drugs.append(drug_helper(drug))
    return drugs


@app.get("/drugs/{drug_id}", response_model=DrugResponse)
async def get_drug(drug_id: str, user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(drug_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    drug = await db.drugs.find_one({"_id": ObjectId(drug_id)})
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    return drug_helper(drug)


class DrugUpdate(BaseModel):
    MarketInformation: Optional[dict] = None
    DrugSubstance: Optional[dict] = None
    DrugProduct: Optional[dict] = None
    References: Optional[List[dict]] = None


@app.put("/drugs/{drug_id}", response_model=MessageResponse)
async def update_drug(drug_id: str, updated_drug: DrugUpdate, user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(drug_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    update_data = {k: v for k, v in updated_drug.dict(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    result = await db.drugs.update_one({"_id": ObjectId(drug_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")

    return {"message": "Drug updated successfully"}


@app.delete("/drugs/{drug_id}", response_model=MessageResponse)
async def delete_drug(drug_id: str, user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(drug_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.drugs.delete_one({"_id": ObjectId(drug_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")
    return {"message": "Drug deleted successfully"}
