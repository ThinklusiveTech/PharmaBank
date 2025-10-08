from fastapi import  HTTPException, Depends
from bson import ObjectId
from typing import Optional, List
from models import DrugData
from database import db
from pydantic import BaseModel, Field
from main import app
from jwt_handler import get_current_user

class DrugUpdate(BaseModel):
    MarketInformation: Optional[dict] = None
    DrugSubstance: Optional[dict] = None
    DrugProduct: Optional[dict] = None
    References: Optional[List[dict]] = None

# ---------------- Helpers ----------------
def drug_helper(drug) -> dict:
    """Convert MongoDB _id to str for response"""
    drug["_id"] = str(drug["_id"])
    return drug

# ---------------- DRUG ROUTES ----------------
class DrugResponse(DrugData):
    id: str = Field(..., alias="_id")

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