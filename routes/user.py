from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List, Dict
from database import get_database
from utils.jwt_utils import decode_access_token
from models.user import Address
from services.user_service import update_user_profile, add_user_address

router = APIRouter()

# --------------------------
# Auth Helper for Logged-in Users
# --------------------------
def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        token = authorization.split(" ")[1]
        return decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# --------------------------
# Update Profile Payload
# --------------------------
class UpdateProfileModel(BaseModel):
    full_name: Optional[str] = None
    garage_name: Optional[str] = None
    business_name: Optional[str] = None
    email: Optional[str] = None
    business_type: Optional[str] = None
    garage_size: Optional[str] = None
    brands_served: Optional[List[str]] = None
    vehicle_types: Optional[List[str]] = None
    distributor_size: Optional[str] = None
    brands_carried: Optional[List[str]] = None
    category_focus: Optional[List[str]] = None
    pan_number: Optional[str] = None
    gstin: Optional[str] = None
    location: Optional[Dict[str, float]] = None

# --------------------------
# Update User Profile
# --------------------------
@router.patch("/update-profile")
async def update_profile(payload: UpdateProfileModel, user=Depends(get_current_user)):
    return await update_user_profile(user.get("user_id"), payload)

# --------------------------
# Add Address Payload
# --------------------------
class AddAddressModel(BaseModel):
    tag: Optional[str] = "others"
    address_line: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    location: Optional[Dict[str, float]] = None
    is_default: Optional[bool] = False

# --------------------------
# Add New Address to Profile
# --------------------------
@router.post("/add-address")
async def add_address(payload: AddAddressModel, user=Depends(get_current_user)):
    return await add_user_address(user.get("user_id"), payload)
