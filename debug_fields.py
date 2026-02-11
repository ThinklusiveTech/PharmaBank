
import sys
import os

# Add the project directory to sys.path
sys.path.append(r'c:\Users\Pratyusha Yasalapu\Downloads\chemBank 2\chemBank')

from models import NewDrugData
import pydantic

print(f"Pydantic version: {pydantic.__version__}")

for field_name, field in NewDrugData.model_fields.items():
    print(f"Field: {field_name}, Type: {field.annotation}")
