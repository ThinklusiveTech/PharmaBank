import sys
import os

# Add the project directory to sys.path
sys.path.append(r'c:\Users\Pratyusha Yasalapu\Downloads\chemBank 2\chemBank')

from models import NewDrugData
from pydantic import ValidationError

full_payload = {
    "MarketInformation": {
        "version": "faf",
        "drugName": "daF",
        "apiName": "dsgef",
        "mechanismOfAction": "dF",
        "firstApprovedDate": "2026-02-11",
        "firstApprovedRegion": "chgrihdgef"
    },
    "PhysicalChemicalProperties": {
        "innName": "dsgf",
        "synonyms": "dsgfddsgbfd",
        "iupacName": "fbgf",
        "molecularWeight": "fdgbfdbg",
        "molecularFormula": "vfdbfd",
        "bcsClass": "dfbgf",
        "monoisotopicMass": "fdbgfd",
        "structureName": "fdbgfd",
        "stereochemistry": "fdbng",
        "solubility": "fdbfg",
        "pka": "fdbgd",
        "logp": "fdbfddf",
        "regulatoryInsights": "fdbf",
        "regionalApproval": "fsdgef",
        "additionalInfo": [
            {
                "drugName": "fdbdf",
                "region": "fdbdffdbf",
                "indication": "dfsgfd",
                "patientSegments": "fdbgd",
                "dosageForm": "fdb",
                "strength": "fdbgf",
                "approvedDate": "2026-02-11",
                "regulatoryBodies": "dfbgf"
            }
        ],
        "drugPatents": [
            {
                "designationType": "fdnbgf",
                "expiryDate": "2026-02-11",
                "regulatoryBody": "fdgbf",
                "exclusivityConsideration": "fdbgd",
                "impactForGenericFilers": "dfbdg"
            }
        ],
        "genericEntrants": [
            {
                "anda": "fbfd",
                "companyName": "fbdf",
                "dosageDetails": "fdb",
                "approvalType": "fgdbng",
                "andaSubmissionDate": "2026-03-14",
                "tentativeApprovalDate": "2026-02-11",
                "finalApprovalDate": "",
                "ftfExclusivity": "dsbf"
            }
        ],
        "genericsApprovedByEma": [
            {
                "companyName": "fdgvd",
                "drugName": "vfdbf",
                "dosageDetails": "bfd",
                "chmpOpinion": "dvbfv",
                "ecDecision": "bdx",
                "ecApprovalDate": "2026-02-11"
            }
        ]
    },
    "ProcessDevelopment": {
        "availableDmfVendors": [
            {
                "dmf": "bfvx",
                "regulatoryBody": "dfbvfgfdbgf",
                "status": "fbd",
                "type": "bgfx",
                "submissionDate": "2026-02-11",
                "holder": "fdbfrd",
                "apiForm": "fdvb"
            }
        ],
        "manufacturingRoutes": [
            {
                "step": "fdbg"
            }
        ],
        "dsImpurities": [
            {
                "impurities": "fbfg",
                "knownImpurities": "fdbgd",
                "specified": "fdvbf",
                "unknownImpurities": "fdbdfd"
            }
        ],
        "genotoxicImpurities": [
            {
                "genotoxicImpurities": "fvdbgfd",
                "classOfImpurity": "fdbfd"
            }
        ],
        "stability": "fdbd",
        "nitrosaminesAssessment": "gdbdg",
        "otherInformation": "fd",
        "regulatoryStartingMaterials": "dfvf",
        "drugSubstanceSpecifications": "fdbfgd"
    },
    "AnalyticalDevelopment": {
        "dosageFormAndStrength": [
            {
                "strength": "fdbf",
                "dosageForm": "cbdf",
                "size": "fdbgdf",
                "color": "fdbdf",
                "imprinting": "fbdf",
                "weight": "fd",
                "packaging": "fbfd",
                "ndcCode": "cbfd",
                "images": ""
            }
        ],
        "supplyChain": [
            {
                "genotoxicImpurities": "fb",
                "classOfImpurity": "fdb"
            }
        ],
        "manufacturingProcess": [
            {
                "dsImpurities": "fbdf",
                "knownImpurities": "fsdbdf",
                "specifiedImpurities": "fbd",
                "unknownImpurities": "fdbfd"
            }
        ],
        "baBeStudies": [
            {
                "studyType": "fdsbfdgrmjyt",
                "dosageForm": "trghrt",
                "dosageStrength": "tehrt",
                "studyDesign": "ethtr",
                "studyCondition": "rehet",
                "additionalDetails": "rehet",
                "endPoint": "fhrt"
            }
        ],
        "shelfLife": [
            {
                "currentExpirationDate": "2026-02-11",
                "strength": "fehtgrtb",
                "expiryDate": "2026-02-11"
            }
        ],
        "stabilityStudies": "fdhrtd",
        "biowaiverRequest": "fhgrff",
        "dissolutionTestMethodAndSamplingTimes": "gbrsg",
        "formulationChallenges": "grnth"
    },
    "DrugProductInformation": {
        "labelingInformation": [
            {
                "image": ""
            }
        ],
        "unmetClinicalNeed": "dD",
        "glossary": "daf"
    },
    "Appendices": {
        "appendices": [
            {
                "appendix": "dngfr"
            }
        ]
    }
}

try:
    validated = NewDrugData(**full_payload)
    print("Validation successful!")
except ValidationError as e:
    print(f"Validation failed with {e.error_count()} errors:")
    print(e)
