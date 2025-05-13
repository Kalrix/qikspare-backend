import os
from dotenv import load_dotenv

load_dotenv()  # Load .env only for local development

# Render will use environment variables set via the dashboard
MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretjwtkey")
JWT_ALGORITHM = "HS256"
