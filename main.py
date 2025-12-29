from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import upload, letters, auth
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from services.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield

# Create Tables (Simple approach for MVP)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Time Capsule API",
    description="Backend for Future Me Clone",
    lifespan=lifespan
)

import os

# CORS Configuration
origins = [
    "http://localhost:5173", # Local Vite
    "http://127.0.0.1:5173",
    os.getenv("FRONTEND_URL", ""), # Production URL
]

# Filter out empty strings if env var is missing
origins = [origin for origin in origins if origin]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins, 
    allow_origin_regex='https?://.*', # Debugging: Allow all HTTP/HTTPS origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(letters.router, prefix="/api", tags=["Letters"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
from routers import users
app.include_router(users.router, prefix="/api/users", tags=["Users"])


@app.get("/")
def read_root():
    return {"message": "Time Capsule API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
# Triggering DB Reload
