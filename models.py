
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Union, Any
from datetime import datetime


def handle_date_field(v):
    """
    Consolidated date validation logic.
    Converts various date string formats or numeric timestamps to Unix timestamp (int).
    Supported formats: DD-MM-YYYY, YYYY-MM-DD, DD/MM/YYYY, YYYY/MM/DD, DD.MM.YYYY, YYYY.MM.DD
    """
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return int(v)
    if isinstance(v, str):
        # Try various formats
        formats = (
            '%Y-%m-%d', '%d-%m-%Y',
            '%Y/%m/%d', '%d/%m/%Y',
            '%Y.%m.%d', '%d.%m.%Y'
        )
        for fmt in formats:
            try:
                dt = datetime.strptime(v, fmt)
                return int(dt.timestamp())
            except ValueError:
                continue
    return v


class Bookmark(BaseModel):
    user_id: str
    drug_id: str

class Users(BaseModel):
    name: str
    email: str
    password: str
    roles: Optional[List[str]] = ["user"]

class ForgotPasswordRequest(BaseModel):
    email: str
    new_password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class InactiveIngredient(BaseModel):
    ingredient_name: str
    percentage_w_w: str

class Reference(BaseModel):
    title: str
    url: str


# Import new schema models

# ==================== Market Information ====================
class MarketInformation(BaseModel):
    version: Optional[str] = None
    drugName: Optional[str] = None
    apiName: Optional[str] = None
    mechanismOfAction: Optional[str] = None
    companyName: Optional[str] = None
    firstApprovedDate: Optional[Union[int, str]] = None
    firstApprovedRegion: Optional[str] = None

    @field_validator('firstApprovedDate', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)


# ==================== Physical Chemical Properties ====================
class AdditionalInfo(BaseModel):
    drugName: Optional[str] = None
    region: Optional[str] = None
    indication: Optional[str] = None
    patientSegments: Optional[str] = None
    dosageForm: Optional[str] = None
    strength: Optional[str] = None
    approvedDate: Optional[Union[int, str]] = None
    regulatoryBodies: Optional[str] = None

    @field_validator('approvedDate', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)


class DrugPatent(BaseModel):
    designationType: Optional[str] = None
    expiryDate: Optional[Union[int, str]] = None
    regulatoryBody: Optional[str] = None
    exclusivityConsideration: Optional[str] = None
    impactForGenericFilers: Optional[str] = None

    @field_validator('expiryDate', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)


class GenericEntrant(BaseModel):
    anda: Optional[str] = None
    companyName: Optional[str] = None
    dosageDetails: Optional[str] = None
    approvalType: Optional[str] = None
    andaSubmissionDate: Optional[Union[int, str]] = None
    tentativeApprovalDate: Optional[Union[int, str]] = None
    finalApprovalDate: Optional[Union[int, str]] = None
    ftfExclusivity: Optional[str] = None

    @field_validator('andaSubmissionDate', 'tentativeApprovalDate', 'finalApprovalDate', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)


class GenericApprovedByEma(BaseModel):
    companyName: Optional[str] = None
    drugName: Optional[str] = None
    dosageDetails: Optional[str] = None
    chmpOpinion: Optional[str] = None
    ecDecision: Optional[str] = None
    ecApprovalDate: Optional[Union[int, str]] = None

    @field_validator('ecApprovalDate', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)


class PhysicalChemicalProperties(BaseModel):
    innName: Optional[str] = None
    synonyms: Optional[str] = None
    iupacName: Optional[str] = None
    molecularWeight: Optional[str] = None
    molecularFormula: Optional[str] = None
    bcsClass: Optional[str] = None
    monoisotopicMass: Optional[str] = None
    structureName: Optional[str] = None
    stereochemistry: Optional[str] = None
    solubility: Optional[str] = None
    pka: Optional[str] = None
    logp: Optional[str] = None
    regulatoryInsights: Optional[str] = None
    regionalApproval: Optional[str] = None
    additionalInfo: Optional[List[AdditionalInfo]] = []
    drugPatents: Optional[List[DrugPatent]] = []
    genericEntrants: Optional[List[GenericEntrant]] = []
    genericsApprovedByEma: Optional[List[GenericApprovedByEma]] = []


# ==================== Process Development ====================
class AvailableDmfVendor(BaseModel):
    dmf: Optional[str] = None
    regulatoryBody: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    submissionDate: Optional[Union[int, str]] = None
    holder: Optional[str] = None
    apiForm: Optional[str] = None

    @field_validator('submissionDate', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)


class ManufacturingRoute(BaseModel):
    step: Optional[str] = None


