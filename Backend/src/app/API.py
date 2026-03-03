from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.v1.routers import auth, profile, projects, campaigns
from src.app.database.db import PostgreSQLDB
from src.app.common import get_logger

logger = get_logger("API")

app = FastAPI(
    title="Real Estate Caller Agent API",
    description="Backend API for managing AI Caller Agent operations for Real Estate Developer",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    logger.info("Starting up FastAPI application...")
    try:
        PostgreSQLDB.create_tables_once()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(projects.router)
app.include_router(campaigns.router)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Real Estate Caller Agent API is running"}
