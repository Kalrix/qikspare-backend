from fastapi import APIRouter, HTTPException, Header, Depends
from bson import ObjectId
from models.pin_models import CreatePinModel, VerifyPinModel, ResetPinModel
from utils.jwt_utils import decode_access_token, create_access_token
import datetime

router = APIRouter()

# ---------------------------
# Auth Helper
# ---------------------------
def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        token = authorization.split(" ")[1]
        return decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# ---------------------------
# Helper to find and update user in correct collection
# ---------------------------
async def find_user_by_phone(phone: str):
    from database import get_database
    db = get_database()

    for role in ["admin", "vendor", "garage", "delivery"]:
        user = await db[f"{role}_users"].find_one({"phone": phone})
        if user:
            return user, role
    return None, None

async def update_pin_by_user_id(user_id: str, new_pin: str):
    from database import get_database
    db = get_database()

    for role in ["admin", "vendor", "garage", "delivery"]:
        result = await db[f"{role}_users"].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"pin": new_pin, "updated_at": datetime.datetime.utcnow()}}
        )
        if result.modified_count > 0:
            return True
    return False

# ---------------------------
# Create or Update PIN
# ---------------------------
@router.post("/user/create-pin")
async def create_or_update_pin(payload: CreatePinModel, user=Depends(get_current_user)):
    if payload.pin != payload.confirm_pin:
        raise HTTPException(status_code=400, detail="PINs do not match")

    success = await update_pin_by_user_id(user.get("user_id"), payload.pin)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to set PIN")

    return {"message": "PIN set successfully"}

# ---------------------------
# Login via PIN
# ---------------------------
@router.post("/user/verify-pin")
async def login_with_pin(payload: VerifyPinModel):
    user, role = await find_user_by_phone(payload.phone)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("pin") != payload.pin:
        raise HTTPException(status_code=401, detail="Invalid PIN")

    token_data = {
        "user_id": str(user["_id"]),
        "phone": user["phone"],
        "role": role
    }

    return {"access_token": create_access_token(token_data)}

# ---------------------------
# Reset PIN via OTP
# ---------------------------
@router.post("/user/reset-pin")
async def reset_pin_after_otp(payload: ResetPinModel):
    if payload.new_pin != payload.confirm_pin:
        raise HTTPException(status_code=400, detail="PINs do not match")

    user, role = await find_user_by_phone(payload.phone)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from database import get_database
    db = get_database()

    await db[f"{role}_users"].update_one(
        {"phone": payload.phone},
        {"$set": {"pin": payload.new_pin, "updated_at": datetime.datetime.utcnow()}}
    )

    return {"message": "PIN reset successfully"}
