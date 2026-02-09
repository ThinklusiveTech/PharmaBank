
from models import NewDrugData
import json

json_data = """
{
    "MarketInformation": {
        "version": "1",
        "drugName": "dolo",
        "apiName": "gzds",
        "mechanismOfAction": "dsgsd",
        "companyName": "dsgs",
        "firstApprovedDate": "2026-02-10",
        "firstApprovedRegion": "dcgfsd"
    },
    "PhysicalChemicalProperties": {
        "innName": "dsfgdf",
        "synonyms": "dsfgfd",
        "iupacName": "dcxgbdfhtd",
        "molecularWeight": "rfhtfdt",
        "molecularFormula": "rfgrdf",
        "bcsClass": "rfhe",
        "monoisotopicMass": "fdht",
        "structureName": "rhfdht",
        "stereochemistry": "dfhbg",
        "solubility": "fhfgd",
        "pka": "fdhg",
        "logp": "fgnhfg",
        "regulatoryInsights": "gnhgf",
        "regionalApproval": "hfdhfd",
        "additionalInfo": [
            {
                "drugName": "fdhgf",
                "region": "rjuetkr",
                "indication": "trjtrsea",
                "patientSegments": "rdhd",
                "dosageForm": "yktyk",
                "strength": "trktu",
                "approvedDate": "2026-02-10",
                "regulatoryBodies": "fgjhg,hj"
            },
            {
                "drugName": "tgkrt",
                "region": "gfjxg",
                "indication": "gfmj",
                "patientSegments": "gfm",
                "dosageForm": "gfmg",
                "strength": "yhkrt",
                "approvedDate": "2026-02-10",
                "regulatoryBodies": "gfkulyu"
            }
        ],
        "drugPatents": [
            {
                "designationType": "trkity",
                "expiryDate": "2026-02-10",
                "regulatoryBody": "kyultkyr",
                "exclusivityConsideration": "trujtky",
                "impactForGenericFilers": "ytkuil"
            },
            {
                "designationType": "yktuy",
                "expiryDate": "2026-02-10",
                "regulatoryBody": "ytkyu",

                "exclusivityConsideration": "ytku",

                "impactForGenericFilers": "ghkyu"

            }

        ],

        "genericEntrants": [

            {

                "anda": "ytkuy",

                "companyName": "ytkiu",

                "dosageDetails": "ytjt",

                "approvalType": "tkyiyii",

                "andaSubmissionDate": "2026-02-10",

                "tentativeApprovalDate": "2026-02-10",

                "finalApprovalDate": "2026-02-10",

                "ftfExclusivity": "yjtyjut"

            },

            {

                "anda": "9oilyu",

                "companyName": "ytky",

                "dosageDetails": "ytkrxfs",

                "approvalType": "tjreds",

                "andaSubmissionDate": "2026-02-10",

                "tentativeApprovalDate": "2026-02-10",

                "finalApprovalDate": "2026-02-10",

                "ftfExclusivity": "gjetayert"

            }

        ],

        "genericsApprovedByEma": [

            {

                "companyName": "trjtyk",

                "drugName": "rtsyty",

                "dosageDetails": "rtyhtrjt",

                "chmpOpinion": "rhijytt",

                "ecDecision": "riyj",

                "ecApprovalDate": "2026-02-10"

            },

            {

                "companyName": "rtktyuhky",

                "drugName": "yhjuy",

                "dosageDetails": "trjytku",

                "chmpOpinion": "trjxrf",

                "ecDecision": "jtyd",

                "ecApprovalDate": "2026-02-10"

            },

            {

                "companyName": "ewtrtjys",

                "drugName": "rehsytu",

                "dosageDetails": "sedhdfmgg",

                "chmpOpinion": "fdnhf",

                "ecDecision": "fhg",

                "ecApprovalDate": "2026-02-10"

            },

            {

                "companyName": "fhgmh",

                "drugName": "fhf",

                "dosageDetails": "fdjrgj",

                "chmpOpinion": "jgdrfj",

                "ecDecision": "dhgjty",

                "ecApprovalDate": "2026-02-10"

            }

        ]

    },

    "ProcessDevelopment": {

        "availableDmfVendors": [

            {

                "dmf": "fgjhc",

                "regulatoryBody": "gfjh",

                "status": "fgmgh",

                "type": "gfnh",

                "submissionDate": "2026-02-10",

                "holder": "vbmhgmh",

                "apiForm": "gvbmhg"

            },

            {

                "dmf": "nfgngh",

                "regulatoryBody": "gmhmg",

                "status": "hgngh",

                "type": "gfjngdc",

                "submissionDate": "2026-02-10",

                "holder": "gmjgxh",

                "apiForm": "gfxng"

            }

        ],

        "manufacturingRoutes": [

            {

                "step": "gncbmgc"

            },

            {

                "step": "gfmg"

            }

        ],

        "dsImpurities": [

            {

                "impurities": "gjgh",

                "knownImpurities": "gfnfg",

                "specified": "hnjgh",

                "unknownImpurities": "fhgbvjh"

            },

            {

                "impurities": "gfmgh",

                "knownImpurities": "fgmgyh",

                "specified": "gfngc",

                "unknownImpurities": "gfjnyghdc"

            }

        ],

        "genotoxicImpurities": [

            {

                "genotoxicImpurities": "gfmgh",

                "classOfImpurity": "gfhjmgch"

            },

            {

                "genotoxicImpurities": "hmgh",

                "classOfImpurity": "gjgh"

            }

        ],

        "stability": "ghmjgh",

        "nitrosaminesAssessment": "hgmc",

        "otherInformation": "hgm,gh",

        "regulatoryStartingMaterials": "hgmhg",

        "drugSubstanceSpecifications": "gfjnygh"

    },

    "AnalyticalDevelopment": {

        "dosageFormAndStrength": [

            {

                "strength": "gfjgh",

                "dosageForm": "ghmg",

                "size": "hgmgh",

                "color": "mhgmhg",

                "imprinting": "hnmh",

                "weight": "ghbmjh",

                "packaging": "hgmgh",

                "ndcCode": "hgmgh",

                "images": ""

            }

        ],

        "supplyChain": [

            {

                "genotoxicImpurities": "hgmgh",

                "classOfImpurity": "ghmhj"

            }

        ],

        "manufacturingProcess": [

            {

                "dsImpurities": "hgmh",

                "knownImpurities": "hgmhg",

                "specifiedImpurities": "ghm",

                "unknownImpurities": "hmghc"

            }

        ],

        "baBeStudies": [

            {

                "studyType": "gmhmgh",

                "dosageForm": "hgmghch",

                "dosageStrength": "ghc",

                "studyDesign": "ghmhj",

                "studyCondition": "yhgjy",

                "additionalDetails": "gjyf",

                "endPoint": "mghmh"

            }

        ],

        "shelfLife": [

            {

                "currentExpirationDate": "2026-02-10",

                "strength": "jtrgf",

                "expiryDate": "2026-02-10"

            }

        ],

        "stabilityStudies": "gfmygh",

        "biowaiverRequest": "hgjngyh",

        "dissolutionTestMethodAndSamplingTimes": "ghfmjgh",

        "formulationChallenges": "gfmgh"

    },

    "DrugProductInformation": {

        "labelingInformation": [

            {

                "image": ""

            }

        ],

        "unmetClinicalNeed": "fgmgh",

        "glossary": "hgmhg"

    },

    "Appendices": {

        "appendices": [

            {

                "appendix": "hgmc"

            }

        ]

    }

}
"""

try:
    data = json.loads(json_data)
    validated = NewDrugData(**data)
    print("Validation Successful!")
except Exception as e:
    print(f"Validation Failed: {e}")
