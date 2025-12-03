from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from bson import ObjectId
from typing import Optional, List, Dict, Any
from models import DrugData
from database import db
from pydantic import BaseModel
from jwt_handler import get_current_user
import json
import os
import uuid


drug_router = APIRouter()


class DrugUpdate(BaseModel):
    cid: Optional[Any] = None
    version: Optional[Any] = None
    marketInformation: Optional[Any] = None
    drugSubstance: Optional[Any] = None
    drugProduct: Optional[Any] = None
    appendices: Optional[Any] = None
    references: Optional[Any] = None


# ---------------- Response Models ----------------
class DrugResponse(BaseModel):
    message: str
    data: Dict[str, Any]


class DrugListResponse(BaseModel):
    message: str
    total_drugs: int
    data: List[Dict[str, Any]]


class MessageResponse(BaseModel):
    message: str


# ---------------- Helpers ----------------
def drug_helper(drug, base_url: str = None) -> dict:
    """Convert MongoDB _id to str and optionally convert image paths to full URLs"""
    drug["_id"] = str(drug["_id"])

    if base_url:
        def convert_paths(obj):
            if isinstance(obj, dict):
                return {k: convert_paths(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_paths(v) for v in obj]
            elif isinstance(obj, str) and obj.startswith("uploads/"):
                return f"{base_url}/{obj}"
            return obj

        drug = convert_paths(drug)

    return drug


# ---------------- CREATE DRUG ----------------
@drug_router.post("/drugs/", response_model=DrugResponse)
async def create_drug(request: Request, user: dict = Depends(get_current_user)):
    """Handles JSON form + dynamic file uploads + path building"""

    # 1️⃣ Read entire multipart form
    form = await request.form()

    if "data" not in form:
        raise HTTPException(status_code=400, detail="Missing 'data' JSON field")

    # 2️⃣ Extract JSON DATA
    try:
        drug_data_dict = json.loads(form["data"])
        validated = DrugData(**drug_data_dict)
        drug_data = validated.dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"JSON validation error: {str(e)}")

    # 3️⃣ Extract dynamic files: chemicalStructure_0, appendix5_0, appendix5_1 etc.
    uploaded_files: List[(str, UploadFile)] = []
    for key, val in form.items():
        if isinstance(val, UploadFile):
            uploaded_files.append((key, val))

    # 4️⃣ File saving config
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB max file

    FIELD_MAPPINGS = {
        "chemicalstructure": ["drugSubstance", "physicalAndChemicalProperties", "chemicalStructure"]
    }

    appendices = {}

    # Helper to insert nested values
    def set_nested_value(data, keys, value):
        for key in keys[:-1]:
            data = data.setdefault(key, {})
        final = keys[-1]

        if final in data and data[final] is not None:
            if not isinstance(data[final], list):
                data[final] = [data[final]]
            data[final].append(value)
        else:
            data[final] = value

    # 5️⃣ Save every uploaded file
    for field_name, file in uploaded_files:

        if not file.filename:
            continue

        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(400, f"File too large: {file.filename}")

        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(400, f"Invalid file type: {file.filename}")

        ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4()}{ext}"

        file_path = os.path.join(upload_dir, unique_name)
        relative_path = f"uploads/{unique_name}"

        # Write file
        with open(file_path, "wb") as f:
            f.write(content)

        clean_name = field_name.lower().split("_")[0]

        # Apply mapping
        if clean_name in FIELD_MAPPINGS:
            set_nested_value(drug_data, FIELD_MAPPINGS[clean_name], relative_path)
        else:
            # Appendices (supports multiple files)
            appendices.setdefault(clean_name, [])
            appendices[clean_name].append(relative_path)

    # Merge appendices with existing data from JSON
    if appendices:
        # Initialize appendices if not exists or is None
        if "appendices" not in drug_data or drug_data["appendices"] is None:
            drug_data["appendices"] = {}
        elif not isinstance(drug_data["appendices"], dict):
            # If appendices exists but is not a dict, reset it
            drug_data["appendices"] = {}
        
        # Merge uploaded files with existing appendices from JSON
        drug_data["appendices"].update(appendices)

    # 6️⃣ Auto-generate CID if not provided
    if not drug_data.get("cid"):
        last = await db.drugs.find_one(sort=[("cid", -1)])
        if last and last.get("cid"):
            try:
                last_num = int(last["cid"][1:])
                drug_data["cid"] = f"D{last_num + 1:03d}"
            except:
                drug_data["cid"] = "D001"
        else:
            drug_data["cid"] = "D001"

    # 7️⃣ Save to MongoDB
    inserted = await db.drugs.insert_one(drug_data)
    created_drug = await db.drugs.find_one({"_id": inserted.inserted_id})

    base_url = str(request.base_url).rstrip("/")
    response_data = drug_helper(created_drug, base_url)

    # Collect URLs
    image_urls = []

    def collect_urls(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                collect_urls(v)
        elif isinstance(obj, list):
            for v in obj:
                collect_urls(v)
        elif isinstance(obj, str) and obj.startswith("uploads/"):
            image_urls.append(f"{base_url}/{obj}")

    collect_urls(created_drug)

    response_data["image_urls"] = image_urls

    return DrugResponse(message="Drug created successfully", data=response_data)


# ---------------- GET ALL DRUGS ----------------
@drug_router.get("/drugs/", response_model=DrugListResponse)
async def get_all_drugs(skip: int = 0, limit: int = 10, user: dict = Depends(get_current_user)):
    drugs = []
    cursor = db.drugs.find().skip(skip).limit(limit)

    async for drug in cursor:
        drugs.append(drug_helper(drug))

    return DrugListResponse(
        message="Drugs retrieved successfully",
        total_drugs=len(drugs),
        data=drugs
    )


# ---------------- GET SINGLE DRUG ----------------
@drug_router.get("/drugs/{drug_id}", response_model=DrugResponse)
async def get_drug(drug_id: str, user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(drug_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    drug = await db.drugs.find_one({"_id": ObjectId(drug_id)})
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")

    return DrugResponse(
        message="Drug retrieved successfully",
        data=drug_helper(drug)
    )


# ---------------- UPDATE DRUG ----------------
@drug_router.put("/drugs/{drug_id}", response_model=DrugResponse)
async def update_drug(drug_id: str, updated_drug: DrugUpdate, user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(drug_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    update_data = {}

    # Flatten nested update data
    if updated_drug.marketInformation:
        update_data.update({
            "brand_name": updated_drug.marketInformation.get("brandName"),
            "indication": updated_drug.marketInformation.get("indication"),
            "generic_name": updated_drug.marketInformation.get("genericName"),
        })

    if updated_drug.cid is not None:
        update_data["cid"] = updated_drug.cid

    if updated_drug.version is not None:
        update_data["version"] = updated_drug.version

    if updated_drug.references is not None:
        update_data["references"] = updated_drug.references

    update_data = {k: v for k, v in update_data.items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields")

    result = await db.drugs.update_one(
        {"_id": ObjectId(drug_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")

    updated_doc = await db.drugs.find_one({"_id": ObjectId(drug_id)})

    return DrugResponse(message="Drug updated successfully", data=drug_helper(updated_doc))


# ---------------- DELETE DRUG ----------------
@drug_router.delete("/drugs/{drug_id}", response_model=MessageResponse)
async def delete_drug(drug_id: str, user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(drug_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    result = await db.drugs.delete_one({"_id": ObjectId(drug_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")

    return {"message": f"Drug with ID {drug_id} deleted successfully"}
