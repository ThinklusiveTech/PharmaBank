import asyncio
import os
import sys

# Add root project path to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db

THERAPEUTIC_AREAS_DATA = {
    "Allergy & Immunology": [
        "Allergic Rhinitis", "Asthma (severe)", "Atopic Dermatitis", "Chronic Urticaria",
        "Food Allergy", "Eosinophilic Esophagitis", "Systemic Lupus Erythematosus",
        "Ankylosing Spondylitis", "Alopecia Areata", "Vitiligo"
    ],
    "Cardiology": [
        "Heart Failure", "Atrial Fibrillation", "Chronic Coronary Syndrome", "Myocardial Infarction",
        "Arterial Hypertension", "Angina Pectoris", "Hypercholesterolemia", "Dyslipidemia",
        "Pulmonary Hypertension", "Arrhythmias", "Hypertrophic Cardiomyopathy",
        "Peripheral Arterial Disease", "Deep Vein Thrombosis", "Pulmonary Embolism",
        "Chronic Thromboembolic Pulmonary Hypertension", "Brugada Syndrome", "Acute Coronary Syndrome"
    ],
    "Dermatology": [
        "Psoriasis", "Atopic Dermatitis", "Psoriatic Arthritis", "Acne", "Rosacea",
        "Hidradenitis Suppurativa", "Chronic Urticaria", "Alopecia Areata", "Vitiligo",
        "Prurigo Nodularis", "Bullous Pemphigoid", "Actinic Keratosis"
    ],
    "Endocrinology & Metabolism": [
        "Type 1 Diabetes Mellitus", "Type 2 Diabetes Mellitus", "Obesity", "Hypothyroidism",
        "Hyperthyroidism", "Acromegaly", "Cushing Syndrome", "Growth Hormone Deficiency",
        "Hypoparathyroidism", "Nonalcoholic Steatohepatitis (NASH)", "Hyperparathyroidism", "Adrenal Insufficiency"
    ],
    "Gastroenterology": [
        "Crohn's Disease", "Ulcerative Colitis", "Gastroesophageal Reflux Disease (GERD)",
        "Irritable Bowel Syndrome", "Celiac Disease", "Eosinophilic Esophagitis",
        "Chronic Hepatitis B", "Chronic Hepatitis C", "Primary Biliary Cholangitis",
        "Primary Sclerosing Cholangitis", "Short Bowel Syndrome"
    ],
    "Hematology": [
        "Iron Deficiency Anemia", "Sickle Cell Disease", "Beta-Thalassemia", "Hemophilia A",
        "Hemophilia B", "Immune Thrombocytopenia (ITP)", "Paroxysmal Nocturnal Hemoglobinuria",
        "Aplastic Anemia", "Myelodysplastic Syndromes", "Polycythemia Vera", "Myelofibrosis"
    ],
    "Infectious Diseases": [
        "COVID-19", "Human Immunodeficiency Virus (HIV)", "Influenza", "Hepatitis B",
        "Hepatitis C", "Respiratory Syncytial Virus (RSV)", "Cytomegalovirus (CMV)",
        "Epstein-Barr Virus (EBV)", "Herpes Simplex Virus (HSV) Infection",
        "Varicella-Zoster Virus (VZV) / Shingles", "Tuberculosis", "Clostridioides difficile",
        "Invasive Aspergilosis", "Invasive Candidiasis", "Cryptococcal Meningitis"
    ],
    "Nephrology": [
        "Chronic Kidney Disease", "Diabetic Nephropathy", "IgA Nephropathy",
        "Focal Segmental Glomerulosclerosis", "Autosomal Dominant Polycystic Kidney Disease",
        "Lupus Nephritis", "Hyperkalemia", "Hyperphosphatemia", "Anemia of CKD"
    ],
    "Neurology": [
        "Multiple Sclerosis", "Parkinson's Disease", "Alzheimer's Disease", "Epilepsy",
        "Migraine", "Amyotrophic Lateral Sclerosis (ALS)", "Myasthenia Gravis",
        "Spinal Muscular Atrophy", "Huntington's Disease", "Restless Legs Syndrome",
        "Neuromyelitis Optica Spectrum Disorder", "Generalized Myasthenia Gravis"
    ],
    "Oncology": [
        "Non-Small Cell Lung Cancer (NSCLC)", "Small Cell Lung Cancer", "Breast Cancer (HER2+)",
        "Breast Cancer (HR+/HER2-)", "Triple-Negative Breast Cancer", "Colorectal Cancer",
        "Prostate Cancer", "Melanoma", "Renal Cell Carcinoma", "Ovarian Cancer",
        "Hepatocellular Carcinoma", "Gastric Cancer", "Pancreatic Cancer",
        "Acute Myeloid Leukemia (AML)", "Chronic Lymphocytic Leukemia (CLL)",
        "Multiple Myeloma", "Diffuse Large B-Cell Lymphoma", "Hodgkin Lymphoma",
        "Mantle Cell Lymphoma", "Bladder Cancer / Urothelial Carcinoma"
    ],
    "Ophthalmology": [
        "Neovascular (Wet) Age-Related Macular Degeneration", "Diabetic Macular Edema",
        "Diabetic Retinopathy", "Retinal Vein Occlusion", "Glaucoma", "Dry Eye Disease",
        "Uveitis", "Geographic Atrophy", "Presbyopia"
    ],
    "Psychiatry": [
        "Major Depressive Disorder", "Treatment-Resistant Depression", "Bipolar I Disorder",
        "Bipolar II Disorder", "Schizophrenia", "Generalized Anxiety Disorder",
        "Post-Traumatic Stress Disorder (PTSD)", "Attention-Deficit/Hyperactivity Disorder (ADHD)",
        "Obsessive-Compulsive Disorder", "Insomnia", "Binge Eating Disorder"
    ],
    "Pulmonology / Respiratory": [
        "Asthma", "Chronic Obstructive Pulmonary Disease (COPD)", "Idiopathic Pulmonary Fibrosis",
        "Cystic Fibrosis", "Pulmonary Arterial Hypertension", "Bronchiectasis", "Alpha-1 Antitrypsin Deficiency"
    ],
    "Rheumatology": [
        "Rheumatoid Arthritis", "Psoriatic Arthritis", "Ankylosing Spondylitis",
        "Systemic Lupus Erythematosus", "Gout", "Sjogren Syndrome", "Systemic Sclerosis (Scleroderma)",
        "Giant Cell Arteritis", "Polymyalgia Rheumatica"
    ],
    "Urology": [
        "Benign Prostatic Hyperplasia (BPH)", "Overactive Bladder", "Erectile Dysfunction",
        "Interstitial Cystitis", "Neurogenic Detrusor Overactivity", "Prostate Cancer"
    ],
    "Rare / Genetic Diseases": [
        "Duchenne Muscular Dystrophy", "Spinal Muscular Atrophy", "Gaucher Disease",
        "Fabry Disease", "Pompe Disease", "Mucopolysaccharidosis", "Hereditary Angioedema",
        "Alpha-1 Antitrypsin Deficiency", "Transthyretin Amyloidosis (ATTR)",
        "Achondroplasia", "Fibrodysplasia Ossificans Progressiva"
    ]
}

