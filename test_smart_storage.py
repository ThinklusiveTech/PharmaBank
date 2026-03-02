
import json
import base64
import os
import uuid
from typing import Optional, List, Dict, Any

# Mocking the utility and requirements for local testing
def process_base64_images(data, uploads_dir="test_uploads"):
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        
    if isinstance(data, dict):
        if "imageData" in data and isinstance(data["imageData"], str) and data["imageData"].startswith("data:image/"):
            base64_str = data["imageData"]
            try:
                header, encoded = base64_str.split(",", 1)
                mime_type = header.split(";")[0].split(":")[1]
                ext = mime_type.split("/")[1]
                if ext == "jpeg": ext = "jpg"
                
                image_data = base64.b64decode(encoded)
                unique_filename = f"{uuid.uuid4()}.{ext}"
                file_path = os.path.join(uploads_dir, unique_filename)
                
                with open(file_path, "wb") as f:
                    f.write(image_data)
                
                data["imageData"] = f"/uploads/{unique_filename}"
                print(f"DEBUG: Saved to {file_path}")
            except Exception as e:
                print(f"ERROR: {e}")

        for k, v in data.items():
            process_base64_images(v, uploads_dir)
    elif isinstance(data, list):
        for item in data:
            process_base64_images(item, uploads_dir)
    return data

# Dummy Base64 image (1x1 red dot)
RED_DOT_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

test_payload = {
    "MarketInformation": {
        "drugName": "TestDrug"
    },
    "PhysicalChemicalProperties": {
        "structure": {
            "imageData": RED_DOT_BASE64,
            "fileName": "dot.png",
            "contentType": "image/png"
        }
    },
    "AnalyticalDevelopment": {
        "dosageFormAndStrength": [
            {
                "images": [
                    {
                        "imageData": RED_DOT_BASE64,
                        "fileName": "dot2.png",
                        "contentType": "image/png"
                    }
                ]
            }
        ]
    }
}

print("--- Testing Smart Image Processing ---")
processed = process_base64_images(test_payload)
print("\nProcessed Payload Structure (excerpts):")
print(f"Structure Image URL: {processed['PhysicalChemicalProperties']['structure']['imageData']}")
print(f"Dosage Image URL: {processed['AnalyticalDevelopment']['dosageFormAndStrength'][0]['images'][0]['imageData']}")

assert processed['PhysicalChemicalProperties']['structure']['imageData'].startswith("/uploads/")
assert processed['AnalyticalDevelopment']['dosageFormAndStrength'][0]['images'][0]['imageData'].startswith("/uploads/")

print("\nVerification Successful!")

# Cleanup test directory
import shutil
if os.path.exists("test_uploads"):
    shutil.rmtree("test_uploads")
