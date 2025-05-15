from fastapi import APIRouter, HTTPException, Header, Depends
from database import get_database
from bson import ObjectId
from models.pin_models import CreatePinModel, VerifyPinModel, ResetPinModel
from utils.jwt_utils import decode_access_token
import datetime

router = APIRouter()

# --- Auth helper ---
def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = authorization.split(" ")[1]
    return decode_access_token(token)

# --- Create/Update PIN ---
@router.post("/user/create-pin")
async def create_pin(payload: CreatePinModel, user=Depends(get_current_user)):
    if payload.pin != payload.confirm_pin:
        raise HTTPException(status_code=400, detail="PINs do not match")

    db = get_database()
    user_id = user.get("user_id")

    await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"pin": payload.pin, "updated_at": datetime.datetime.utcnow()}}
    )

    return {"message": "PIN set successfully"}

# --- Verify PIN (Login using PIN) ---
@router.post("/user/verify-pin")
async def verify_pin(payload: VerifyPinModel):
    db = get_database()

    user = await db["users"].find_one({"phone": payload.phone})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("pin") != payload.pin:
        raise HTTPException(status_code=401, detail="Invalid PIN")

    from utils.jwt_utils import create_access_token
    token_data = {
        "user_id": str(user["_id"]),
        "phone": user["phone"],
        "role": user.get("role", "garage")
    }
    return {"access_token": create_access_token(token_data)}

# --- Reset PIN with OTP ---
@router.post("/user/reset-pin")
async def reset_pin(payload: ResetPinModel):
    if payload.new_pin != payload.confirm_pin:
        raise HTTPException(status_code=400, detail="PINs do not match")

    db = get_database()

    user = await db["users"].find_one({"phone": payload.phone})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Optional: Verify OTP via 2Factor or flag
    # Skipping for now - frontend should verify OTP before calling this.

    await db["users"].update_one(
        {"phone": payload.phone},
        {"$set": {"pin": payload.new_pin, "updated_at": datetime.datetime.utcnow()}}
    )

    return {"message": "PIN reset successfully"}
