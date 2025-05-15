from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal, Union
from datetime import datetime

# ---------------------- COMMON MODELS ----------------------

class Location(BaseModel):
    addressLine: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class BankDetails(BaseModel):
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    bank_name: Optional[str] = None
    beneficiary_name: Optional[str] = None
    upi_id: Optional[str] = None

# ---------------------- BASE USER ----------------------

class BaseUser(BaseModel):
    full_name: str
    phone: str
    email: Optional[EmailStr] = None
    role: Literal["admin", "vendor", "garage", "delivery"]
    pin: Optional[str] = None
    referral_code: Optional[str] = None
    referred_by: Optional[str] = None
    referral_count: int = 0
    referral_users: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ---------------------- SPECIFIC USER TYPES ----------------------

class AdminUser(BaseUser):
    role: Literal["admin"]

class VendorUser(BaseUser):
    role: Literal["vendor"]
    business_name: str
    business_type: Optional[str] = None
    gstin: Optional[str] = None
    pan_number: Optional[str] = None
    distributor_size: Optional[str] = None
    brands_carried: List[str] = []
    category_focus: List[str] = []
    kyc_status: Optional[str] = "optional"
    documents: List[dict] = []
    location: Location
    addresses: List[Location] = []
    bank_details: Optional[BankDetails] = None

class GarageUser(BaseUser):
    role: Literal["garage"]
    garage_name: str
    garage_size: Optional[str] = None
    brands_served: List[str] = []
    vehicle_types: List[str] = []
    category_focus: List[str] = []
    gstin: Optional[str] = None
    pan_number: Optional[str] = None
    kyc_status: Optional[str] = "optional"
    documents: List[dict] = []
    location: Location
    addresses: List[Location] = []

class DeliveryUser(BaseUser):
    role: Literal["delivery"]
    vehicle_type: str
    vehicle_number: Optional[str] = None
    warehouse_assigned: Optional[str] = None
    location: Location

# ---------------------- UPDATE VARIANTS ----------------------

class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    pin: Optional[str] = None

class VendorUserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    pin: Optional[str] = None
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    gstin: Optional[str] = None
    pan_number: Optional[str] = None
    distributor_size: Optional[str] = None
    brands_carried: Optional[List[str]] = None
    category_focus: Optional[List[str]] = None
    kyc_status: Optional[str] = None
    documents: Optional[List[dict]] = None
    location: Optional[Location] = None
    addresses: Optional[List[Location]] = None
    bank_details: Optional[BankDetails] = None

class GarageUserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    pin: Optional[str] = None
    garage_name: Optional[str] = None
    garage_size: Optional[str] = None
    brands_served: Optional[List[str]] = None
    vehicle_types: Optional[List[str]] = None
    category_focus: Optional[List[str]] = None
    gstin: Optional[str] = None
    pan_number: Optional[str] = None
    kyc_status: Optional[str] = None
    documents: Optional[List[dict]] = None
    location: Optional[Location] = None
    addresses: Optional[List[Location]] = None

class DeliveryUserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    pin: Optional[str] = None
    vehicle_type: Optional[str] = None
    vehicle_number: Optional[str] = None
    warehouse_assigned: Optional[str] = None
    location: Optional[Location] = None

# ---------------------- UNIFIED UPDATE MODEL ----------------------

class UserUpdateModel(
    AdminUserUpdate,
    VendorUserUpdate,
    GarageUserUpdate,
    DeliveryUserUpdate
):
    pass

# ---------------------- STORAGE / UTILS ----------------------

class UserInDB(BaseUser):
    id: Optional[str] = Field(alias="_id")

def create_user_model(data: dict) -> Union[AdminUser, VendorUser, GarageUser, DeliveryUser]:
    role = data.get("role")
    if role == "admin":
        return AdminUser(**data)
    elif role == "vendor":
        return VendorUser(**data)
    elif role == "garage":
        return GarageUser(**data)
    elif role == "delivery":
        return DeliveryUser(**data)
    else:
        raise ValueError("Invalid user role")