class DsImpurity(BaseModel):
    impurities: Optional[str] = None
    knownImpurities: Optional[str] = None
    specified: Optional[str] = None
    unknownImpurities: Optional[str] = None


class GenotoxicImpurity(BaseModel):
    genotoxicImpurities: Optional[str] = None
    classOfImpurity: Optional[str] = None


class ProcessDevelopment(BaseModel):
    availableDmfVendors: Optional[List[AvailableDmfVendor]] = []
    manufacturingRoutes: Optional[List[ManufacturingRoute]] = []
    dsImpurities: Optional[List[DsImpurity]] = []
    genotoxicImpurities: Optional[List[GenotoxicImpurity]] = []
    stability: Optional[str] = None
    nitrosaminesAssessment: Optional[str] = None
    otherInformation: Optional[str] = None
    regulatoryStartingMaterials: Optional[str] = None
    drugSubstanceSpecifications: Optional[str] = None


# ==================== Drug Product Information ====================
class ImageObject(BaseModel):
    imageData: Optional[str] = None  # Base64 encoded image or URL
    fileName: Optional[str] = None
    contentType: Optional[str] = None


# ==================== Analytical Development ====================
class DosageFormAndStrength(BaseModel):
    strength: Optional[str] = None
    dosageForm: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    imprinting: Optional[str] = None
    weight: Optional[str] = None
    packaging: Optional[str] = None
    ndcCode: Optional[str] = None
    images: Optional[List[ImageObject]] = []

    @field_validator('images', mode='before')
    @classmethod
    def handle_empty_string(cls, v):
        if v == "":
            return []
        return v


class SupplyChain(BaseModel):
    genotoxicImpurities: Optional[str] = None
    classOfImpurity: Optional[str] = None


class ManufacturingProcess(BaseModel):
    dsImpurities: Optional[str] = None
    knownImpurities: Optional[str] = None
    specifiedImpurities: Optional[str] = None
    unknownImpurities: Optional[str] = None


class BaBeStudy(BaseModel):
    studyType: Optional[str] = None
    dosageForm: Optional[str] = None
    dosageStrength: Optional[str] = None
    studyDesign: Optional[str] = None
    studyCondition: Optional[str] = None
    additionalDetails: Optional[str] = None
    endPoint: Optional[str] = None


class ShelfLife(BaseModel):
    currentExpirationDate: Optional[Union[int, str]] = None
    strength: Optional[str] = None
    expiryDate: Optional[Union[int, str]] = None

    @field_validator('currentExpirationDate', 'expiryDate', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)


class AnalyticalDevelopment(BaseModel):
    dosageFormAndStrength: Optional[List[DosageFormAndStrength]] = []
    supplyChain: Optional[List[SupplyChain]] = []
    manufacturingProcess: Optional[List[ManufacturingProcess]] = []
    baBeStudies: Optional[List[BaBeStudy]] = []
    shelfLife: Optional[List[ShelfLife]] = []
    stabilityStudies: Optional[str] = None
    biowaiverRequest: Optional[str] = None
    dissolutionTestMethodAndSamplingTimes: Optional[str] = None
    formulationChallenges: Optional[str] = None


class LabelingInformation(BaseModel):
    image: Optional[List[ImageObject]] = []

    @field_validator('image', mode='before')
    @classmethod
    def handle_empty_string(cls, v):
        if v == "":
            return []
        return v


class DrugProductInformation(BaseModel):
    labelingInformation: Optional[List[LabelingInformation]] = []
    unmetClinicalNeed: Optional[str] = None
    glossary: Optional[str] = None


# ==================== Appendices ====================
class AppendixItem(BaseModel):
    appendix: Optional[str] = None


class Appendices(BaseModel):
    appendices: Optional[List[AppendixItem]] = []


# ==================== Main Drug Data Model ====================
class NewDrugData(BaseModel):
    cid: Optional[str] = None  # Drug identifier (e.g., D001, D002)
    market_information: Optional[MarketInformation] = Field(None, alias="MarketInformation")
    physical_chemical_properties: Optional[PhysicalChemicalProperties] = Field(None, alias="PhysicalChemicalProperties")
    process_development: Optional[ProcessDevelopment] = Field(None, alias="ProcessDevelopment")
    analytical_development: Optional[AnalyticalDevelopment] = Field(None, alias="AnalyticalDevelopment")
    drug_product_information: Optional[DrugProductInformation] = Field(None, alias="DrugProductInformation")
    appendices: Optional[Appendices] = Field(None, alias="Appendices")

NewDrugData.model_rebuild()
