from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from typing import Optional, List, Dict, Any
from models import DrugData
from database import db
from pydantic import BaseModel, Field

drug_router = APIRouter()

class DrugUpdate(BaseModel):
    cid: Optional[str] = None
    marketInformation: Optional[dict] = None
    drugSubstance: Optional[dict] = None
    drugProduct: Optional[dict] = None
    appendices: Optional[dict] = None
    references: Optional[List[dict]] = None

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
def drug_helper(drug) -> dict:
    """Convert MongoDB _id to str for response"""
    drug["_id"] = str(drug["_id"])
    return drug

from jwt_handler import get_current_user

@drug_router.post("/drugs/", response_model=DrugResponse)
async def create_drug(drug: DrugData, user: dict = Depends(get_current_user)):
    drug_data = drug.dict()

    # Auto-generate CID if not provided
    if not drug_data.get("cid"):
        # Generate CID like D001, D002, etc.
        last_drug = await db.drugs.find_one(sort=[("cid", -1)])
        if last_drug and last_drug.get("cid"):
            try:
                last_num = int(last_drug["cid"][1:])  # Extract number after 'D'
                drug_data["cid"] = f"D{last_num + 1:03d}"
            except (ValueError, IndexError):
                drug_data["cid"] = "D001"
        else:
            drug_data["cid"] = "D001"

    result = await db.drugs.insert_one(drug_data)
    created_drug = await db.drugs.find_one({"_id": result.inserted_id})
    return DrugResponse(message="Drug created successfully", data=drug_helper(created_drug))

@drug_router.get("/drugs/", response_model=DrugListResponse)
async def get_all_drugs(skip: int = 0, limit: int = 10, user: dict = Depends(get_current_user)):
    drugs = []
    cursor = db.drugs.find().skip(skip).limit(limit)
    async for drug in cursor:
        drugs.append(drug_helper(drug))
    return DrugListResponse(message="Drugs retrieved successfully", total_drugs=len(drugs), data=drugs)

