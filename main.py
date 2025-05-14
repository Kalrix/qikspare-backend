from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import connect_to_mongo
from routes import auth, admin, invoice, user

app = FastAPI()

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

# Mount Routes
app.include_router(auth.router, prefix="/api/auth")       # Auth, OTP, register
app.include_router(admin.router, prefix="/api")           # Admin: /api/admin/users
app.include_router(invoice.router, prefix="/api/invoices")
app.include_router(user.router, prefix="/api/user")
