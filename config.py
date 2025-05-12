import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretjwtkey")
JWT_ALGORITHM = "HS256"
