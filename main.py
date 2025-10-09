from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from login import login_router
from drug import drug_router

app = FastAPI()

origins = [
    "http://localhost:3004",
    "http://127.0.0.1:3000",
    "https://cmcintel.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login_router)
app.include_router(drug_router)

@app.get("/", response_model=dict)
async def root():
    return {"message": "ChemBank API is running"}
