from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

client = None
db = None

async def connect_to_mongo():
    global client, db

    client = AsyncIOMotorClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=False)

    # ✅ Always fallback to hardcoded DB name to avoid URI-related errors
    db = client["qikspare"]
    print("✅ MongoDB connected and database 'qikspare' initialized")

def get_database():
    global db
    if db is None:
        raise Exception("Database not initialized. Call connect_to_mongo() first.")
    return db
