from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import List, Optional, Union, Any, Dict
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


class LossOfExclusivityItem(BaseModel):
    exclusivityCode: Optional[str] = None
    country: Optional[str] = None
    regulatoryBody: Optional[str] = None
    expiredDate: Optional[Union[int, str]] = None

    @field_validator('expiredDate', mode='before')
    @classmethod
    def validate_dates(cls, v):
        return handle_date_field(v)


# ==================== Step 1: Product Overview ====================
class ProductOverview(BaseModel):
    model_config = ConfigDict(extra='allow')

    version: Optional[str] = None
    drugName: Optional[str] = None
    apiName: Optional[str] = None
    mechanismOfAction: Optional[str] = None
    companyName: Optional[str] = None
    therapeuticArea: Optional[str] = None
    approvedIndications: Optional[str] = None
    firstApprovedDate: Optional[Union[int, str]] = None
    firstApprovedRegion: Optional[str] = None
    dosageForms: Optional[Union[str, List[Any], Dict[str, Any]]] = None
    dosageFormAndStrength: Optional[Union[List[Any], Dict[str, Any], str]] = None
    dosageFormsAndStrengths: Optional[Union[List[Any], Dict[str, Any], str]] = None
    lossOfExclusivity: Optional[Union[List[LossOfExclusivityItem], List[Any], str]] = None
    lossOfExclusivityDate: Optional[Union[int, str]] = None
    expiredDate: Optional[Union[int, str]] = None
    timeFromLoeToFirstGenericLaunchMonths: Optional[Union[int, float, str]] = None
    timeFromLoeToFirstGenericLaunch: Optional[Union[int, float, str]] = None
    globalAnnualRevenue: Optional[Union[List[Any], Dict[str, Any], str]] = None
    marketingRights: Optional[Union[List[Any], Dict[str, Any], str]] = None
    marketingDistributionRights: Optional[Union[List[Any], Dict[str, Any], str]] = None
    createdBy: Optional[str] = None
    createdByEmail: Optional[str] = None
    createdByName: Optional[str] = None

    @field_validator('firstApprovedDate', 'firstApprovedDate', 'lossOfExclusivityDate', 'expiredDate', mode='before')
    @classmethod
    def validate_dates(cls, v):
        return handle_date_field(v)


# ==================== Step 2: Physical & Chemical Properties ====================
class IndividualSolvent(BaseModel):
    solvent: Optional[str] = None
    solubility: Optional[str] = None


class AqueousSolubilityItem(BaseModel):
    ph: Optional[str] = None
    solvent: Optional[str] = None
    solubility: Optional[str] = None
    units: Optional[str] = None


class PhysicalChemicalProperties(BaseModel):
    model_config = ConfigDict(extra="allow")

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
    aqueousSolubility: Optional[Union[List[AqueousSolubilityItem], List[Any], str]] = []
    pka: Optional[str] = None
    logp: Optional[str] = None
    logd: Optional[str] = None
    compendialStatus: Optional[str] = None
    referenceStandard: Optional[str] = None
    hygroscopicity: Optional[str] = None
    photostability: Optional[str] = None
    particleSizeDistribution: Optional[str] = None
    individualSolvent: Optional[Union[List[IndividualSolvent], List[Any], str]] = []

    @field_validator('structure', mode='before')
    @classmethod
    def handle_list_structure(cls, v):
        if isinstance(v, list) and len(v) > 0:
            return v[0]
        return v


class RegulatoryApprovalDetail(BaseModel):
    model_config = ConfigDict(extra="allow")

    drugName: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    indication: Optional[str] = None
    patientSegments: Optional[str] = None
    dosageForm: Optional[str] = None
    dose: Optional[str] = None
    approvedDate: Optional[Union[int, str]] = None
    regulatoryBodies: Optional[Union[List[str], str]] = None

    @field_validator('approvedDate', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)


