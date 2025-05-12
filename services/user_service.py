from bson import ObjectId
from fastapi import HTTPException
from database import get_database
from models.user import Address
import datetime
import uuid

db = get_database()

# --- Update User Profile ---
async def update_user_profile(user_id: str, payload):
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")

    update_fields = {k: v for k, v in payload.dict().items() if v is not None}
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_fields["updated_at"] = datetime.datetime.utcnow()

    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_fields}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Profile not updated (maybe same data)")

    return {"message": "Profile updated successfully"}

# --- Add Address ---
async def add_user_address(user_id: str, payload):
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")

    new_address = Address(
        address_id=str(uuid.uuid4()),
        tag=payload.tag,
        address_line=payload.address_line,
        city=payload.city,
        state=payload.state,
        pincode=payload.pincode,
        location=payload.location,
        is_default=payload.is_default,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )

    if payload.is_default:
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"addresses.$[].is_default": False}}
        )

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"addresses": new_address.dict()}}
    )

    return {"message": "Address added successfully", "address_id": new_address.address_id}
