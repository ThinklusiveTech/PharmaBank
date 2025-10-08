from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# Allow frontend origins
origins = [
    "http://localhost:3004",          # local React dev
    "http://127.0.0.1:3000",
    "https://cmcintel.com",           # your frontend production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],              # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],              # Allow all headers
)


# ---------------- Root ----------------
@app.get("/", response_model=dict)
async def root():
    return {"message": "MongoDB is connected"}


# Import routes so FastAPI registers them
import login
import drug




