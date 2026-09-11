from fastapi import APIRouter, Depends, HTTPException
from app.database import db
from app.jwt_handler import require_roles
from pydantic import BaseModel
from typing import Any, Optional
import time
from datetime import datetime

draft_router = APIRouter()

# ---------------- Request Models ----------------
class DraftSaveRequest(BaseModel):
    id: str
    formData: Any
    currentStep: int
    drugName: Optional[str] = ""
    lastModified: Optional[int] = None

# ---------------- Routes ----------------

@draft_router.post("/drafts/", response_model=dict)
async def save_or_update_draft(request: DraftSaveRequest, user: dict = Depends(require_roles(["editor"]))):
    """Save or update a draft report for the authenticated editor, ensuring only one draft exists per drug."""
    now_ms = int(time.time() * 1000)
    timestamp = request.lastModified if request.lastModified else now_ms
    user_id = str(user["_id"])
    
    extracted_name = (request.drugName or "").strip()
    form_data = request.formData or {}
    cid = form_data.get("cid") or (form_data.get("ProductOverview") or {}).get("cid") if isinstance(form_data, dict) else None
    drug_id = form_data.get("_id") or form_data.get("id") or form_data.get("original_id") if isinstance(form_data, dict) else None

    # Match existing draft by id, or matching published drug_id / cid / drugName for this user
    existing_draft = None
    if request.id:
        existing_draft = await db.drafts.find_one({"id": request.id, "user_id": user_id})
    if not existing_draft and drug_id:
        existing_draft = await db.drafts.find_one({
            "user_id": user_id,
            "$or": [
                {"formData._id": str(drug_id)},
                {"formData.id": str(drug_id)},
                {"formData.original_id": str(drug_id)}
            ]
        })
    if not existing_draft and cid:
        existing_draft = await db.drafts.find_one({
            "user_id": user_id,
            "$or": [
                {"formData.cid": str(cid)},
                {"formData.ProductOverview.cid": str(cid)}
            ]
        })
    if not existing_draft and extracted_name:
        existing_draft = await db.drafts.find_one({
            "user_id": user_id,
            "$or": [
                {"drugName": {"$regex": f"^{extracted_name}$", "$options": "i"}},
                {"formData.drugName": {"$regex": f"^{extracted_name}$", "$options": "i"}}
            ]
        })

    target_id = existing_draft["id"] if existing_draft else request.id

    draft_data = {
        "id": target_id,
        "user_id": user_id,
        "formData": request.formData,
        "currentStep": request.currentStep,
        "drugName": request.drugName,
        "lastModified": timestamp
    }
    
    # Update/overwrite the target draft
    await db.drafts.update_one(
        {"id": target_id, "user_id": user_id},
        {"$set": draft_data},
        upsert=True
    )

    return {"message": "Draft saved successfully", "id": target_id}

@draft_router.get("/drafts/", response_model=list)
async def get_drafts(user: dict = Depends(require_roles(["editor"]))):
    """Retrieve all drafts for the authenticated editor"""
    drafts = []
    cursor = db.drafts.find({"user_id": str(user["_id"])}).sort("lastModified", -1)
    async for draft in cursor:
        draft["_id"] = str(draft["_id"])
        drafts.append(draft)
    return drafts

@draft_router.get("/drafts/{draft_id}", response_model=dict)
async def get_draft(draft_id: str, user: dict = Depends(require_roles(["editor"]))):
    """Retrieve a specific draft by ID"""
    draft = await db.drafts.find_one({"id": draft_id, "user_id": str(user["_id"])})
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    draft["_id"] = str(draft["_id"])
    return draft

@draft_router.delete("/drafts/{draft_id}", response_model=dict)
async def delete_draft(draft_id: str, user: dict = Depends(require_roles(["editor"]))):
    """Delete a specific draft by ID"""
    result = await db.drafts.delete_one({"id": draft_id, "user_id": str(user["_id"])})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Draft not found")
    return {"message": "Draft deleted successfully"}
