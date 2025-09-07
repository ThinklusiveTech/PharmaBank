from fastapi import FastAPI, HTTPException
from typing import List
from models import DrugData, Users
from database import db

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "MongoDB is connected"}

@app.post("/user")
async def create_user(user: Users):
    user_dict = user.dict()
    result = await db.users.insert_one(user_dict)
    return {"inserted_id": str(result.inserted_id)}

# --- CRUD APIs ---

# Create
@app.post("/drugs/", response_model=DrugData)
async def create_drug(drug: DrugData):
    drug_dict = drug.dict()
    result = await db.drugs.insert_one(drug_dict)
    drug_dict["_id"] = str(result.inserted_id)
    return drug_dict

# Read All
@app.get("/drugs/", response_model=List[DrugData])
async def get_all_drugs():
    drugs = []
    async for drug in db.drugs.find():
        drug["_id"] = str(drug["_id"])
        drugs.append(drug)
    return drugs

# Read by ID (MongoDB ObjectId)
from bson import ObjectId

@app.get("/drugs/{drug_id}", response_model=DrugData)
async def get_drug(drug_id: str):
    drug = await db.drugs.find_one({"_id": ObjectId(drug_id)})
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    drug["_id"] = str(drug["_id"])
    return drug

# Update
@app.put("/drugs/{drug_id}", response_model=DrugData)
async def update_drug(drug_id: str, updated_drug: DrugData):
    result = await db.drugs.replace_one({"_id": ObjectId(drug_id)}, updated_drug.dict())
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")
    updated = await db.drugs.find_one({"_id": ObjectId(drug_id)})
    updated["_id"] = str(updated["_id"])
    return updated

# Delete
@app.delete("/drugs/{drug_id}")
async def delete_drug(drug_id: str):
    result = await db.drugs.delete_one({"_id": ObjectId(drug_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")
    return {"message": "Drug deleted successfully"}