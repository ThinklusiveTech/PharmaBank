from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.handlers.login import login_router
from app.handlers.drug import drug_router
from app.handlers.bookmark import bookmark_router
from app.handlers.draft import draft_router
from fastapi.responses import FileResponse
import os


app = FastAPI()

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