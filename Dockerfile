<<<<<<< HEAD
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for bcrypt & psycopg2/mongo drivers)
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (so Docker caches pip install)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Expose port (optional but useful for clarity)
EXPOSE 8000

# Run FastAPI with uvicorn
=======
# Use official Python base image
FROM python:3.12

# Copy project files
COPY . .

# Set working directory
WORKDIR /

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start FastAPI app
>>>>>>> main
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
