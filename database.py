from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

client = None
db = None

async def connect_to_mongo():
    global client, db

    # Force SSL / TLS for production (MongoDB Atlas requires this)
    client = AsyncIOMotorClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=False)
    
    # Pick the database name from the URI or hardcode it
    db = client["qikspare"]

def get_database():
    global db
    if db is None:
        raise Exception("Database not initialized. Call connect_to_mongo() first.")
    return db
