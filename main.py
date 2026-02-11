from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from login import login_router
from drug import drug_router
from bookmark import bookmark_router
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

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Custom route to serve uploaded images with CORS headers
from fastapi.responses import FileResponse

@app.get("/uploads/{filename}")
async def get_upload(filename: str):
    file_path = os.path.join("uploads", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, headers={"Access-Control-Allow-Origin": "*"})

@app.get("/", response_model=dict)
async def root():
    return {"message": "ChemBank API is running"}