from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import List, Optional, Union, Any
from datetime import datetime
import calendar


def handle_date_field(v):
    """
    Converts various date string formats or numeric timestamps to Unix timestamp (int).
    Supported: DD-MM-YYYY, YYYY-MM-DD, DD/MM/YYYY, YYYY/MM/DD, DD.MM.YYYY, YYYY.MM.DD
    Supports lists recursively.
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
                return calendar.timegm(dt.timetuple())
            except ValueError:
                continue
        return v
    if isinstance(v, list):
        return [handle_date_field(item) for item in v]
    return v


# ==================== Auth Models ====================
class Bookmark(BaseModel):
    user_id: str
    drug_id: str


class Users(BaseModel):
    name: str
    email: str
    password: str
    roles: Optional[List[str]] = ["subscriber"]


class ForgotPasswordRequest(BaseModel):
    email: str
    new_password: str


class LoginRequest(BaseModel):
    email: str
    password: str


# ==================== Common ====================
class ImageObject(BaseModel):
    imageData: Optional[str] = None   # base64 data URI or /uploads/ URL
    fileName: Optional[str] = None
    contentType: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def map_frontend_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Map frontend 'name' to 'fileName'
            if "name" in data and not data.get("fileName"):
                data["fileName"] = data["name"]
            # Map frontend 'type' to 'contentType'
            if "type" in data and not data.get("contentType"):
                data["contentType"] = data["type"]
        return data


# ==================== Step 1: Product Overview ====================
class ProductOverview(BaseModel):
    version: Optional[str] = None
    drugName: Optional[str] = None
    apiName: Optional[str] = None
    mechanismOfAction: Optional[str] = None
    companyName: Optional[str] = None
    approvedIndications: Optional[str] = None
    firstApprovedDate: Optional[Union[int, str]] = None
    firstApprovedRegion: Optional[str] = None
    dosageForms: Optional[str] = None
    lossOfExclusivity: Optional[Union[List[Any], int, str]] = None
    globalAnnualRevenue: Optional[str] = None

    @field_validator('firstApprovedDate', 'lossOfExclusivity', mode='before')
    @classmethod
    def validate_dates(cls, v):
        return handle_date_field(v)


# ==================== Step 2: Physical & Chemical Properties ====================
class IndividualSolvent(BaseModel):
    solvent: Optional[str] = None
    solubility: Optional[str] = None


class PhysicalChemicalProperties(BaseModel):
    innName: Optional[str] = None
    synonyms: Optional[str] = None
    iupacName: Optional[str] = None
    molecularWeight: Optional[str] = None
    molecularFormula: Optional[str] = None
    bcsClass: Optional[str] = None
    monoisotopicMass: Optional[str] = None
    # structure: accepts a URL string OR an ImageObject (for file/base64 uploads)
    structure: Optional[Union[ImageObject, str]] = None
    stereochemistry: Optional[str] = None
    solubility: Optional[str] = None
    pka: Optional[str] = None
    logp: Optional[str] = None
    logd: Optional[str] = None
    individualSolvent: Optional[List[IndividualSolvent]] = []

    @field_validator('structure', mode='before')
    @classmethod
    def handle_list_structure(cls, v):
        if isinstance(v, list) and len(v) > 0:
            return v[0]
        return v


# ==================== Step 3: Regulatory Insights ====================
class RegulatoryApprovalDetail(BaseModel):
    drugName: Optional[str] = None
    region: Optional[str] = None
    indication: Optional[str] = None
    patientSegments: Optional[str] = None
    dosageForm: Optional[str] = None
    dose: Optional[str] = None
    approvedDate: Optional[Union[int, str]] = None
    regulatoryBodies: Optional[str] = None

    @field_validator('approvedDate', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)


class SpecialDesignation(BaseModel):
    designationType: Optional[str] = None
    regulatorBody: Optional[str] = None
    indication: Optional[str] = None
    dateGranted: Optional[Union[int, str]] = None

    @field_validator('dateGranted', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)


class DrugPatent(BaseModel):
    designationType: Optional[str] = None
    expiryDate: Optional[Union[int, str]] = None

    @field_validator('expiryDate', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)


class RegulatoryAdditionalInfo(BaseModel):
    consideration: Optional[str] = None
    impactForGenericFilers: Optional[str] = None


class RegulatoryInsights(BaseModel):
    regulatoryInsights: Optional[str] = None
    regionalApproval: Optional[str] = None
    approvalDetails: Optional[List[RegulatoryApprovalDetail]] = []
    specialDesignations: Optional[List[SpecialDesignation]] = []
    drugPatents: Optional[List[DrugPatent]] = []
    additionalInfo: Optional[List[RegulatoryAdditionalInfo]] = []


# ==================== Step 4: Generic Entrants ====================
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
    def validate_dates(cls, v):
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


class GenericEntrants(BaseModel):
    genericEntrants: Optional[List[GenericEntrant]] = []
    genericsApprovedByEma: Optional[List[GenericApprovedByEma]] = []


# ==================== Step 5: Drug Substance (formerly Process Development) ====================
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
    nameOfImpurities: Optional[str] = None
    specifiedUnspecifiedImpurities: Optional[str] = None
    image: Optional[Union[ImageObject, str]] = None

    @field_validator('image', mode='before')
    @classmethod
    def handle_list_image(cls, v):
        if isinstance(v, list) and len(v) > 0:
            return v[0]
        return v


class GenotoxicImpurity(BaseModel):
    genotoxicImpurities: Optional[str] = None
    classOfImpurity: Optional[str] = None


class DrugSubstance(BaseModel):
    availableDmfVendors: Optional[List[AvailableDmfVendor]] = []
    manufacturingRoutes: Optional[List[ManufacturingRoute]] = []
    dsImpurities: Optional[List[DsImpurity]] = []
    genotoxicImpurities: Optional[List[GenotoxicImpurity]] = []
    stability: Optional[Union[List[Any], str]] = []
    nitrosaminesAssessment: Optional[str] = None
    otherInformation: Optional[str] = None
    regulatoryStartingMaterials: Optional[str] = None
    drugSubstanceSpecifications: Optional[str] = None
    stableAndCommerciallyUsedPolymorphicForm: Optional[str] = None


# ==================== Step 6: Drug Product Information ====================
class DosageFormAndStrength(BaseModel):
    strength: Optional[str] = None
    dosageForm: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    imprinting: Optional[str] = None
    weight: Optional[str] = None
    packaging: Optional[str] = None
    ndcCode: Optional[str] = None
    # images: accepts a URL string OR a list of ImageObjects
    images: Optional[Union[List[ImageObject], str]] = []

    @field_validator('images', mode='before')
    @classmethod
    def handle_images(cls, v):
        if v == "":
            return []
        return v


class SupplyChainItem(BaseModel):
    apiManufacturingAndAnalysis: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    reference: Optional[str] = None
    phaseOfProgram: Optional[str] = None


class ShelfLife(BaseModel):
    currentExpirationDate: Optional[Union[int, str]] = None
    strength: Optional[str] = None
    expiryDate: Optional[Union[int, str]] = None

    @field_validator('currentExpirationDate', 'expiryDate', mode='before')
    @classmethod
    def validate_dates(cls, v):
        return handle_date_field(v)


class ManufacturingProcess(BaseModel):
    dsImpurities: Optional[str] = None
    knownImpurities: Optional[str] = None
    specifiedImpurities: Optional[str] = None
    unknownImpurities: Optional[str] = None


class DissolutionStudy(BaseModel):
    studyType: Optional[str] = None
    uspApparatus: Optional[str] = None
    rotationSpeed: Optional[str] = None
    dissolutionMedium: Optional[str] = None
    temperature: Optional[str] = None
    acceptanceCriteria: Optional[str] = None


class Pharmacokinetics(BaseModel):
    absorption: Optional[str] = None
    volumeOfDistribution: Optional[str] = None
    metabolism: Optional[str] = None
    excretion: Optional[str] = None
    halfLife: Optional[str] = None
    steadyState: Optional[str] = None
    foodInteractions: Optional[str] = None
    drugInteractions: Optional[str] = None


class DrugProductInformation(BaseModel):
    dosageFormAndStrength: Optional[List[DosageFormAndStrength]] = []
    supplyChain: Optional[List[SupplyChainItem]] = []
    shelfLife: Optional[List[ShelfLife]] = []
    manufacturingProcess: Optional[List[ManufacturingProcess]] = []
    dissolutionStudies: Optional[List[DissolutionStudy]] = []
    pharmacokinetics: Optional[List[Pharmacokinetics]] = []
    formulationChallenges: Optional[str] = None
    stabilityStudies: Optional[Union[List[Any], str]] = []
    maximumDailyDose: Optional[str] = None
    excipientsGrade: Optional[str] = None
    storageAndShippingConditions: Optional[str] = None
    unmetClinicalNeed: Optional[str] = None


# ==================== Step 7: Labeling Information ====================
class LabelingInformationItem(BaseModel):
    # image: accepts a URL string OR an ImageObject (for file/base64 uploads)
    image: Optional[Union[ImageObject, str]] = None

    @field_validator('image', mode='before')
    @classmethod
    def handle_list_image(cls, v):
        if isinstance(v, list) and len(v) > 0:
            return v[0]
        return v


class LabelingSection(BaseModel):
    labelingInformation: Optional[List[LabelingInformationItem]] = []

    @field_validator('labelingInformation', mode='before')
    @classmethod
    def handle_empty_string(cls, v):
        if v == "":
            return []
        return v


# ==================== Step 8: BA/BE Studies ====================
class BaBeStudy(BaseModel):
    studyType: Optional[str] = None
    dosageForm: Optional[str] = None
    dosageStrength: Optional[str] = None
    studyDesign: Optional[str] = None
    studyCondition: Optional[str] = None
    additionalDetails: Optional[str] = None
    endPoint: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def handle_endpoint_alias(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Handle 'endpoint' vs 'endPoint'
            if "endpoint" in data and not data.get("endPoint"):
                data["endPoint"] = data["endpoint"]
        return data


class BaBeStudies(BaseModel):
    baBeStudies: Optional[List[BaBeStudy]] = []
    biowaiverRequest: Optional[str] = None
    dissolutionTestMethodAndSamplingTimes: Optional[str] = None


# ==================== Step 11: Appendices ====================
class AppendixItem(BaseModel):
    appendix: Optional[str] = None


class Appendices(BaseModel):
    appendices: Optional[List[AppendixItem]] = []


# ==================== Main Drug Data Model ====================
# Uses snake_case field names with PascalCase aliases so the JSON payload
# is accepted without Pydantic naming conflicts.
class NewDrugData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    cid: Optional[str] = None
    executive_summary: Optional[str] = Field(None, alias="ExecutiveSummary")
    product_overview: Optional[ProductOverview] = Field(None, alias="ProductOverview")
    physical_chemical_properties: Optional[PhysicalChemicalProperties] = Field(None, alias="PhysicalChemicalProperties")
    regulatory_insights: Optional[RegulatoryInsights] = Field(None, alias="RegulatoryInsights")
    generic_entrants: Optional[GenericEntrants] = Field(None, alias="GenericEntrants")
    drug_substance: Optional[DrugSubstance] = Field(None, alias="DrugSubstance")
    drug_product_information: Optional[DrugProductInformation] = Field(None, alias="DrugProductInformation")
    labeling_information: Optional[LabelingSection] = Field(None, alias="LabelingInformation")
    babe_studies: Optional[BaBeStudies] = Field(None, alias="BaBeStudies")
    sources: Optional[str] = Field(None, alias="Sources")
    glossary: Optional[str] = Field(None, alias="Glossary")
    appendices: Optional[Appendices] = Field(None, alias="Appendices")

    @field_validator('*', mode='before')
    @classmethod
    def deep_robustness_validator(cls, v, info):
        # 1. Handle empty objects
        if isinstance(v, dict) and not v:
            return None
            
        # 2. Handle wrapped strings (e.g., Sources: {"sources": "val"} or {"Sources": "val"})
        if info.field_name in ['sources', 'glossary', 'executive_summary']:
            if isinstance(v, dict):
                # Try to extract a value if any key in the dict matches the field name (case insensitive)
                for key, val in v.items():
                    if key.lower() == info.field_name.lower():
                        return val
                        
        return v


NewDrugData.model_rebuild()
