from database import get_database

async def generate_id(key: str, prefix: str):
    db = get_database()
    counters = db["counters"]
    result = await counters.find_one_and_update(
        {"_id": key},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    seq = result["seq"]
    return f"{prefix}-{str(seq).zfill(5)}"
