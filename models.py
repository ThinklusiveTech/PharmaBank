from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------- Market Information ----------------
class MarketInformation(BaseModel):
    BrandName: str = ""
    Indication: str = ""
    ApprovedFor: str = ""
    ApprovedCountries: List[str] = Field(default_factory=list)
    ApprovedDate: str = ""
    GenericName: str = ""
    GenericApprovedDate: str = ""
    PotentialGenericAvailability: str = ""
    SpecialStatus: str = ""
    PatentExclusivityInfo: str = ""


# ---------------- Drug Substance ----------------
class PhysicalAndChemicalProperties(BaseModel):
    ChemicalStructure: str = ""
    PotencyClassification: str = ""
    ElementalFormula: str = ""
    BCSClass: str = ""
    MolecularWeight: str = ""
    AverageIsotopicMass: str = ""
    IUPACName: str = ""
    Solubility: str = ""


class ProcessDevelopment(BaseModel):
    AvailableDMFvendors: List[str] = Field(default_factory=list)
    PotencyClassification: str = ""
    ManufacturingSite: str = ""
    ManufacturingRoute: str = ""
    PolymorphStudies: str = ""
    RegulatoryStartingMaterials: str = ""
    RSMsAndIntermediateSpecifications: str = ""
    DrugSubstanceSpecifications: str = ""
    ImpurityQualification: str = ""
    GenotoxicImpuritiesAssessment: str = ""
    NitrosaminesAssessment: str = ""
    FateOfImpuritiesStudies: str = ""
    CPPsAndCQAStudies: str = ""
    OtherInformation: str = ""


class AnalyticalDevelopment(BaseModel):
    RSMMethods: str = ""
    IPCTestMethods: str = ""
    FinalAPIMethods: str = ""
    ResidualSolventRiskAssessment: str = ""
    RSMSynthesis: str = ""
    StabilityOfDrugSubstance: str = ""


class DrugSubstance(BaseModel):
    PhysicalAndChemicalProperties: PhysicalAndChemicalProperties
    ProcessDevelopment: ProcessDevelopment
    AnalyticalDevelopment: AnalyticalDevelopment
    AgencyFeedback: str = ""


# ---------------- Drug Product ----------------
class Ingredient(BaseModel):
    IngredientName: str = ""
    Percent_w_w: str = ""


class Information(BaseModel):
    DosageForms: str = ""
    Strength: str = ""
    TargetPopulation: str = ""
    MaximumDailyDose: str = ""
    DevelopmentProgramDesignation: str = ""
    StorageAndShippingConditions: str = ""


class Formulation(BaseModel):
    FormulationComposition: List[str] = Field(default_factory=list)
    InactiveIngredients: List[Ingredient] = Field(default_factory=list)
    MaximumDailyDose: str = ""
    UnmetClinicalNeed: str = ""
    ManufacturingProcess: str = ""
    ExcipientsGrade: str = ""
    ImpuritiesAndProcessImpurities: str = ""
    Specification: str = ""
    TestMethods: str = ""
    ResidualSolventsRiskAssessment: str = ""
    NitrosamineRiskAssessment: str = ""
    StabilityStudies: str = ""
    PackagingMaterial: str = ""
    Presentation: str = ""
    DOE_CPP_CQA_CMAs: str = ""
    DissolutionStudies: str = ""
    FoodStudyReports: str = ""
    CurrentLabel: str = ""
    EmbossingDebossing: str = ""


class DrugProduct(BaseModel):
    Information: Information
    Formulation: Formulation


# ---------------- Main Drug Record ----------------
class DrugRecord(BaseModel):
    MarketInformation: MarketInformation
    DrugSubstance: DrugSubstance
    DrugProduct: DrugProduct
    References: List[str] = Field(default_factory=list)

