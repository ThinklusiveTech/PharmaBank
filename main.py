from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/", response_model=dict)
async def root():
    return {"message": "MongoDB is connected"}

# Import routes so FastAPI registers them
import login
import drug
