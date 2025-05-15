from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import connect_to_mongo

# Route modules
from routes import (
    auth,
    admin,
    invoice,
    pin_routes,
    user_routes,
    user_routes as user_crud_routes  # reuse user_routes for admin CRUD
)

app = FastAPI(
    title="QikSpare API",
    version="1.0.0",
    description="Backend for QikSpare Garage App & Admin Dashboard",
)

# --------------------------
# Startup MongoDB Connection
# --------------------------
@app.on_event("startup")
async def startup_db():
    await connect_to_mongo()

# --------------------------
# CORS Setup (Open for dev)
# --------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔐 In production, use allow_origins=["https://qikspare.in"]
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# API Routes
# --------------------------
app.include_router(auth.router, prefix="/api/auth", tags=["Auth & OTP"])
app.include_router(admin.router, prefix="/api", tags=["Admin APIs"])
app.include_router(invoice.router, prefix="/api/invoices", tags=["Invoices"])
app.include_router(pin_routes.router, prefix="/api", tags=["PIN System"])
app.include_router(user_routes.router, prefix="/api/user", tags=["User Profile & Address"])
app.include_router(user_crud_routes.router, prefix="/api", tags=["User Management"])  # Admin CRUD for all users
