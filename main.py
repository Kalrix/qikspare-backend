from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import connect_to_mongo
from routes import auth, admin, invoice  # ✅ Route imports

app = FastAPI()

# ✅ Connect to MongoDB on startup
app.add_event_handler("startup", connect_to_mongo)

# ✅ Allowed frontend domains — replace/add your actual frontend URL
origins = [
    "https://qikspare-admin.vercel.app",  # Production frontend domain
    "http://localhost:3000",              # Local development
]

# ✅ CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Route registrations
app.include_router(auth.router, prefix="/api/auth")         # for /api/auth/*
app.include_router(admin.router, prefix="/api")             # for /api/admin/*
app.include_router(invoice.router, prefix="/api/invoices")  # for /api/invoices/*
