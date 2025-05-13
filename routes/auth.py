from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from database import get_database
from utils.jwt_utils import create_access_token, decode_access_token
from bson import ObjectId
import datetime
import uuid
import httpx

router = APIRouter()

# ---- CONFIG ----
TWOFACTOR_API_KEY = "acd01d56-2fbd-11f0-8b17-0200cd936042"
OTP_TEMPLATE_NAME = "QIKSPARE"  # Must match your 2Factor template name
TWOFACTOR_BASE = f"https://2factor.in/API/V1/{TWOFACTOR_API_KEY}/SMS"

# -------- MODELS --------
class RequestOtpModel(BaseModel):
    phone: str

class VerifyOtpModel(BaseModel):
    phone: str
    otp: str
    role: str  # garage / workshop / mechanic / admin / vendor
    referral_code: Optional[str] = None

# -------- Send OTP --------
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

# -------- Verify OTP --------
@router.post("/verify-otp")
async def verify_otp(payload: VerifyOtpModel):
    db = get_database()
    phone, otp = payload.phone, payload.otp
    role, referral_code = payload.role, payload.referral_code

    # Step 1: Verify OTP with 2Factor
    url = f"{TWOFACTOR_BASE}/VERIFY3/{phone}/{otp}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    data = response.json()

    if data["Status"] != "Success":
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Step 2: Check if user exists
    user = await db["users"].find_one({"phone": phone})

    if user:
        if role == "admin" and user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Unauthorized as admin")
        token_data = {"user_id": str(user["_id"]), "phone": phone, "role": user["role"]}
        return {"access_token": create_access_token(token_data)}

    # Step 3: Register new user
    user_count = await db["users"].count_documents({})
    referred_by = None

    if role == "admin":
        if user_count == 0:
            new_ref_code = "QIKSPARE01"
        else:
            raise HTTPException(status_code=403, detail="Admin registration not allowed from app")
    else:
        new_ref_code = str(uuid.uuid4())[:8].upper()
        if referral_code:
            referrer = await db["users"].find_one({"referral_code": referral_code})
            if not referrer:
                raise HTTPException(status_code=400, detail="Invalid referral code")
            referred_by = referral_code

    new_user = {
        "full_name": None,
        "garage_name": None,
        "business_name": None,
        "phone": phone,
        "email": None,
        "password_hash": None,
        "role": role,
        "business_type": None,
        "garage_size": None,
        "brands_served": [],
        "vehicle_types": [],
        "addresses": [],
        "distributor_size": None,
        "brands_carried": [],
        "category_focus": [],
        "pan_number": None,
        "gstin": None,
        "kyc_status": "optional",
        "documents": [],
        "warehouse_assigned": None,
        "vehicle_type": None,
        "vehicle_number": None,
        "referral_code": new_ref_code,
        "referred_by": referred_by,
        "referral_count": 0,
        "referral_users": [],
        "location": None,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    }

    result = await db["users"].insert_one(new_user)
    user_id = result.inserted_id

    if referred_by:
        await db["users"].update_one(
            {"referral_code": referred_by},
            {
                "$inc": {"referral_count": 1},
                "$push": {"referral_users": str(user_id)}
            }
        )

    token_data = {"user_id": str(user_id), "phone": phone, "role": role}
    return {"access_token": create_access_token(token_data)}

# -------- Current User --------
def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        token = authorization.split(" ")[1]
        return decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.get("/me")
async def get_profile(user=Depends(get_current_user)):
    db = get_database()
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")

    user_data = await db["users"].find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    user_data["_id"] = str(user_data["_id"])
    return user_data
