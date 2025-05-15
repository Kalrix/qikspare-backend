from bson import ObjectId
from pymongo.collection import ReturnDocument
from database import get_database
from models.user import create_user_model

db = get_database()

# --------------------------
# Create User by Role
# --------------------------
async def create_user_service(data: dict):
    user = create_user_model(data)
    role = user.role
    result = db[f"{role}_users"].insert_one(user.dict())
    return str(result.inserted_id)


# --------------------------
# Get All Users (merged from all roles)
# --------------------------
async def get_all_users_service():
    all_users = []
    for role in ["admin", "vendor", "garage", "delivery"]:
        users = list(db[f"{role}_users"].find())
        for user in users:
            user["_id"] = str(user["_id"])
            user["role"] = role
        all_users.extend(users)
    return all_users


# --------------------------
# Get User by ID (across collections)
# --------------------------
async def get_user_by_id_service(user_id: str):
    for role in ["admin", "vendor", "garage", "delivery"]:
        user = db[f"{role}_users"].find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
            user["role"] = role
            return user
    return None


# --------------------------
# Update User by ID
# --------------------------
async def update_user_by_id_service(user_id: str, payload: dict):
    for role in ["admin", "vendor", "garage", "delivery"]:
        updated = db[f"{role}_users"].find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": payload},
            return_document=ReturnDocument.AFTER
        )
        if updated:
            updated["_id"] = str(updated["_id"])
            updated["role"] = role
            return updated
    return None


# --------------------------
# Delete User by ID
# --------------------------
async def delete_user_service(user_id: str):
    for role in ["admin", "vendor", "garage", "delivery"]:
        deleted = db[f"{role}_users"].delete_one({"_id": ObjectId(user_id)})
        if deleted.deleted_count > 0:
            return {"user_id": user_id, "role": role}
    return None
