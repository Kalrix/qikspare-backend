from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, Dict
from database import get_database
from utils.jwt_utils import create_access_token, decode_access_token
from models.user import create_user_model, Location
from bson import ObjectId
import datetime
import uuid
import httpx

router = APIRouter()

# ---- CONFIG ----
TWOFACTOR_API_KEY = "acd01d56-2fbd-11f0-8b17-0200cd936042"
OTP_TEMPLATE_NAME = "QIKSPARE"
TWOFACTOR_BASE = f"https://2factor.in/API/V1/{TWOFACTOR_API_KEY}/SMS"
ROLES = ["admin", "vendor", "garage", "delivery"]

# -------- MODELS --------
class RequestOtpModel(BaseModel):
    phone: str

class VerifyOtpModel(BaseModel):
    phone: str
    otp: str
    role: str
    referral_code: Optional[str] = None

class AddAddressModel(BaseModel):
    tag: Optional[str] = "others"
    address_line: str
    city: str
    state: str
    pincode: str
    location: Optional[Dict[str, float]] = None
    is_default: Optional[bool] = False

# -------- Helpers --------
def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        token = authorization.split(" ")[1]
        return decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

async def find_user_by_phone(phone: str):
    db = get_database()
    for role in ROLES:
        user = await db[f"{role}_users"].find_one({"phone": phone})
        if user:
            return user, role
    return None, None

async def get_user_by_id(user_id: str):
    db = get_database()
    for role in ROLES:
        user = await db[f"{role}_users"].find_one({"_id": ObjectId(user_id)})
        if user:
            return user, role
    return None, None

# -------- OTP Request --------
@router.post("/request-otp")
async def request_otp(payload: RequestOtpModel):
    phone = payload.phone
    url = f"{TWOFACTOR_BASE}/{phone}/AUTOGEN/{OTP_TEMPLATE_NAME}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    data = response.json()
    if data["Status"] != "Success":
        raise HTTPException(status_code=500, detail="Failed to send OTP")
    return {"message": "OTP sent successfully."}

# -------- Verify OTP & Register/Login --------
@router.post("/verify-otp")
async def verify_otp(payload: VerifyOtpModel):
    db = get_database()
    phone = payload.phone
    role = payload.role
    referral_code = payload.referral_code

    if role not in ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Step 1: Verify OTP
    url = f"{TWOFACTOR_BASE}/VERIFY3/{phone}/{payload.otp}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    if response.json().get("Status") != "Success":
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Step 2: Login if user exists
    user, found_role = await find_user_by_phone(phone)
    if user:
        if role == "admin" and found_role != "admin":
            raise HTTPException(status_code=403, detail="Unauthorized as admin")
        token_data = {
            "user_id": str(user["_id"]),
            "phone": phone,
            "role": found_role
        }
        return {"access_token": create_access_token(token_data)}

    # Step 3: Register new user
    if role == "admin":
        count = await db["admin_users"].count_documents({})
        if count > 0:
            raise HTTPException(status_code=403, detail="Admin registration blocked")
        new_ref_code = "QIKSPARE01"
        referred_by = None
    else:
        new_ref_code = str(uuid.uuid4())[:8].upper()
        referred_by = None
        if referral_code:
            ref_user, ref_role = await find_user_by_phone(referral_code)
            if not ref_user:
                raise HTTPException(status_code=400, detail="Invalid referral code")
            referred_by = referral_code
            await db[f"{ref_role}_users"].update_one(
                {"referral_code": referral_code},
                {
                    "$inc": {"referral_count": 1},
                    "$push": {"referral_users": str(ref_user["_id"])}
                }
            )

    # Base payload for new user
    payload_dict = {
        "full_name": "New User",  # ✅ Default to avoid Pydantic validation error
        "phone": phone,
        "role": role,
        "pin": None,
        "referral_code": new_ref_code,
        "referred_by": referred_by,
        "referral_count": 0,
        "referral_users": [],
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow()
    }

    if role != "admin":
        payload_dict["location"] = Location().dict()
        payload_dict["addresses"] = []

    user_obj = create_user_model(payload_dict)
    result = await db[f"{role}_users"].insert_one(user_obj.dict())

    token_data = {
        "user_id": str(result.inserted_id),
        "phone": phone,
        "role": role
    }
    return {"access_token": create_access_token(token_data)}

# -------- Get Profile --------
@router.get("/me")
async def get_profile(user=Depends(get_current_user)):
    user_data, role = await get_user_by_id(user.get("user_id"))
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    user_data["_id"] = str(user_data["_id"])
    user_data["role"] = role
    return user_data

# -------- Add Address --------
@router.post("/add-address")
async def add_address(payload: AddAddressModel, user=Depends(get_current_user)):
    db = get_database()
    user_id = user.get("user_id")
    role = user.get("role")

    if role == "admin":
        raise HTTPException(status_code=403, detail="Admins don't have address")

    result = await db[f"{role}_users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"addresses": payload.dict()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Failed to add address")

    return {"message": "Address added successfully"}
