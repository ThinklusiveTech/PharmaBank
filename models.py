from pydantic import BaseModel
from typing import Dict, List, Optional, Union

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
