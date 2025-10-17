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
    cid: Optional[str] = None
    marketInformation: Optional[Dict[str, Any]] = None
    drugSubstance: Optional[Dict[str, Any]] = None
    drugProduct: Optional[Dict[str, Any]] = None
    appendices: Optional[Dict[str, Any]] = None
    references: Optional[List[Dict[str, Any]]] = None
