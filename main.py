from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import connect_to_mongo
from routes import auth, admin, invoice, user

app = FastAPI()

# ✅ Connect to MongoDB on startup (correct async usage)
@app.on_event("startup")
async def startup_db():
    await connect_to_mongo()

# ✅ CORS Configuration (safe for mobile, Expo, web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # ✅ Allow all origins (adjust to specific domains in prod)
    allow_credentials=False,      # ⚠️ Must be False when using "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Mount API Routes
app.include_router(auth.router, prefix="/api/auth")       # For login, OTP, register
app.include_router(admin.router, prefix="/api")     # Admin APIs
app.include_router(invoice.router, prefix="/api/invoices")# Invoice APIs
app.include_router(user.router, prefix="/api/user")       # Profile, address management

