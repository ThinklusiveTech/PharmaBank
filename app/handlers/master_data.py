from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
from app.database import db

master_data_router = APIRouter()


@master_data_router.get("/therapeutic-areas/")
async def get_therapeutic_areas():
    """
    Returns a mapping of Therapeutic Area -> List of Approved Indications.
    Example: {"Cardiology": ["Heart Failure", "Atrial Fibrillation", ...]}
    """
    cursor = db.therapeutic_areas.find({}, {"_id": 0})
    docs = await cursor.to_list(length=100)
    result = {}
    for doc in docs:
        if "area" in doc and "indications" in doc:
            result[doc["area"]] = doc["indications"]
    return {"status": "success", "data": result}


@master_data_router.get("/regions-countries/")
async def get_regions_countries():
    """
    Returns a mapping of Region -> List of Countries.
    Example: {"Asia": ["China", "India", "Japan", ...], "Europe": [...]}
    """
    cursor = db.regions_countries.find({}, {"_id": 0})
    docs = await cursor.to_list(length=100)
    result = {}
    for doc in docs:
        if "region" in doc and "countries" in doc:
            result[doc["region"]] = doc["countries"]
    return {"status": "success", "data": result}


@master_data_router.get("/regulatory-authorities/")
async def get_regulatory_authorities():
    """
    Returns a list of Country, Regulatory Authority & Abbreviation records.
    Example: [{"country": "United States", "authority": "Food and Drug Administration", "abbreviation": "FDA (USFDA)"}]
    """
    cursor = db.regulatory_authorities.find({}, {"_id": 0})
    docs = await cursor.to_list(length=200)
    return {"status": "success", "data": docs}
