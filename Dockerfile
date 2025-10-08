# Use official Python image
FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Install system dependencies for bcrypt and build tools
RUN apt-get update && \
    apt-get install -y build-essential libffi-dev libssl-dev git && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose FastAPI port
EXPOSE 8000


# Run FastAPI using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

