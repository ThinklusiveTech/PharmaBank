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
if environment == "production":
    origins = [
        "https://cmcintel.com",
        "http://localhost:3004",  # Allow localhost for testing
    ]
else:
    origins = ["*"]  # Allow all origins in development

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
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