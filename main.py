import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from dotenv import load_dotenv

from .database import engine, init_db
from .routes import router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler to ensure database schema is created on startup."""
    try:
        init_db()
        print("Database schema successfully verified and initialized in MySQL (scamlens_db).")
    except Exception as e:
        print(f"Warning: Failed to initialize database schema: {e}")
    yield


app = FastAPI(
    title="SCAMLENS AI API",
    description="AI-powered Scam Detection Platform Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
origins = [
    FRONTEND_ORIGIN,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health_check():
    """Health check endpoint providing API and MySQL status."""
    db_status = "unhealthy"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "online",
        "service": "SCAMLENS AI Backend",
        "version": "1.0.0",
        "database": db_status
    }


@app.get("/", tags=["system"])
def root():
    return {
        "message": "SCAMLENS AI API is active. See the scam before you click.",
        "documentation": "/docs",
        "health": "/health"
    }


# Include v1 endpoints
app.include_router(router)
