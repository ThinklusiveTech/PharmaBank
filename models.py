<<<<<<< HEAD
from pydantic import BaseModel
from typing import Dict, List, Optional, Union

class Users(BaseModel):
    name: str
    email: str
    password: str


class InactiveIngredient(BaseModel):
    ingredient_name: str
    percentage_w_w: str

class DrugData(BaseModel):
    # --- Market Information ---
    brand_name: Optional[str]
    indication: Optional[str]
    approved_for: Optional[str]
    approved_countries: List[str] = []
    approved_date: Optional[str]
    generic_name: Optional[str]
    generic_approved_date: Optional[str]
    potential_generic_availability: Optional[str]
    special_status: Optional[str]
    patent_exclusivity_info: Optional[str]

    # --- Drug Substance Physical and Chemical Properties ---
    chemical_structure: Optional[str]
    potency_classification: Optional[str]
    elemental_formula: Optional[str]
    bcs_class: Optional[str]
    molecular_weight: Optional[str]
    average_isotopic_mass: Optional[str]
    iupac_name: Optional[str]
    solubility: Optional[str]

    # --- Drug Substance Process Development ---
    available_dmf_vendors: List[str] = []
    process_potency_classification: Optional[str]
    manufacturing_site: Optional[str]
    manufacturing_route: Optional[str]
    polymorph_studies: Optional[str]
    regulatory_starting_materials: List[str] = []
    rsm_and_intermediate_specifications: Optional[str]
    drug_substance_specifications: Optional[str]
    impurity_qualification: Optional[str]
    genotoxic_impurities_assessment: Optional[str]
    nitrosamines_assessment: Optional[str]
    fate_of_impurities_studies: Optional[str]
    cpps_and_cqa_studies: Optional[str]
    other_information_reagents_and_solvents_grade: Optional[str]

    # --- Drug Substance Analytical Development ---
    rsm_methods: Optional[str]
    ipc_test_methods: Optional[str]
    final_api_methods: Optional[str]
    residual_solvent_risk_assessment: Optional[str]
    rsm_synthesis: Optional[str]
    stability_of_drug_substance: Optional[str]

    # --- Drug Substance Agency Feedback ---
    current_vendor_feedback: Optional[str]

    # --- Drug Product Information ---
    dosage_forms: List[str] = []
    strength: Optional[str]
    target_population: Optional[str]
    maximum_daily_dose: Optional[str]
    development_program_designation: Optional[str]
    storage_and_shipping_conditions: Optional[str]

    # --- Drug Product Formulation ---
    formulation_composition: Optional[str]
    inactive_ingredients: List[InactiveIngredient] = []
    dp_maximum_daily_dose: Optional[str]
    unmet_clinical_need_with_dosage_form: Optional[str]
    dp_manufacturing_process: Optional[str]
    dp_excipients_grade: Optional[str]
    dp_impurities_and_process_impurities: Optional[str]
    dp_specification: Optional[str]
    dp_test_methods: Optional[str]
    residual_solvents_risk_assessment: Optional[str]
    nitrosamine_risk_assessment: Optional[str]
    stability_studies: Optional[str]
    packaging_material: Optional[str]
    presentation: Optional[str]
    doe_cpp_cqa_cma: Optional[str]
    dissolution_studies: Optional[str]
    food_study_reports: Optional[str]
    current_label: Optional[str]
    dp_embossing_debossing: Optional[str]

    # --- References ---
    references: List[str] = []
=======
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

>>>>>>> main
