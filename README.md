
# ChemBank API

## Prerequisites
- Python 3.8+ (for local), OR
- Docker & Docker Compose (for containerized run)

## Setup

### Option 1: Running with Docker (Recommended)

This will start both the API and a local MongoDB instance.

1.  **Build and Run**:
    ```powershell
    docker-compose up --build
    ```

    The API will be available at `http://127.0.0.1:8000`.
    MongoDB will be available at `mongodb://localhost:27017`.

2.  **Stop**:
    Press `Ctrl+C` or run:
    ```powershell
    docker-compose down
    ```

### Option 2: Running Locally (Manual)

1.  **Create/Activate Virtual Environment**:
    ```powershell
    # Windows
    python -m venv venv
    .\venv\Scripts\Activate
    ```

2.  **Install Dependencies**:
    ```powershell
    pip install -r requirements.txt
    ```

3.  **Environment Variables**:
    Make sure you have a `.env` file or set the following environment variables (defaults are in `database.py`):
    - `MONGO_URL`: Connection string for MongoDB
    - `DB_NAME`: Database name (default: `chembank`)

4.  **Start the Server**:
    ```powershell
    uvicorn main:app --reload
    ```

## API Documentation
Once running, you can access the interactive API docs at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
