from pydantic import BaseModel, Field
from typing import Optional

class CreatePinModel(BaseModel):
    """
    Used when creating or updating a user's PIN.
    """
    pin: str = Field(..., min_length=4, max_length=4, description="4-digit PIN")
    confirm_pin: str = Field(..., min_length=4, max_length=4, description="Confirm 4-digit PIN")


class VerifyPinModel(BaseModel):
    """
    Used when logging in using a PIN.
    """
    phone: str = Field(..., description="Registered phone number")
    pin: str = Field(..., min_length=4, max_length=4, description="4-digit login PIN")


class ResetPinModel(BaseModel):
    """
    Used for resetting a PIN after OTP verification.
    """
    phone: str = Field(..., description="Registered phone number")
    otp: str = Field(..., min_length=4, max_length=6, description="OTP received via SMS")
    new_pin: str = Field(..., min_length=4, max_length=4, description="New 4-digit PIN")
    confirm_pin: str = Field(..., min_length=4, max_length=4, description="Confirm new 4-digit PIN")
