from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import connect_to_mongo
from routes import auth, admin, invoice  # ✅ Route imports

app = FastAPI()

# ✅ Connect to MongoDB on app startup
app.add_event_handler("startup", connect_to_mongo)

# ✅ Allowed frontend origins — production + local (optional)
origins = [
    "https://qikspare-admin.onrender.com",  # ✅ Production frontend
    "http://localhost:3000",                # Optional: local dev frontend
]

# ✅ CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # ⚠️ Don't use ["*"] when credentials=True
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register all routes
app.include_router(auth.router, prefix="/api/auth")
app.include_router(admin.router, prefix="/api")
app.include_router(invoice.router, prefix="/api/invoices")
