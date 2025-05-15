from fastapi import APIRouter, Depends, HTTPException, Header
from bson import ObjectId
from typing import Optional
from database import get_database
from utils.jwt_utils import decode_access_token
from models.user import UserUpdateModel

router = APIRouter()
db = get_database()

def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        token = authorization.split(" ")[1]
        return decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.patch("/update-profile")
async def update_profile(payload: UserUpdateModel, user=Depends(get_current_user)):
    user_id = user.get("user_id")
    role = user.get("role")

    update_data = {k: v for k, v in payload.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    result = await db[f"{role}_users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="No changes made")

    return {"message": "Profile updated successfully"}
