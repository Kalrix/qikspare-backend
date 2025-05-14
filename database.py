from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

client = None
db = None

async def connect_to_mongo():
    global client, db

    client = AsyncIOMotorClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=False  # Set True only if using self-signed certs
    )
    db = client.get_default_database() or client["qikspare"]  # fallback if URI doesn’t include DB

def get_database():
    global db
    if db is None:
        raise Exception("Database not initialized. Call connect_to_mongo() first.")
    return db
