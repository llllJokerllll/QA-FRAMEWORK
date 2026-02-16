from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import asyncio
from typing import Optional
import os

from config import settings
from database import init_db
from api.v1 import router as api_router
from api.v1.health import router as health_router, set_startup_complete
from api.v1.integrations import include_router as include_integrations_router
from core.auth import get_current_user
from core.logging_config import configure_logging, get_logger
from models import User
from integration.qa_framework_client import get_qa_test_suites

# Configure structured logging
log_level = os.getenv("LOG_LEVEL", "INFO")
environment = os.getenv("ENVIRONMENT", "development")
configure_logging(log_level=log_level, environment=environment)
logger = get_logger(__name__)

app = FastAPI(
    title="QA-Framework Dashboard API",
    description="API para la dashboard unificada de QA-FRAMEWORK",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # expose_headers=["Access-Control-Allow-Origin"]
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")

# Include integration router
include_integrations_router(app)


@app.on_event("startup")
async def startup_event():
    """Initialize database and other resources on startup"""
    logger.info("Initializing QA-Framework Dashboard...")
    await init_db()
    set_startup_complete()
    logger.info("QA-Framework Dashboard initialized successfully")


@app.get("/")
async def root():
    return {"message": "QA-Framework Dashboard API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "qa-framework-dashboard-api"}


@app.get("/api/v1/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/api/v1/integration/qa-framework/suites")
async def get_qa_framework_suites(current_user: User = Depends(get_current_user)):
    """Get available test suites from QA-FRAMEWORK"""
    try:
        suites = await get_qa_test_suites()
        return {"suites": suites}
    except Exception as e:
        logger.error(f"Error getting QA-FRAMEWORK suites: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error connecting to QA-FRAMEWORK: {str(e)}"
        )
