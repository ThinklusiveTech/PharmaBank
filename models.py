from pydantic import BaseModel
from typing import Dict, List, Optional, Union, Any

class Users(BaseModel):
    name: str
    email: str
    password: str
    roles: Optional[List[str]] = ["user"]

class ForgotPasswordRequest(BaseModel):
    email: str
    new_password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class InactiveIngredient(BaseModel):
    ingredient_name: str
    percentage_w_w: str

class Reference(BaseModel):
    title: str
    url: str

class DrugData(BaseModel):
    cid: Optional[Any] = None
    marketInformation: Optional[Any] = None
    drugSubstance: Optional[Any] = None
    drugProduct: Optional[Any] = None
    appendices: Optional[Any] = None
    references: Optional[Any] = None
