from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union

class Users(BaseModel):
    username: str
    email: str
    password: str

class InactiveIngredient(BaseModel):
    ingredient_name: str = Field(alias="IngredientName")
    percentage_w_w: str = Field(alias="%w/w")

class DrugData(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    # --- Market Information ---
    brand_name: Optional[str] = Field(default=None, alias="BrandName")
    indication: Optional[str] = Field(default=None, alias="Indication")
    approved_for: Optional[str] = Field(default=None, alias="ApprovedFor")
    approved_countries: List[str] = Field(default_factory=list, alias="ApprovedCountries")
    approved_date: Optional[str] = Field(default=None, alias="ApprovedDate")
    generic_name: Optional[str] = Field(default=None, alias="GenericName")
    generic_approved_date: Optional[str] = Field(default=None, alias="GenericApprovedDate")
    potential_generic_availability: Optional[str] = Field(default=None, alias="PotentialGenericAvailability")
    special_status: Optional[str] = Field(default=None, alias="SpecialStatus")
    patent_exclusivity_info: Optional[str] = Field(default=None, alias="PatentExclusivityInfo")

    # --- Drug Substance Physical and Chemical Properties ---
    chemical_structure: Optional[str] = Field(default=None, alias="ChemicalStructure")
    potency_classification: Optional[str] = Field(default=None, alias="PotencyClassification")
    elemental_formula: Optional[str] = Field(default=None, alias="ElementalFormula")
    bcs_class: Optional[str] = Field(default=None, alias="BCSClass")
    molecular_weight: Optional[str] = Field(default=None, alias="MolecularWeight")
    average_isotopic_mass: Optional[str] = Field(default=None, alias="AverageIsotopicMass")
    iupac_name: Optional[str] = Field(default=None, alias="IUPACName")
    solubility: Optional[str] = Field(default=None, alias="Solubility")

    # --- Drug Substance Process Development ---
    available_dmf_vendors: List[str] = Field(default_factory=list, alias="AvailableDMFvendors")
    process_potency_classification: Optional[str] = Field(default=None, alias="PotencyClassification")
    manufacturing_site: Optional[str] = Field(default=None, alias="ManufacturingSite")
    manufacturing_route: Optional[str] = Field(default=None, alias="ManufacturingRoute")
    polymorph_studies: Optional[str] = Field(default=None, alias="PolymorphStudies")
    regulatory_starting_materials: List[str] = Field(default_factory=list, alias="RegulatoryStartingMaterials")
    rsm_and_intermediate_specifications: Optional[str] = Field(default=None, alias="RSMandIntermediateSpecifications")
    drug_substance_specifications: Optional[str] = Field(default=None, alias="DrugSubstanceSpecifications")
    impurity_qualification: Optional[str] = Field(default=None, alias="ImpurityQualification")
    genotoxic_impurities_assessment: Optional[str] = Field(default=None, alias="GenotoxicImpuritiesAssessment")
    nitrosamines_assessment: Optional[str] = Field(default=None, alias="NitrosaminesAssessment")
    fate_of_impurities_studies: Optional[str] = Field(default=None, alias="FateOfImpuritiesStudies")
    cpps_and_cqa_studies: Optional[str] = Field(default=None, alias="CPPsAndCQAStudies")
    other_information_reagents_and_solvents_grade: Optional[str] = Field(default=None, alias="OtherInformationReagentsAndSolventsGrade")

    # --- Drug Substance Analytical Development ---
    rsm_methods: Optional[str] = Field(default=None, alias="RSMMethods")
    ipc_test_methods: Optional[str] = Field(default=None, alias="IPCTestMethods")
    final_api_methods: Optional[str] = Field(default=None, alias="FinalAPIMethods")
    residual_solvent_risk_assessment: Optional[str] = Field(default=None, alias="ResidualSolventRiskAssessment")
    rsm_synthesis: Optional[str] = Field(default=None, alias="RSMSynthesis")
    stability_of_drug_substance: Optional[str] = Field(default=None, alias="StabilityOfDrugSubstance")

    # --- Drug Substance Agency Feedback ---
    current_vendor_feedback: Optional[str] = Field(default=None, alias="CurrentVendorFeedback")

    # --- Drug Product Information ---
    dosage_forms: List[str] = Field(default_factory=list, alias="DosageForms")
    strength: Optional[str] = Field(default=None, alias="Strength")
    target_population: Optional[str] = Field(default=None, alias="TargetPopulation")
    maximum_daily_dose: Optional[str] = Field(default=None, alias="MaximumDailyDose")
    development_program_designation: Optional[str] = Field(default=None, alias="DevelopmentProgramDesignation")
    storage_and_shipping_conditions: Optional[str] = Field(default=None, alias="StorageAndShippingConditions")

    # --- Drug Product Formulation ---
    formulation_composition: Optional[str] = Field(default=None, alias="FormulationComposition")
    inactive_ingredients: List[InactiveIngredient] = Field(default_factory=list, alias="InactiveIngredients")
    dp_maximum_daily_dose: Optional[str] = Field(default=None, alias="MaximumDailyDose")
    unmet_clinical_need_with_dosage_form: Optional[str] = Field(default=None, alias="UnmetClinicalNeedWithDosageForm")
    dp_manufacturing_process: Optional[str] = Field(default=None, alias="DPManufacturingProcess")
    dp_excipients_grade: Optional[str] = Field(default=None, alias="DPExcipientsGrade")
    dp_impurities_and_process_impurities: Optional[str] = Field(default=None, alias="DPImpuritiesAndProcessImpurities")
    dp_specification: Optional[str] = Field(default=None, alias="DPSpecification")
    dp_test_methods: Optional[str] = Field(default=None, alias="DPTestMethods")
    residual_solvents_risk_assessment: Optional[str] = Field(default=None, alias="ResidualSolventsRiskAssessment")
    nitrosamine_risk_assessment: Optional[str] = Field(default=None, alias="NitrosamineRiskAssessment")
    stability_studies: Optional[str] = Field(default=None, alias="StabilityStudies")
    packaging_material: Optional[str] = Field(default=None, alias="PackagingMaterial")
    presentation: Optional[str] = Field(default=None, alias="Presentation")
    doe_cpp_cqa_cma: Optional[str] = Field(default=None, alias="DOE_CPP_CQA_CMA")
    dissolution_studies: Optional[str] = Field(default=None, alias="DissolutionStudies")
    food_study_reports: Optional[str] = Field(default=None, alias="FoodStudyReports")
    current_label: Optional[str] = Field(default=None, alias="CurrentLabel")
    dp_embossing_debossing: Optional[str] = Field(default=None, alias="DPEmbossingDebossing")

    # --- References ---
    references: List[str] = Field(default_factory=list, alias="References")