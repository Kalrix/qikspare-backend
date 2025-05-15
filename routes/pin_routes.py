from fastapi import APIRouter, HTTPException, Header, Depends
from bson import ObjectId
from database import get_database
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
# Create or Update PIN
# ---------------------------
@router.post("/user/create-pin")
async def create_or_update_pin(payload: CreatePinModel, user=Depends(get_current_user)):
    """
    Create or update a 4-digit login PIN. Requires Authorization header.
    """
    if payload.pin != payload.confirm_pin:
        raise HTTPException(status_code=400, detail="PINs do not match")

    db = get_database()
    user_id = user.get("user_id")

    result = await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "pin": payload.pin,
                "updated_at": datetime.datetime.utcnow()
            }
        }
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Failed to set PIN")

    return {"message": "PIN set successfully"}


# ---------------------------
# Login via PIN
# ---------------------------
@router.post("/user/verify-pin")
async def login_with_pin(payload: VerifyPinModel):
    """
    Login using phone number and 4-digit PIN.
    """
    db = get_database()
    user = await db["users"].find_one({"phone": payload.phone})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("pin") != payload.pin:
        raise HTTPException(status_code=401, detail="Invalid PIN")

    token_data = {
        "user_id": str(user["_id"]),
        "phone": user["phone"],
        "role": user.get("role", "garage")
    }

    return {"access_token": create_access_token(token_data)}


# ---------------------------
# Reset PIN via OTP (Frontend verifies OTP first)
# ---------------------------
@router.post("/user/reset-pin")
async def reset_pin_after_otp(payload: ResetPinModel):
    """
    Reset PIN after successful OTP verification (OTP should be validated on frontend).
    """
    if payload.new_pin != payload.confirm_pin:
        raise HTTPException(status_code=400, detail="PINs do not match")

    db = get_database()
    user = await db["users"].find_one({"phone": payload.phone})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db["users"].update_one(
        {"phone": payload.phone},
        {
            "$set": {
                "pin": payload.new_pin,
                "updated_at": datetime.datetime.utcnow()
            }
        }
    )

    return {"message": "PIN reset successfully"}
