import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.app.v1.routers import auth, projects, documents, campaigns, calls, prospects, dashboard
from src.app.common import get_logger,setup_logging
from src.app.database.db import Base, engine
from src.app.common.settings import Settings


# Create all tables
Base.metadata.create_all(bind=engine)

# Create upload directory
os.makedirs(Settings.upload_dir, exist_ok=True)


@asynccontextmanager
async def lifespans(app: FastAPI):
    setup_logging()
    logger = get_logger("app_lifespan")
    logger.info("Starting up the RealEstate Caller API...")
    yield
    logger.info("Shutting down the RealEstate Caller API...")

app = FastAPI(
    title=Settings.app_name,
    description="AI-Powered Real Estate Caller Agent Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

PREFIX = "/api/v1"
app.include_router(auth.router, prefix=PREFIX)
app.include_router(projects.router, prefix=PREFIX)
app.include_router(documents.router, prefix=PREFIX)
app.include_router(campaigns.router, prefix=PREFIX)
app.include_router(prospects.router, prefix=PREFIX)
app.include_router(calls.router, prefix=PREFIX)
app.include_router(dashboard.router, prefix=PREFIX)


@app.get("/")
def root():
    return {"message": "RealEstate Caller API", "docs": "/api/docs"}


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Real Estate Caller Agent API is running"}
