from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from pymongo.collection import ReturnDocument
from bson import ObjectId

from database import get_database
from utils.jwt_utils import decode_access_token
from models.user import (
    create_user_model,
    AdminUser,
    VendorUser,
    GarageUser,
    DeliveryUser,
    AdminUserUpdate,
    VendorUserUpdate,
    GarageUserUpdate,
    DeliveryUserUpdate,
    UserInDB,
)

router = APIRouter()

# --------------------------
# Auth Helper for Admin Only
# --------------------------
def get_admin_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# --------------------------
# Create User (Admin only)
# --------------------------
@router.post("/admin/create-user")
async def create_user(user_data: dict, admin=Depends(get_admin_user)):
    db = get_database()
    try:
        user = create_user_model(user_data)
        role = user.role
        result = db[f"{role}_users"].insert_one(user.dict())
        return {"status": "success", "user_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --------------------------
# Get All Users (Admin only)
# --------------------------
@router.get("/admin/users")
async def get_all_users(admin=Depends(get_admin_user)):
    db = get_database()
    all_users = []
    for role in ["admin", "vendor", "garage", "delivery"]:
        users = list(db[f"{role}_users"].find())
        for user in users:
            user["role"] = role
            user["_id"] = str(user["_id"])
            all_users.append(user)
    return {"count": len(all_users), "data": all_users}


# --------------------------
# Get Single User by ID
# --------------------------
@router.get("/admin/user/{user_id}")
async def get_user_by_id(user_id: str, admin=Depends(get_admin_user)):
    db = get_database()
    for role in ["admin", "vendor", "garage", "delivery"]:
        user = db[f"{role}_users"].find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
            user["role"] = role
            return user
    raise HTTPException(status_code=404, detail="User not found")


# --------------------------
# Update User by ID
# --------------------------
@router.patch("/admin/update-user/{user_id}")
async def update_user_by_id(user_id: str, payload: dict, admin=Depends(get_admin_user)):
    db = get_database()
    for role in ["admin", "vendor", "garage", "delivery"]:
        result = db[f"{role}_users"].find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": payload},
            return_document=ReturnDocument.AFTER
        )
        if result:
            result["_id"] = str(result["_id"])
            result["role"] = role
            return {"status": "updated", "data": result}
    raise HTTPException(status_code=404, detail="User not found")


# --------------------------
# Delete User by ID
# --------------------------
@router.delete("/admin/user/{user_id}")
async def delete_user(user_id: str, admin=Depends(get_admin_user)):
    db = get_database()
    for role in ["admin", "vendor", "garage", "delivery"]:
        deleted = db[f"{role}_users"].delete_one({"_id": ObjectId(user_id)})
        if deleted.deleted_count > 0:
            return {"status": "deleted", "user_id": user_id, "role": role}
    raise HTTPException(status_code=404, detail="User not found")
