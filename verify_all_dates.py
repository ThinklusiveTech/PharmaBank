
import json
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union, List, Any

# Mocking the consolidated logic and models
def handle_date_field(v):
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return int(v)
    if isinstance(v, str):
        formats = (
            '%Y-%m-%d', '%d-%m-%Y',
            '%Y/%m/%d', '%d/%m/%Y',
            '%Y.%m.%d', '%d.%m.%Y'
        )
        for fmt in formats:
            try:
                dt = datetime.strptime(v, fmt)
                return int(dt.timestamp())
            except ValueError:
                continue
    return v

class MarketInformation(BaseModel):
    firstApprovedDate: Optional[Union[int, str]] = None
    @field_validator('firstApprovedDate', mode='before')
    @classmethod
    def validate_date(cls, v):
        return handle_date_field(v)

class DrugUpdate(BaseModel):
    MarketInformation: Optional[MarketInformation] = None

print("--- Testing Various Formats ---")
formats_to_test = [
    ("27-12-2001", "DD-MM-YYYY"),
    ("2001-12-27", "YYYY-MM-DD"),
    ("27/12/2001", "DD/MM/YYYY"),
    ("2001/12/27", "YYYY/MM/DD"),
    ("27.12.2001", "DD.MM.YYYY"),
    ("2001.12.27", "YYYY.MM.DD"),
    (1009432800, "Integer Timestamp")
]

for ds, desc in formats_to_test:
    val = handle_date_field(ds)
    print(f"Testing {ds} ({desc}): {val} (type: {type(val)})")

print("\n--- Testing Model Validation ---")
data = {
    "MarketInformation": {
        "firstApprovedDate": "27-12-2001"
    }
}
update = DrugUpdate(**data)
dump = update.model_dump(exclude_unset=True)
print("Model Dump (Update):", dump)
assert isinstance(dump["MarketInformation"]["firstApprovedDate"], int)

data_slash = {
    "MarketInformation": {
        "firstApprovedDate": "27/12/2001"
    }
}
update_slash = DrugUpdate(**data_slash)
dump_slash = update_slash.model_dump(exclude_unset=True)
print("Model Dump (Update with Slash):", dump_slash)
assert isinstance(dump_slash["MarketInformation"]["firstApprovedDate"], int)

print("\nVerification Successful!")