REGIONS_COUNTRIES_DATA = {
    "Africa": ["Egypt", "Kenya", "Morocco", "Nigeria", "South Africa", "Uganda"],
    "Asia": [
        "China", "Hong Kong", "India", "Israel", "Japan", "Malaysia", "Saudi Arabia",
        "Singapore", "South Korea", "Thailand", "Vietnam", "Indonesia", "Philippines", "Taiwan"
    ],
    "Europe": [
        "Belgium", "Denmark", "Finland", "France", "Germany", "Iceland", "Ireland",
        "Italy", "Netherlands", "Norway", "Spain", "Sweden", "Switzerland", "United Kingdom"
    ],
    "North America": ["Canada", "Mexico", "United States"],
    "Oceania": ["Australia", "New Zealand"],
    "South America": ["Brazil", "Argentina", "Chile", "Colombia", "Peru"]
}

REGULATORY_AUTHORITIES_DATA = [
    {"country": "United States", "authority": "Food and Drug Administration", "abbreviation": "FDA (USFDA)"},
    {"country": "European Union", "authority": "European Medicines Agency", "abbreviation": "EMA"},
    {"country": "United Kingdom", "authority": "Medicines and Healthcare products Regulatory Agency", "abbreviation": "MHRA"},
    {"country": "Canada", "authority": "Health Canada", "abbreviation": "HC"},
    {"country": "Australia", "authority": "Therapeutic Goods Administration", "abbreviation": "TGA"},
    {"country": "Japan", "authority": "Pharmaceuticals and Medical Devices Agency", "abbreviation": "PMDA"},
    {"country": "Japan", "authority": "Ministry of Health, Labour and Welfare", "abbreviation": "MHLW"},
    {"country": "China", "authority": "National Medical Products Administration", "abbreviation": "NMPA"},
    {"country": "India", "authority": "Central Drugs Standard Control Organisation", "abbreviation": "CDSCO"},
    {"country": "Switzerland", "authority": "Swiss Agency for Therapeutic Products", "abbreviation": "Swissmedic"},
    {"country": "South Korea", "authority": "Ministry of Food and Drug Safety", "abbreviation": "MFDS"},
    {"country": "Singapore", "authority": "Health Sciences Authority", "abbreviation": "HSA"},
    {"country": "Brazil", "authority": "National Health Surveillance Agency", "abbreviation": "ANVISA"},
    {"country": "Mexico", "authority": "Federal Commission for Protection against Sanitary Risks", "abbreviation": "COFEPRIS"},
    {"country": "New Zealand", "authority": "Medsafe", "abbreviation": "Medsafe"},
    {"country": "South Africa", "authority": "South African Health Products Regulatory Authority", "abbreviation": "SAHPRA"},
    {"country": "Saudi Arabia", "authority": "Saudi Food and Drug Authority", "abbreviation": "SFDA"},
    {"country": "Taiwan", "authority": "Taiwan Food and Drug Administration", "abbreviation": "TFDA"},
    {"country": "Israel", "authority": "Ministry of Health", "abbreviation": "IMOH"},
    {"country": "Russia", "authority": "Ministry of Health / Roszdravnadzor", "abbreviation": "Roszdravnadzor"},
    {"country": "Netherland", "authority": "Medicines Evaluation Board", "abbreviation": "MEB"},
    {"country": "Sweden", "authority": "Medical Products Agency", "abbreviation": "MPA"},
    {"country": "France", "authority": "French National Agency for the Safety of Medicines and Health Products", "abbreviation": "ANSM"},
    {"country": "Germany", "authority": "Federal Institute for Drugs and Medical Devices", "abbreviation": "BfArM"},
    {"country": "Denmark", "authority": "Danish Medicines Agency", "abbreviation": "DKMA (also DMA)"},
    {"country": "Norway", "authority": "Norwegian Medical Products Agency", "abbreviation": "NoMA"},
    {"country": "Belgium", "authority": "Federal Agency for Medicines and Health Products", "abbreviation": "FAMHP"},
    {"country": "Finland", "authority": "Finnish Medicines Agency", "abbreviation": "Fimea"},
    {"country": "Italy", "authority": "Italian Medicines Agency", "abbreviation": "AIFA"},
    {"country": "Ireland", "authority": "Health Products Regulatory Authority", "abbreviation": "HPRA"},
    {"country": "Iceland", "authority": "Icelandic Medicines Agency", "abbreviation": "IMA"},
    {"country": "Malaysia", "authority": "National Pharmaceutical Regulatory Agency", "abbreviation": "NPRA"},
    {"country": "Uganda", "authority": "National Drug Authority", "abbreviation": "NDA"},
    {"country": "Spain", "authority": "Spanish Agency of Medicines and Medical Devices", "abbreviation": "AEMPS"}
]


async def seed_master_data():
    print("Starting master data seeding...")

    # 1. Seed Therapeutic Areas
    await db.therapeutic_areas.delete_many({})
    ta_docs = [{"area": area, "indications": indications} for area, indications in THERAPEUTIC_AREAS_DATA.items()]
    await db.therapeutic_areas.insert_many(ta_docs)
    print(f"Seeded {len(ta_docs)} Therapeutic Areas into db.therapeutic_areas")

    # 2. Seed Regions and Countries
    await db.regions_countries.delete_many({})
    rc_docs = [{"region": region, "countries": countries} for region, countries in REGIONS_COUNTRIES_DATA.items()]
    await db.regions_countries.insert_many(rc_docs)
    print(f"Seeded {len(rc_docs)} Regions into db.regions_countries")

    # 3. Seed Regulatory Authorities
    await db.regulatory_authorities.delete_many({})
    await db.regulatory_authorities.insert_many(REGULATORY_AUTHORITIES_DATA)
    print(f"Seeded {len(REGULATORY_AUTHORITIES_DATA)} Regulatory Authorities into db.regulatory_authorities")

    print("Master data seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_master_data())