@drug_router.get("/drugs/{drug_id}", response_model=DrugResponse)
async def get_drug(drug_id: str, user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(drug_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    drug = await db.drugs.find_one({"_id": ObjectId(drug_id)})
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    return DrugResponse(message="Drug retrieved successfully", data=drug_helper(drug))

@drug_router.put("/drugs/{drug_id}", response_model=DrugResponse)
async def update_drug(drug_id: str, updated_drug: DrugUpdate, user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(drug_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    update_data = {}

    # Flatten nested structures to match DrugData fields
    if updated_drug.marketInformation:
        market = updated_drug.marketInformation
        update_data.update({
            "brand_name": market.get("brandName"),
            "indication": market.get("indication"),
            "approved_for": market.get("approvedFor"),
            "approved_countries": market.get("approvedCountries", []),
            "approved_date": market.get("approvedDate"),
            "generic_name": market.get("genericName"),
            "generic_approved_date": market.get("genericApprovedDate"),
            "potential_generic_availability": market.get("potentialGenericAvailability"),
            "special_status": market.get("specialStatus"),
            "patent_exclusivity_info": market.get("patentExclusivityInfo")
        })

    if updated_drug.drugSubstance:
        ds = updated_drug.drugSubstance
        if "physicalAndChemicalProperties" in ds:
            props = ds["physicalAndChemicalProperties"]
            update_data.update({
                "chemical_structure": props.get("chemicalStructure"),
                "potency_classification": props.get("potencyClassification"),
                "elemental_formula": props.get("elementalFormula"),
                "bcs_class": props.get("bcsClass"),
                "molecular_weight": props.get("molecularWeight"),
                "average_isotopic_mass": props.get("averageIsotopicMass"),
                "iupac_name": props.get("structureName"),  # or iupac_name
                "solubility": props.get("solubility")
            })
        if "processDevelopment" in ds:
            proc = ds["processDevelopment"]
            update_data.update({
                "available_dmf_vendors": proc.get("availableDmfVendors", []),
                "manufacturing_site": proc.get("manufacturingSites"),  # Now accepts list
                "manufacturing_route": proc.get("manufacturingRoute"),
                "polymorph_studies": proc.get("polymorphStudies"),
                "regulatory_starting_materials": proc.get("regulatoryStartingMaterials"),
                "rsm_and_intermediate_specifications": proc.get("rsmAndIntermediateSpecifications"),
                "drug_substance_specifications": proc.get("drugSubstanceSpecifications"),
                "impurity_qualification": proc.get("impurityQualification"),
                "genotoxic_impurities_assessment": proc.get("genotoxicImpuritiesAssessment"),
                "nitrosamines_assessment": proc.get("nitrosaminesAssessment"),
                "fate_of_impurities_studies": proc.get("fateOfImpurities"),
                "cpps_and_cqa_studies": proc.get("cppsAndCqaStudies"),
                "other_information_reagents_and_solvents_grade": proc.get("otherInformation"),
                "rsm_methods": proc.get("rsmMethods"),
                "ipc_test_methods": proc.get("ipcTestMethods"),
                "final_api_methods": proc.get("finalApiMethods"),
                "residual_solvent_risk_assessment": proc.get("residualSolventRiskAssessment"),
                "rsm_synthesis": proc.get("rsmSynthesis"),
                "stability_of_drug_substance": proc.get("stabilityOfDrugSubstance"),
                "current_vendor_feedback": proc.get("drugSubstanceSites")
            })

    if updated_drug.drugProduct:
        dp = updated_drug.drugProduct
        if "information" in dp:
            info = dp["information"]
            update_data.update({
                "dosage_forms": info.get("dosageForms", []),
                "strength": info.get("strengths"),  # Now accepts list
                "target_population": info.get("targetPopulation"),
                "maximum_daily_dose": info.get("maximumDailyDose"),
                "development_program_designation": info.get("developmentProgramDesignation"),
                "storage_and_shipping_conditions": info.get("storageAndShippingConditions"),
                "formulation_composition": info.get("dpFormulation"),
                "inactive_ingredients": info.get("inactiveIngredients", []),
                "dp_maximum_daily_dose": info.get("dpMaximumDailyDose"),
                "unmet_clinical_need_with_dosage_form": info.get("unmetClinicalNeed"),
                "dp_manufacturing_process": info.get("manufacturingProcess"),
                "dp_excipients_grade": info.get("excipientsgGrade"),
                "dp_impurities_and_process_impurities": info.get("impurities"),
                "dp_specification": info.get("specification"),
                "dp_test_methods": info.get("testMethods"),
                "residual_solvents_risk_assessment": info.get("residualSolventsRiskAssessment"),
                "nitrosamine_risk_assessment": info.get("nitrosamineRiskAssessment"),
                "stability_studies": info.get("stabilityStudies"),
                "packaging_material": info.get("packagingAndStorageConditions"),  # Now accepts dict
                "presentation": info.get("presentation"),
                "doe_cpp_cqa_cma": info.get("doeCppCqaCma"),
                "dissolution_studies": info.get("dissolutionStudies"),
                "food_study_reports": info.get("foodStudyReports"),
                "current_label": info.get("currentLabel"),
                "dp_embossing_debossing": info.get("dpEmbossingDebossingInfo")
            })

    # Handle direct fields
    if updated_drug.cid is not None:
        update_data["cid"] = updated_drug.cid
    if updated_drug.references is not None:
        update_data["references"] = updated_drug.references

    # Remove None values
    update_data = {k: v for k, v in update_data.items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    result = await db.drugs.update_one({"_id": ObjectId(drug_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")

    # Fetch the updated drug
    updated_drug_doc = await db.drugs.find_one({"_id": ObjectId(drug_id)})
    return DrugResponse(message="Drug updated successfully", data=drug_helper(updated_drug_doc))

@drug_router.delete("/drugs/{drug_id}", response_model=MessageResponse)
async def delete_drug(drug_id: str, user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(drug_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.drugs.delete_one({"_id": ObjectId(drug_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")
    return {"message": f"Drug with ID {drug_id} deleted successfully"}