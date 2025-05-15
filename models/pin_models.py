from pydantic import BaseModel, Field
from typing import Optional

class CreatePinModel(BaseModel):
    pin: str = Field(min_length=4, max_length=4)
    confirm_pin: str = Field(min_length=4, max_length=4)

class VerifyPinModel(BaseModel):
    phone: str
    pin: str

class ResetPinModel(BaseModel):
    phone: str
    otp: str
    new_pin: str = Field(min_length=4, max_length=4)
    confirm_pin: str = Field(min_length=4, max_length=4)
