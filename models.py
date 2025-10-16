from pydantic import BaseModel
from typing import Dict, List, Optional, Union, Any

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

class DrugData(BaseModel):
    cid: Optional[str] = None
    brand_name: Optional[str] = None
    indication: Optional[str] = None
    approved_for: Optional[str] = None
    approved_countries: List[str] = []
    approved_date: Optional[str] = None
    generic_name: Optional[str] = None
    generic_approved_date: Optional[str] = None
    potential_generic_availability: Optional[str] = None
    special_status: Optional[str] = None
    patent_exclusivity_info: Optional[str] = None
    chemical_structure: Optional[str] = None
    potency_classification: Optional[str] = None
    elemental_formula: Optional[str] = None
    bcs_class: Optional[str] = None
    molecular_weight: Optional[str] = None
    average_isotopic_mass: Optional[str] = None
    iupac_name: Optional[str] = None
    solubility: Optional[str] = None
    available_dmf_vendors: Union[List[str], List[Dict[str, str]]] = []
    process_potency_classification: Optional[str] = None
    manufacturing_site: Union[str, List[Dict[str, str]]] = None
    manufacturing_route: Optional[str] = None
    polymorph_studies: Optional[str] = None
    regulatory_starting_materials: Union[str, List[str]] = None
    rsm_and_intermediate_specifications: Optional[str] = None
    drug_substance_specifications: Optional[str] = None
    impurity_qualification: Optional[str] = None
    genotoxic_impurities_assessment: Optional[str] = None
    nitrosamines_assessment: Optional[str] = None
    fate_of_impurities_studies: Optional[str] = None
    cpps_and_cqa_studies: Optional[str] = None
    other_information_reagents_and_solvents_grade: Optional[str] = None
    rsm_methods: Optional[str] = None
    ipc_test_methods: Optional[str] = None
    final_api_methods: Optional[str] = None
    residual_solvent_risk_assessment: Optional[str] = None
    rsm_synthesis: Optional[str] = None
    stability_of_drug_substance: Optional[str] = None
    current_vendor_feedback: Optional[str] = None
    dosage_forms: List[str] = []
    strength: Union[str, List[Dict[str, Any]]] = None
    target_population: Optional[str] = None
    maximum_daily_dose: Optional[str] = None
    development_program_designation: Optional[str] = None
    storage_and_shipping_conditions: Optional[str] = None
    formulation_composition: Optional[str] = None
    inactive_ingredients: List[InactiveIngredient] = []
    dp_maximum_daily_dose: Optional[str] = None
    unmet_clinical_need_with_dosage_form: Optional[str] = None
    dp_manufacturing_process: Optional[str] = None
    dp_excipients_grade: Optional[str] = None
    dp_impurities_and_process_impurities: Optional[str] = None
    dp_specification: Optional[str] = None
    dp_test_methods: Optional[str] = None
    residual_solvents_risk_assessment: Optional[str] = None
    nitrosamine_risk_assessment: Optional[str] = None
    stability_studies: Optional[str] = None
    packaging_material: Union[str, Dict[str, Any]] = None
    presentation: Optional[str] = None
    doe_cpp_cqa_cma: Optional[str] = None
    dissolution_studies: Optional[str] = None
    food_study_reports: Optional[str] = None
    current_label: Optional[str] = None
    dp_embossing_debossing: Optional[str] = None
    references: Union[List[str], List[Reference]] = []
