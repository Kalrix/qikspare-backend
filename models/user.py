from datetime import datetime
from pydantic import BaseModel, Field, constr
from typing import List, Optional, Dict

# -----------------------------------
# Address Model
# -----------------------------------
class Address(BaseModel):
    address_id: Optional[str] = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    tag: Optional[str] = "others"  # home / garage / workshop / others
    address_line: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    location: Optional[Dict[str, float]] = None  # { "lat": float, "lng": float }
    is_default: Optional[bool] = False
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

# -----------------------------------
# Main User Model
# -----------------------------------
class User(BaseModel):
    # Identity
    full_name: Optional[str] = None
    phone: Optional[constr(strip_whitespace=True, min_length=10, max_length=15)] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None
    role: Optional[str] = "customer"  # customer / garage / vendor / admin / rider / oem

    # Garage/Vendor/Business
    garage_name: Optional[str] = None
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    garage_size: Optional[str] = None
    distributor_size: Optional[str] = None

    # Category Specialization
    brands_served: Optional[List[str]] = None
    vehicle_types: Optional[List[str]] = None
    brands_carried: Optional[List[str]] = None
    category_focus: Optional[List[str]] = None

    # Compliance
    pan_number: Optional[str] = None
    gstin: Optional[str] = None
    kyc_status: Optional[str] = "optional"  # optional / pending / verified / rejected
    documents: Optional[List[str]] = None

    # Rider-specific fields
    warehouse_assigned: Optional[str] = None
    vehicle_type: Optional[str] = None
    vehicle_number: Optional[str] = None

    # Location & Addresses
    location: Optional[Dict[str, float]] = None  # { "lat": float, "lng": float }
    addresses: Optional[List[Address]] = None

    # Referral System
    referral_code: Optional[str] = None
    referred_by: Optional[str] = None
    referral_count: Optional[int] = 0
    referral_users: Optional[List[str]] = None

    # Meta
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
