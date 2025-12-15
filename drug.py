from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request, Response
from bson import ObjectId
from typing import Optional, List, Dict, Any
from models import DrugData
from database import db
from pydantic import BaseModel
from jwt_handler import get_current_user
import json
import os
import uuid
import base64
from datetime import datetime


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
def drug_helper(drug, base_url=None) -> dict:
    """Convert MongoDB _id to str"""
    drug["_id"] = str(drug["_id"])
    return drug


# ---------------- CREATE DRUG ----------------
@drug_router.post("/drugs/", response_model=DrugResponse)
async def create_drug(request: Request, user: dict = Depends(get_current_user)):
    """Handles JSON form + dynamic file uploads + path building"""

    # 1️⃣ Read entire multipart form
    form = await request.form()
    print(f"[DEBUG] Form keys received: {list(form.keys())}")
    print(f"[DEBUG] Form data types: {[(k, type(v).__name__) for k, v in form.items()]}")

    # Debug: Check if chemicalStructure is in form
    if "chemicalStructure" in form:
        file_obj = form["chemicalStructure"]
        print(f"[DEBUG] chemicalStructure file object: {file_obj}")
        print(f"[DEBUG] chemicalStructure filename: {getattr(file_obj, 'filename', 'No filename')}")
        print(f"[DEBUG] chemicalStructure content_type: {getattr(file_obj, 'content_type', 'No content_type')}")
    else:
        print(f"[DEBUG] chemicalStructure NOT found in form")

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
        if hasattr(val, 'filename'):
            uploaded_files.append((key, val))
    print(f"[DEBUG] uploaded_files: {uploaded_files}")

    # 4️⃣ File saving config
    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB max file

    FIELD_MAPPINGS = {
        "chemicalStructure": ["drugSubstance", "physicalAndChemicalProperties", "chemicalStructure"]
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

    # 5️⃣ Save every uploaded file as Base64 in MongoDB
    for field_name, file in uploaded_files:

        if not file.filename:
            continue

        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(400, f"File too large: {file.filename}")

        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(400, f"Invalid file type: {file.filename}")

        # Convert to Base64 string
        encoded_string = base64.b64encode(content).decode("utf-8")
        base64_image = f"data:{file.content_type};base64,{encoded_string}"

        clean_name = field_name
        print(f"[DEBUG] clean_name: {clean_name}")

        # Apply mapping
        if clean_name in FIELD_MAPPINGS:
            print(f"[DEBUG] Setting mapped field {clean_name} as Base64")
            set_nested_value(drug_data, FIELD_MAPPINGS[clean_name], base64_image)
            print(f"[DEBUG] After setting, chemicalStructure length: {len(base64_image)}")
        else:
            # Appendices (supports multiple files)
            print(f"[DEBUG] Adding to appendices - {clean_name}")
            appendices.setdefault(clean_name, [])
            appendices[clean_name].append(base64_image)

    # Merge appendices with existing data from JSON
    if appendices:
        print(f"[DEBUG] Uploaded appendices to merge: {appendices}")
        # Initialize appendices if not exists or is None
        if "appendices" not in drug_data or drug_data["appendices"] is None:
            drug_data["appendices"] = {}
        elif not isinstance(drug_data["appendices"], dict):
            # If appendices exists but is not a dict, reset it
            drug_data["appendices"] = {}
        
        print(f"[DEBUG] Existing appendices before merge: {drug_data.get('appendices')}")
        # Merge uploaded files with existing appendices from JSON
        drug_data["appendices"].update(appendices)
        print(f"[DEBUG] Final appendices after merge: {drug_data['appendices']}")

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
    print(f"[DEBUG] Saving to DB - appendices field: {drug_data.get('appendices')}")
    inserted = await db.drugs.insert_one(drug_data)
    created_drug = await db.drugs.find_one({"_id": inserted.inserted_id})
    print(f"[DEBUG] Retrieved from DB - appendices field: {created_drug.get('appendices')}")

    response_data = drug_helper(created_drug)
    print(f"[DEBUG] After drug_helper - appendices field: {response_data.get('appendices')}")

    # Collect URLs
    image_urls = []

    def collect_urls(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                collect_urls(v)
        elif isinstance(obj, list):
            for v in obj:
                collect_urls(v)
        elif isinstance(obj, str) and (obj.startswith("http") or obj.startswith("data:image")):
            image_urls.append(obj)

    collect_urls(response_data)
    print(f"[DEBUG] Collected image URLs: {image_urls}")

    response_data["image_urls"] = image_urls
    print(f"[DEBUG] Final response appendices: {response_data.get('appendices')}")

    return DrugResponse(message="Drug created successfully", data=response_data)


# ---------------- GET ALL DRUGS ----------------
@drug_router.get("/drugs/", response_model=DrugListResponse)
async def get_all_drugs(request: Request, skip: int = 0, limit: int = 10, user: dict = Depends(get_current_user)):
    drugs = []
    base_url = str(request.base_url).rstrip("/")
    cursor = db.drugs.find().skip(skip).limit(limit)

    async for drug in cursor:
        response_data = drug_helper(drug, base_url)

        # Collect URLs from the converted data
        image_urls = []
        def collect_urls(obj):
            if isinstance(obj, dict):
                for v in obj.values():
                    collect_urls(v)
            elif isinstance(obj, list):
                for v in obj:
                    collect_urls(v)
            elif isinstance(obj, str) and (obj.startswith("http") or obj.startswith("data:image")):
                image_urls.append(obj)

        collect_urls(response_data)
        response_data["image_urls"] = image_urls

        drugs.append(response_data)

    return DrugListResponse(
        message="Drugs retrieved successfully",
        total_drugs=len(drugs),
        data=drugs
    )


# ---------------- GET SINGLE DRUG ----------------
@drug_router.get("/drugs/{drug_id}", response_model=DrugResponse)
async def get_drug(drug_id: str, request: Request, user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(drug_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    drug = await db.drugs.find_one({"_id": ObjectId(drug_id)})
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")

    response_data = drug_helper(drug)

    # Collect URLs from the converted data
    image_urls = []
    def collect_urls(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                collect_urls(v)
        elif isinstance(obj, list):
            for v in obj:
                collect_urls(v)
        elif isinstance(obj, str) and (obj.startswith("http") or obj.startswith("data:image")):
            image_urls.append(obj)

    collect_urls(response_data)
    response_data["image_urls"] = image_urls

    return DrugResponse(
        message="Drug retrieved successfully",
        data=response_data
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

    return DrugResponse(message="Drug updated successfully", data=drug_helper(updated_doc, None))


# ---------------- DELETE DRUG ----------------
@drug_router.delete("/drugs/{drug_id}", response_model=MessageResponse)
async def delete_drug(drug_id: str, user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(drug_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    result = await db.drugs.delete_one({"_id": ObjectId(drug_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")

    return {"message": f"Drug with ID {drug_id} deleted successfully"}
