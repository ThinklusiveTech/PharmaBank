from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.handlers.login import login_router
from app.handlers.drug import drug_router
from app.handlers.bookmark import bookmark_router
from app.handlers.draft import draft_router
from app.handlers.master_data import master_data_router
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os


async def ensure_default_users():
    """Ensure standard system users automatically exist in MongoDB on startup"""
    from app.database import db
    from app.hashing import get_password_hash

    default_users = [
        {
            "name": "ChemBank Admin",
            "email": "admin@chembank.com",
            "password": "admin123",
            "roles": ["admin"],
            "status": "active",
            "isActive": True
        },
        {
            "name": "ChemBank Editor",
            "email": "editor@chembank.com",
            "password": "editor123",
            "roles": ["editor"],
            "status": "active",
            "isActive": True
        },
        {
            "name": "ChemBank Subscriber",
            "email": "subscriber@chembank.com",
            "password": "subscriber123",
            "roles": ["subscriber"],
            "status": "active",
            "isActive": True
        }
    ]


    for u in default_users:
        existing = await db.users.find_one({"email": u["email"]})
        if not existing:
            hashed_pwd = get_password_hash(u["password"])
            user_data = {
                "name": u["name"],
                "email": u["email"],
                "password": hashed_pwd,
                "roles": u["roles"]
            }
            await db.users.insert_one(user_data)
            print(f"✅ Auto-created missing default user: {u['email']}")


async def ensure_master_data():
    """Ensure master data (countries, regulatory authorities, therapeutic areas) exist in MongoDB on startup"""
    from app.database import db
    from scripts.seed_master_data import THERAPEUTIC_AREAS_DATA, REGIONS_COUNTRIES_DATA, REGULATORY_AUTHORITIES_DATA

    if await db.therapeutic_areas.count_documents({}) == 0:
        ta_docs = [{"area": area, "indications": indications} for area, indications in THERAPEUTIC_AREAS_DATA.items()]
        await db.therapeutic_areas.insert_many(ta_docs)
        print(f"✅ Auto-seeded {len(ta_docs)} Therapeutic Areas")

    if await db.regions_countries.count_documents({}) == 0:
        rc_docs = [{"region": region, "countries": countries} for region, countries in REGIONS_COUNTRIES_DATA.items()]
        await db.regions_countries.insert_many(rc_docs)
        print(f"✅ Auto-seeded {len(rc_docs)} Regions & Countries")

    if await db.regulatory_authorities.count_documents({}) == 0:
        await db.regulatory_authorities.insert_many(REGULATORY_AUTHORITIES_DATA)
        print(f"✅ Auto-seeded {len(REGULATORY_AUTHORITIES_DATA)} Regulatory Authorities")


async def ensure_drug_timestamps():
    """Ensure all existing drugs in MongoDB have valid createdAt and updatedAt fields"""
    from app.database import db
    from bson import ObjectId
    from datetime import datetime, timezone

    cursor = db.drugs.find({})
    updated_count = 0
    async for drug in cursor:
        d_id = drug.get("_id")
        po = drug.get("ProductOverview") if isinstance(drug.get("ProductOverview"), dict) else {}
        
        # Determine existing or fallback creation timestamp
        created_at = drug.get("createdAt") or po.get("createdAt")
        if not created_at and d_id and ObjectId.is_valid(str(d_id)):
            created_at = ObjectId(str(d_id)).generation_time.isoformat()
        if not created_at:
            created_at = datetime.now(timezone.utc).isoformat()

        # Determine existing or fallback update timestamp
        updated_at = drug.get("updatedAt") or po.get("updatedAt") or created_at

        # If fields are missing in document or ProductOverview, update MongoDB
        needs_update = (
            not drug.get("createdAt") or
            not drug.get("updatedAt") or
            ("ProductOverview" in drug and isinstance(drug["ProductOverview"], dict) and (
                not drug["ProductOverview"].get("createdAt") or
                not drug["ProductOverview"].get("updatedAt")
            ))
        )

        if needs_update and d_id:
            update_fields = {
                "createdAt": created_at,
                "updatedAt": updated_at
            }
            if "ProductOverview" in drug and isinstance(drug["ProductOverview"], dict):
                update_fields["ProductOverview.createdAt"] = created_at
                update_fields["ProductOverview.updatedAt"] = updated_at

            await db.drugs.update_one(
                {"_id": d_id},
                {"$set": update_fields}
            )
            updated_count += 1

    if updated_count > 0:
        print(f"✅ Migrated timestamps for {updated_count} existing drugs in MongoDB")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    try:
        await ensure_default_users()
        await ensure_master_data()
        await ensure_drug_timestamps()
    except Exception as e:
        print(f"⚠️ Error during startup initialization: {e}")
    yield


app = FastAPI(lifespan=lifespan)

# CORS configuration
environment = os.getenv("ENVIRONMENT", "development")
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")

if allowed_origins_env:
    origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
elif environment == "production":
    origins = [
        "https://cmcintel.com",
        "http://localhost:3000",  # Docker port mapping (used in docker-compose)
        "http://localhost:3004",  # Vite local dev port
        "http://localhost:5173",  # Vite default/fallback dev port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3004",
        "http://127.0.0.1:5173",
    ]
else:
    origins = ["*"]  # Allow all origins in development

# Allow credentials only if we are using explicit origins (non-wildcard)
allow_credentials = "*" not in origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://(.*\.)?cmcintel\.com",
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login_router, prefix="/v1")
app.include_router(drug_router, prefix="/v1")
app.include_router(bookmark_router, prefix="/v1")
app.include_router(draft_router, prefix="/v1")
app.include_router(master_data_router, prefix="/v1")

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Mount the uploads directory for serving images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/", response_model=dict)
async def root():
    return {"message": "ChemBank API is running"}