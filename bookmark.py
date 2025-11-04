from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from database import db
from jwt_handler import get_current_user
from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Any

bookmark_router = APIRouter()

# ---------------- Request Models ----------------
class BookmarkRequest(BaseModel):
    drug_id: str

# ---------------- Response Models ----------------
class BookmarkResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    message: str
    data: Dict[str, Any]

class MessageResponse(BaseModel):
    message: str

class BookmarkListResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    message: str
    total_bookmarks: int
    data: List[Dict[str, Any]]

# ---------------- Helpers ----------------
def drug_helper(drug) -> dict:
    """Convert MongoDB _id to str for response"""
    drug["_id"] = str(drug["_id"])
    return drug

@bookmark_router.post("/bookmarks/", response_model=BookmarkResponse)
async def bookmark_drug(request: BookmarkRequest, user: dict = Depends(get_current_user)):
    drug_id = request.drug_id
    if not ObjectId.is_valid(drug_id):
        raise HTTPException(status_code=400, detail="Invalid drug ID")

    # Check if drug exists
    drug = await db.drugs.find_one({"_id": ObjectId(drug_id)})
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")

    # Check if already bookmarked
    existing = await db.bookmarks.find_one({"user_id": str(user["_id"]), "drug_id": drug_id})
    if existing:
        raise HTTPException(status_code=409, detail="Drug already bookmarked")

    bookmark_data = {
        "user_id": str(user["_id"]),
        "drug_id": drug_id
    }
    await db.bookmarks.insert_one(bookmark_data)
    return BookmarkResponse(message="Drug bookmarked successfully", data=drug_helper(drug))



@bookmark_router.get("/bookmarks/", response_model=BookmarkListResponse)
async def get_bookmarked_drugs(skip: int = 0, limit: int = 10, user: dict = Depends(get_current_user)):
    bookmarks = []
    cursor = db.bookmarks.find({"user_id": str(user["_id"])}).skip(skip).limit(limit)
    async for bookmark in cursor:
        drug = await db.drugs.find_one({"_id": ObjectId(bookmark["drug_id"])})
        if drug:
            bookmarks.append(drug_helper(drug))
    return BookmarkListResponse(message="Bookmarked drugs retrieved successfully", total_bookmarks=len(bookmarks), data=bookmarks) 

@bookmark_router.delete("/bookmarks/{drug_id}", response_model=MessageResponse)
async def unbookmark_drug(drug_id: str, user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(drug_id):
        raise HTTPException(status_code=400, detail="Invalid drug ID")

    result = await db.bookmarks.delete_one({"user_id": str(user["_id"]), "drug_id": drug_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return MessageResponse(message="Drug unbookmarked successfully")