class SpecialDesignation(BaseModel):
    model_config = ConfigDict(extra="allow")

    designationType: Optional[str] = None
    country: Optional[str] = None
    regulatorBody: Optional[str] = None
    indication: Optional[str] = None
    dateGranted: Optional[Union[int, str]] = None
    expiryDate: Optional[Union[int, str]] = None
    withdrawn: Optional[Union[int, str]] = None

    @field_validator('dateGranted', 'expiryDate', 'withdrawn', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)


class ExclusivityInfoItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    designationType: Optional[str] = None
    exclusivityCode: Optional[str] = None
    regulatoryBody: Optional[str] = None
    country: Optional[str] = None
    expiryDate: Optional[Union[int, str]] = None

    @field_validator('expiryDate', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)


class PatentInformationItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    patentNo: Optional[str] = None
    patentExpiration: Optional[Union[int, str]] = None
    drugSubstance: Optional[str] = None
    drugProduct: Optional[str] = None
    submissionDate: Optional[Union[int, str]] = None
    regulatoryBody: Optional[str] = None
    designationType: Optional[str] = None
    expiryDate: Optional[Union[int, str]] = None

    @field_validator('patentExpiration', 'submissionDate', 'expiryDate', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)


class DrugPatent(BaseModel):
    model_config = ConfigDict(extra="allow")

    patentNo: Optional[str] = None
    patentExpiration: Optional[Union[int, str]] = None
    drugSubstance: Optional[str] = None
    drugProduct: Optional[str] = None
    submissionDate: Optional[Union[int, str]] = None
    regulatoryBody: Optional[str] = None
    designationType: Optional[str] = None
    expiryDate: Optional[Union[int, str]] = None

    @field_validator('patentExpiration', 'submissionDate', 'expiryDate', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)


class RegulatoryAdditionalInfo(BaseModel):
    model_config = ConfigDict(extra="allow")

    consideration: Optional[str] = None
    impactForGenericFilers: Optional[str] = None


# ==================== Step 3: Development Feasibility & Timeline ====================
class DevelopmentFeasibility(BaseModel):
    model_config = ConfigDict(extra="allow")
    recommendedRegulatoryPathway: Optional[str] = None
    overallCmcComplexityRating: Optional[str] = None
    estimatedDsDevelopmentTimelineMonths: Optional[Union[float, int, str]] = None
    estimatedDpDevelopmentTimelineMonths: Optional[Union[float, int, str]] = None
    estimatedTotalTimeToFilingMonths: Optional[Union[float, int, str]] = None
    keyDevelopmentRiskFlags: Optional[str] = None
    firstToFile180DayExclusivityOpportunity: Optional[str] = None
    therapeuticEquivalenceTeCode: Optional[str] = None
    bdRecommendation: Optional[str] = None


class RegulatoryInsights(BaseModel):
    model_config = ConfigDict(extra="allow")

    regulatoryInsights: Optional[str] = None
    regionalApproval: Optional[str] = None
    approvalDetails: Optional[Union[List[RegulatoryApprovalDetail], List[Any], str]] = []
    specialDesignations: Optional[Union[List[SpecialDesignation], List[Any], str]] = []
    exclusivityInfo: Optional[Union[List[ExclusivityInfoItem], List[Any], str]] = []
    patentInformation: Optional[Union[List[PatentInformationItem], List[Any], str]] = []
    drugPatents: Optional[Union[List[PatentInformationItem], List[DrugPatent], List[Any], str]] = []
    additionalInfo: Optional[Union[List[RegulatoryAdditionalInfo], List[Any], str]] = []


# ==================== Step 4: Generic Entrants ====================
class GenericEntrant(BaseModel):
    model_config = ConfigDict(extra="allow")

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
    model_config = ConfigDict(extra="allow")

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
    model_config = ConfigDict(extra="allow")

    genericEntrants: Optional[Union[List[GenericEntrant], List[Any], str]] = []
    genericsApprovedByEma: Optional[Union[List[GenericApprovedByEma], List[Any], str]] = []


