from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import connect_to_mongo

from routes import (
    auth,
    admin,
    invoice,
    pin_routes,
    user_routes
)

app = FastAPI(
    title="QikSpare API",
    version="1.0.0",
    description="Backend for QikSpare Garage App & Admin Dashboard",
)

@app.on_event("startup")
async def startup_db():
    await connect_to_mongo()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth & OTP"])
app.include_router(admin.router, prefix="/api", tags=["Admin APIs"])
app.include_router(invoice.router, prefix="/api/invoices", tags=["Invoices"])
app.include_router(pin_routes.router, prefix="/api", tags=["PIN System"])
app.include_router(user_routes.router, prefix="/api/user", tags=["User Profile & Address"])
