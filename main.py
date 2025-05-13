from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import connect_to_mongo
from routes import auth, admin, invoice  # ✅ Route imports

app = FastAPI()

# ✅ Connect to MongoDB on app startup
app.add_event_handler("startup", connect_to_mongo)

# ✅ CORS setup
# Use "*" for mobile app compatibility (e.g. APK, Expo)
# Note: allow_credentials must be False when using "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],             # ✅ TEMP: Allow all origins (suitable for mobile app builds)
    allow_credentials=False,         # ⚠️ Must be False with "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register API routes
app.include_router(auth.router, prefix="/api/auth")
app.include_router(admin.router, prefix="/api")
app.include_router(invoice.router, prefix="/api/invoices")
