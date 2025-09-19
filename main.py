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


# ---------------- USERS ----------------
@app.post("/user")
async def create_user(user: Users):
    result = await db.users.insert_one(user.dict())
    return {"inserted_id": str(result.inserted_id)}


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
