import json
from models import NewDrugData

aspirin_data = {
  "ExecutiveSummary": "Aspirin (acetylsalicylic acid) is a widely used analgesic...",
  "ProductOverview": {
    "version": "1.0.0",
    "drugName": "Aspirin Gold",
    "firstApprovedDate": "1899-03-06",
    "lossOfExclusivity": "2030-01-01"
  },
  "RegulatoryInsights": {
    "regulatoryInsights": "Widely used...",
    "approvalDetails": [
      {
        "drugName": "Aspirin Protective",
        "approvedDate": "1980-01-01"
      }
    ],
    "specialDesignations": [
      {
        "designationType": "Orphan Drug",
        "dateGranted": "2000-06-15"
      }
    ]
  },
  "PhysicalChemicalProperties": {
    "innName": "Acetylsalicylic Acid",
    "individualSolvent": [
      { "solvent": "Ethanol", "solubility": "200" }
    ]
  },
  "DrugSubstance": {
    "availableDmfVendors": [
      { "dmf": "DMF-001", "submissionDate": "2010-01-01" }
    ],
    "dsImpurities": [
      { "nameOfImpurities": "Salicylic Acid", "specifiedUnspecifiedImpurities": "Specified" }
    ]
  },
  "Sources": "WHO Essential Medicines List",
  "Glossary": "ASA (Acetylsalicylic Acid)"
}

try:
    drug = NewDrugData(**aspirin_data)
    print("Successfully parsed Aspirin Gold payload!")
    
    # Check top level
    print(f"Executive Summary: {drug.executive_summary[:30]}...")
    
    # Check Product Overview dates
    print(f"First Approved Date (Timestamp): {drug.product_overview.firstApprovedDate}")
    
    # Check Drug Substance (Renamed from Process Development)
    print(f"Drug Substance DMF Vendor: {drug.drug_substance.availableDmfVendors[0].dmf}")
    print(f"DMF Submission Date (Timestamp): {drug.drug_substance.availableDmfVendors[0].submissionDate}")
    
    # Check Impurities (Updated fields)
    print(f"Impurity Name: {drug.drug_substance.dsImpurities[0].nameOfImpurities}")
    
    # Check Sources (String field)
    print(f"Sources: {drug.sources}")

except Exception as e:
    print(f"Validation FAILED: {e}")
    import traceback
    traceback.print_exc()