# ==================== Step 5: Drug Substance (formerly Process Development) ====================
class AvailableDmfVendor(BaseModel):
    model_config = ConfigDict(extra="allow")

    dmf: Optional[str] = None
    company: Optional[str] = None
    typeOfDmf: Optional[str] = None
    yearApproved: Optional[Union[int, str]] = None
    status: Optional[str] = None
    regulatoryBody: Optional[str] = None
    type: Optional[str] = None
    submissionDate: Optional[Union[int, str]] = None
    holder: Optional[str] = None
    apiForm: Optional[str] = None

    @field_validator('submissionDate', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)


class KsmAvailabilityItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    rsmName: Optional[str] = None
    supplier: Optional[str] = None


class ManufacturingRoute(BaseModel):
    model_config = ConfigDict(extra="allow")

    step: Optional[str] = None
    description: Optional[str] = None
    schematicRepresentation: Optional[Union[ImageObject, str]] = None

    @field_validator('schematicRepresentation', mode='before')
    @classmethod
    def handle_schematic_image(cls, v):
        if isinstance(v, list) and len(v) > 0:
            return v[0]
        return v


class DrugSubstanceSpecificationItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    testCriteria: Optional[str] = None
    acceptanceCriteria: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None


class DsImpurity(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: Optional[str] = None
    nameOfImpurities: Optional[str] = None
    structure: Optional[Union[ImageObject, str]] = None
    image: Optional[Union[ImageObject, str]] = None
    knownUnknown: Optional[str] = None
    specifiedUnspecifiedImpurities: Optional[str] = None

    @field_validator('structure', 'image', mode='before')
    @classmethod
    def handle_list_image(cls, v):
        if isinstance(v, list) and len(v) > 0:
            return v[0]
        return v


class ForcedDegradationStudyItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    stressCondition: Optional[str] = None
    details: Optional[str] = None
    percentAssay: Optional[str] = None
    percentImpurities: Optional[str] = None


class GenotoxicImpurity(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: Optional[str] = None
    genotoxicImpurities: Optional[str] = None
    gtiClass: Optional[str] = None
    classOfImpurity: Optional[str] = None


class NitrosaminesAssessmentItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    nameOfImpurity: Optional[str] = None
    structure: Optional[Union[ImageObject, str]] = None
    riskOutcome: Optional[str] = None

    @field_validator('structure', mode='before')
    @classmethod
    def handle_structure_image(cls, v):
        if isinstance(v, list) and len(v) > 0:
            return v[0]
        return v


class StabilityDataItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    condition: Optional[str] = None
    durationMonths: Optional[Union[int, str]] = None


class DrugSubstance(BaseModel):
    model_config = ConfigDict(extra="allow")

    availableDmfVendors: Optional[Union[List[AvailableDmfVendor], List[Any], str]] = []
    ksmAvailability: Optional[Union[List[KsmAvailabilityItem], List[Any], str]] = []
    manufacturingRoutes: Optional[Union[List[ManufacturingRoute], List[Any], str]] = []
    stableAndCommerciallyUsedPolymorphicForm: Optional[str] = None
    drugSubstanceSpecifications: Optional[Union[List[DrugSubstanceSpecificationItem], List[Any], dict, str]] = None
    dsImpurities: Optional[Union[List[DsImpurity], List[Any], str]] = []
    forcedDegradationStudies: Optional[Union[List[ForcedDegradationStudyItem], List[Any], str]] = []
    genotoxicImpurities: Optional[Union[List[GenotoxicImpurity], List[Any], str]] = []
    nitrosaminesAssessment: Optional[Union[List[NitrosaminesAssessmentItem], List[Any], str]] = []
    recommendedStorageCondition: Optional[str] = None
    stabilityData: Optional[Union[List[StabilityDataItem], List[Any], str]] = []
    stability: Optional[Union[List[Any], str]] = []
    packaging: Optional[str] = None
    otherInformation: Optional[str] = None
    regulatoryStartingMaterials: Optional[Union[str, List[Any]]] = None


# ==================== Step 6: Drug Product Information ====================
class PresentationItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    strength: Optional[str] = None
    dosageForm: Optional[str] = None
    shape: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    imprint: Optional[str] = None
    ndcCode: Optional[str] = None


class ContainerClosureSystemItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    component: Optional[str] = None
    material: Optional[str] = None
    function: Optional[str] = None


class ExcipientsComplianceItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    excipient: Optional[str] = None
    proposedLevel: Optional[str] = None
    fdaIidMaxLevel: Optional[str] = None
    status: Optional[str] = None


class ManufacturingProcessItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    step: Optional[str] = None
    description: Optional[str] = None
    dsImpurities: Optional[str] = None
    knownImpurities: Optional[str] = None
    specifiedImpurities: Optional[str] = None
    unknownImpurities: Optional[str] = None


class DrugProductSpecificationItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    testCriteria: Optional[str] = None
    methodTechnique: Optional[str] = None
    acceptanceCriteria: Optional[str] = None


class DpImpurityItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: Optional[str] = None
    structure: Optional[Union[ImageObject, str]] = None
    knownUnknown: Optional[str] = None

    @field_validator('structure', mode='before')
    @classmethod
    def handle_structure_image(cls, v):
        if isinstance(v, list) and len(v) > 0:
            return v[0]
        return v


class StabilityStudyItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    condition: Optional[str] = None
    durationMonths: Optional[Union[int, str]] = None
    packaging: Optional[str] = None


class DissolutionMethodItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    apparatus: Optional[str] = None
    media: Optional[str] = None
    speedRpm: Optional[str] = None
    samplingTimes: Optional[str] = None
    temperature: Optional[str] = None


class DosageFormAndStrength(BaseModel):
    model_config = ConfigDict(extra="allow")

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
    model_config = ConfigDict(extra="allow")

    apiManufacturingAndAnalysis: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    reference: Optional[str] = None
    phaseOfProgram: Optional[str] = None


class ShelfLife(BaseModel):
    model_config = ConfigDict(extra="allow")

    currentExpirationDate: Optional[Union[int, str]] = None
    strength: Optional[str] = None
    expiryDate: Optional[Union[int, str]] = None

    @field_validator('currentExpirationDate', 'expiryDate', mode='before')
    @classmethod
    def validate_dates(cls, v):
        return handle_date_field(v)


class DissolutionStudy(BaseModel):
    model_config = ConfigDict(extra="allow")

    studyType: Optional[str] = None
    uspApparatus: Optional[str] = None
    rotationSpeed: Optional[str] = None
    dissolutionMedium: Optional[str] = None
    temperature: Optional[str] = None
    acceptanceCriteria: Optional[str] = None


class Pharmacokinetics(BaseModel):
    model_config = ConfigDict(extra="allow")

    absorption: Optional[str] = None
    volumeOfDistribution: Optional[str] = None
    metabolism: Optional[str] = None
    excretion: Optional[str] = None
    halfLife: Optional[str] = None
    steadyState: Optional[str] = None
    foodInteractions: Optional[str] = None
    drugInteractions: Optional[str] = None


class DrugProductInformation(BaseModel):
    model_config = ConfigDict(extra="allow")

    presentation: Optional[Union[List[PresentationItem], List[Any], str]] = []
    containerClosureSystem: Optional[Union[List[ContainerClosureSystemItem], List[Any], str]] = []
    excipientsCompliance: Optional[Union[List[ExcipientsComplianceItem], List[Any], str]] = []
    manufacturingTechnology: Optional[str] = None
    manufacturingProcess: Optional[Union[List[ManufacturingProcessItem], List[Any], str]] = []
    maximumDailyDose: Optional[str] = None
    storageAndShippingConditions: Optional[str] = None
    drugProductSpecifications: Optional[Union[List[DrugProductSpecificationItem], List[Any], str]] = []
    dpImpurities: Optional[Union[List[DpImpurityItem], List[Any], str]] = []
    nitrosamineStatement: Optional[str] = None
    stabilityStudies: Optional[Union[List[StabilityStudyItem], List[Any], str]] = []
    dissolutionMethod: Optional[Union[List[DissolutionMethodItem], List[Any], str]] = []

    # Backward compatible fields
    dosageFormAndStrength: Optional[Union[List[DosageFormAndStrength], List[Any], str]] = []
    supplyChain: Optional[Union[List[SupplyChainItem], List[Any], str]] = []
    shelfLife: Optional[Union[List[ShelfLife], List[Any], str]] = []
    dissolutionStudies: Optional[Union[List[DissolutionStudy], List[Any], str]] = []
    pharmacokinetics: Optional[Union[List[Pharmacokinetics], List[Any], str]] = []
    formulationChallenges: Optional[str] = None
    excipientsGrade: Optional[str] = None
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
    labelingInformation: Optional[Union[List[LabelingInformationItem], List[Any], str]] = []

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
    baBeStudies: Optional[Union[List[BaBeStudy], List[Any], str]] = []
    biowaiverRequest: Optional[str] = None
    dissolutionTestMethodAndSamplingTimes: Optional[str] = None


# ==================== Step 11: Appendices ====================
class AppendixItem(BaseModel):
    appendix: Optional[str] = None


class Appendices(BaseModel):
    appendices: Optional[Union[List[AppendixItem], List[Any], str]] = []


# ==================== Main Drug Data Model ====================
# Uses snake_case field names with PascalCase aliases so the JSON payload
# is accepted without Pydantic naming conflicts.
class NewDrugData(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    cid: Optional[str] = None
    created_by: Optional[str] = Field(None, alias="createdBy")
    created_by_email: Optional[str] = Field(None, alias="createdByEmail")
    created_by_name: Optional[str] = Field(None, alias="createdByName")
    executive_summary: Optional[Union[str, Any]] = Field(None, alias="ExecutiveSummary")
    product_overview: Optional[Union[ProductOverview, Dict[str, Any], Any]] = Field(None, alias="ProductOverview")
    development_feasibility: Optional[Union[DevelopmentFeasibility, Dict[str, Any], Any]] = Field(None, alias="DevelopmentFeasibility")
    physical_chemical_properties: Optional[Union[PhysicalChemicalProperties, Dict[str, Any], Any]] = Field(None, alias="PhysicalChemicalProperties")
    regulatory_insights: Optional[Union[RegulatoryInsights, Dict[str, Any], Any]] = Field(None, alias="RegulatoryInsights")
    generic_entrants: Optional[Union[GenericEntrants, Dict[str, Any], Any]] = Field(None, alias="GenericEntrants")
    drug_substance: Optional[Union[DrugSubstance, Dict[str, Any], Any]] = Field(None, alias="DrugSubstance")
    drug_product_information: Optional[Union[DrugProductInformation, Dict[str, Any], Any]] = Field(None, alias="DrugProductInformation")
    labeling_information: Optional[Union[LabelingSection, List[Any], Dict[str, Any], Any]] = Field(None, alias="LabelingInformation")
    babe_studies: Optional[Union[BaBeStudies, List[Any], Dict[str, Any], Any]] = Field(None, alias="BaBeStudies")
    sources: Optional[Union[List[Any], Dict[str, Any], str, Any]] = Field(None, alias="Sources")
    glossary: Optional[Union[List[Any], Dict[str, Any], str, Any]] = Field(None, alias="Glossary")
    appendices: Optional[Union[Appendices, List[Any], Dict[str, Any], Any]] = Field(None, alias="Appendices")

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
