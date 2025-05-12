from fastapi import APIRouter, Depends, Header, HTTPException
from database import get_database
from utils.jwt_utils import decode_access_token
from bson import ObjectId
from pydantic import BaseModel
from typing import Optional, List
import datetime

router = APIRouter()

# ---------------------------
# Auth Helper for Admin
# ---------------------------
def get_admin_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing auth token")
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access only")
    return payload

# ---------------------------
# Model for Updating / Creating User
# ---------------------------
class AdminUpdateUserModel(BaseModel):
    full_name: Optional[str]
    email: Optional[str]
    business_name: Optional[str]
    garage_name: Optional[str]
    business_type: Optional[str]
    garage_size: Optional[str]
    brands_served: Optional[List[str]]
    vehicle_types: Optional[List[str]]
    distributor_size: Optional[str]
    brands_carried: Optional[List[str]]
    category_focus: Optional[List[str]]
    pan_number: Optional[str]
    gstin: Optional[str]
    location: Optional[dict]
    phone: Optional[str]
    role: Optional[str]

# ---------------------------
# Get All Users (Admin only)
# ---------------------------
@router.get("/admin/users")
async def get_all_users(user=Depends(get_admin_user)):
    db = get_database()
    cursor = db.users.find()
    users = []
    async for u in cursor:
        u["_id"] = str(u["_id"])
        users.append(u)
    return {"users": users}

# ---------------------------
# Update Any User (Admin only)
# ---------------------------
@router.patch("/admin/update-user/{user_id}")
async def update_user_by_admin(user_id: str, payload: AdminUpdateUserModel, user=Depends(get_admin_user)):
    db = get_database()

    update_data = {k: v for k, v in payload.dict().items() if v is not None}
    print(f"🛠️ DEBUG: Payload received for user_id={user_id}: {payload.dict()}")
    print(f"🛠️ DEBUG: Cleaned update data: {update_data}")

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = datetime.datetime.utcnow()

    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="User not updated (maybe same data or invalid ID)")

    return {"message": "User updated successfully"}

# ---------------------------
# Create New User (Admin only)
# ---------------------------
@router.post("/admin/create-user")
async def create_user_by_admin(payload: AdminUpdateUserModel, user=Depends(get_admin_user)):
    db = get_database()

    if not payload.phone or not payload.role:
        raise HTTPException(status_code=400, detail="Phone and Role are required")

    new_user = {k: v for k, v in payload.dict().items() if v is not None}
    new_user["created_at"] = datetime.datetime.utcnow()
    new_user["updated_at"] = datetime.datetime.utcnow()

    if not new_user.get("referral_code") and payload.full_name:
        new_user["referral_code"] = payload.full_name.replace(" ", "").upper()[:6] + "01"

    result = await db.users.insert_one(new_user)
    new_user["_id"] = str(result.inserted_id)

    return {"message": "User created successfully", "user": new_user}

# ---------------------------
# Create User from App (Non-admin)
# ---------------------------
@router.post("/auth/register-user")
async def register_user_from_app(payload: AdminUpdateUserModel, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing auth token")

    token = authorization.split(" ")[1]
    user_payload = decode_access_token(token)

    if user_payload.get("role") == "admin":
        raise HTTPException(status_code=403, detail="Admins should use /admin/create-user")

    db = get_database()

    if not payload.phone or not payload.role:
        raise HTTPException(status_code=400, detail="Phone and Role are required")

    new_user = {k: v for k, v in payload.dict().items() if v is not None}
    new_user["created_at"] = datetime.datetime.utcnow()
    new_user["updated_at"] = datetime.datetime.utcnow()

    if not new_user.get("referral_code") and payload.full_name:
        new_user["referral_code"] = payload.full_name.replace(" ", "").upper()[:6] + "01"

    result = await db.users.insert_one(new_user)
    new_user["_id"] = str(result.inserted_id)

    return {"message": "User registered successfully", "user": new_user}
