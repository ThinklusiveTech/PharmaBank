from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request, Response
from bson import ObjectId
from typing import Optional, List, Dict, Any
from models import NewDrugData
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
    # New schema fields only
    cid: Optional[Any] = None
    MarketInformation: Optional[Any] = None
    PhysicalChemicalProperties: Optional[Any] = None
    ProcessDevelopment: Optional[Any] = None
    AnalyticalDevelopment: Optional[Any] = None
    DrugProductInformation: Optional[Any] = None
    Appendices: Optional[Any] = None



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
        
        # Validate with new schema only
        validated = NewDrugData(**drug_data_dict)
        drug_data = validated.dict()
        print(f"[DEBUG] Using NEW schema")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON parse error: {str(e)}")
    except Exception as validation_error:
        raise HTTPException(
            status_code=400, 
            detail=f"JSON validation error: {str(validation_error)[:200]}"
        )

    # 3️⃣ Extract dynamic files: chemicalStructure_0, appendix5_0, appendix5_1 etc.
    uploaded_files: List[(str, UploadFile)] = []
    for key, val in form.items():
        if hasattr(val, 'filename'):
            uploaded_files.append((key, val))
    print(f"[DEBUG] uploaded_files: {uploaded_files}")

    # 4️⃣ File saving config
    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB max file

    # Updated field mappings for new schema
    # Images can be uploaded to:
    # 1. AnalyticalDevelopment.dosageFormAndStrength[].images
    # 2. DrugProductInformation.labelingInformation[].image[]
    FIELD_MAPPINGS = {
        "dosageFormImages": ["AnalyticalDevelopment", "dosageFormAndStrength", 0, "images"],
        "labelingImages": ["DrugProductInformation", "labelingInformation", 0, "image"]
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

        # Apply mapping for recognized image fields
        if clean_name in FIELD_MAPPINGS:
            value_to_set = base64_image
            
            # Special handling for LabelingInformation images which expects ImageObject
            if clean_name == "labelingImages":
                 value_to_set = {
                     "imageData": base64_image,
                     "fileName": file.filename,
                     "contentType": file.content_type
                 }
            
            print(f"[DEBUG] Setting mapped field {clean_name}")
            set_nested_value(drug_data, FIELD_MAPPINGS[clean_name], value_to_set)
            print(f"[DEBUG] After setting {clean_name}, payload prepared")
        else:
            # Skip unrecognized files - new schema doesn't support arbitrary file uploads
            print(f"[WARN] File field '{clean_name}' not mapped - skipping")

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

    # 6️⃣ Save to MongoDB
    print(f"[DEBUG] Saving to DB - cid: {drug_data.get('cid')}")
    inserted = await db.drugs.insert_one(drug_data)
    created_drug = await db.drugs.find_one({"_id": inserted.inserted_id})
    print(f"[DEBUG] Retrieved from DB - _id: {created_drug.get('_id')}")

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
async def get_all_drugs(request: Request, skip: int = 0,  user: dict = Depends(get_current_user)):
    drugs = []
    base_url = str(request.base_url).rstrip("/")
    cursor = db.drugs.find().skip(skip)

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

    # Build update data from new schema fields only
    update_data = {}
    
    # Update CID if provided
    if updated_drug.cid is not None:
        update_data["cid"] = updated_drug.cid
    
    # Update main sections of new schema
    if updated_drug.MarketInformation is not None:
        update_data["MarketInformation"] = updated_drug.MarketInformation
    
    if updated_drug.PhysicalChemicalProperties is not None:
        update_data["PhysicalChemicalProperties"] = updated_drug.PhysicalChemicalProperties
    
    if updated_drug.ProcessDevelopment is not None:
        update_data["ProcessDevelopment"] = updated_drug.ProcessDevelopment
    
    if updated_drug.AnalyticalDevelopment is not None:
        update_data["AnalyticalDevelopment"] = updated_drug.AnalyticalDevelopment
    
    if updated_drug.DrugProductInformation is not None:
        update_data["DrugProductInformation"] = updated_drug.DrugProductInformation
    
    if updated_drug.Appendices is not None:
        update_data["Appendices"] = updated_drug.Appendices

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

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
