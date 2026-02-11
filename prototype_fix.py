
from pydantic import BaseModel, Field
from typing import Optional

class MarketInformation(BaseModel):
    version: Optional[str] = None

class NewDrugData(BaseModel):
    # Using alias to avoid shadowing
    market_info: Optional[MarketInformation] = Field(None, alias="MarketInformation")

payload = {"MarketInformation": {"version": "1"}}
try:
    data = NewDrugData(**payload)
    print("Validation successful!")
    print(f"Data: {data.model_dump(by_alias=True)}")
    print(f"Internal name 'market_info': {data.market_info}")
except Exception as e:
    print(f"Validation failed: {e}")

class NewDrugDataShadowed(BaseModel):
    MarketInformation: Optional[MarketInformation] = None

try:
    data = NewDrugDataShadowed(**payload)
    print("Shadowed Validation successful!")
except Exception as e:
    print(f"Shadowed Validation failed: {e}")
