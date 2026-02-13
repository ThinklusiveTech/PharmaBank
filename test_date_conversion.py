
import json
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union, List, Any

# Copying relevant models from models.py to test logic locally
class MarketInformation(BaseModel):
    firstApprovedDate: Optional[Union[int, str]] = None

    @field_validator('firstApprovedDate', mode='before')
    @classmethod
    def handle_date_field(cls, v):
        if isinstance(v, (int, float)):
            return int(v)
        if isinstance(v, str):
            for fmt in ('%Y-%m-%d', '%d-%m-%Y'):
                try:
                    dt = datetime.strptime(v, fmt)
                    return int(dt.timestamp())
                except ValueError:
                    continue
        return v

class NewDrugData(BaseModel):
    market_information: Optional[MarketInformation] = Field(None, alias="MarketInformation")

# Test case
test_data = {
    "MarketInformation": {
        "firstApprovedDate": "27-12-2001"
    }
}

try:
    validated = NewDrugData(**test_data)
    dumped = validated.model_dump(by_alias=True)
    print("Validated Data:", json.dumps(dumped, indent=2))
    
    date_val = dumped["MarketInformation"]["firstApprovedDate"]
    print(f"Type of firstApprovedDate: {type(date_val)}")
    print(f"Value: {date_val}")
    
    # Expected: 1009411200 (approx, depends on timezone if not specified, 
    # but datetime.strptime uses local time and timestamp() too)
    
except Exception as e:
    print(f"Error: {e}")
