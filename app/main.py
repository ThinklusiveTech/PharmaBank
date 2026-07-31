from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.handlers.login import login_router
from app.handlers.drug import drug_router
from app.handlers.bookmark import bookmark_router
from app.handlers.draft import draft_router
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    try:
        await ensure_default_users()
    except Exception as e:
        print(f"⚠️ Error ensuring default users on startup: {e}")
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

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Mount the uploads directory for serving images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/", response_model=dict)
async def root():
    return {"message": "ChemBank API is running"}