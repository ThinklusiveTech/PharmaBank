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
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
