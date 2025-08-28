import uvicorn
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

from app.api.routes import api_router
from app.core.config import settings
from app.core.tasks import run_periodic_tasks
from app.core.broadcast import broadcast_new_email
from app.core.ws_clients import company_email_ws_clients

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[DEBUG] Lifespan startup called")
    """
    Lifespan event handler for FastAPI application.
    This replaces the deprecated @app.on_event("startup") and @app.on_event("shutdown").
    """
    # Startup
    try:
        asyncio.create_task(run_periodic_tasks())
        print("[DEBUG] run_periodic_tasks task created")
    except Exception as e:
        print(f"[DEBUG] Failed to create run_periodic_tasks: {e}")
    yield
    print("[DEBUG] Lifespan shutdown called")
    # Shutdown
    # Add any cleanup code here if needed

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI agent service",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded logos
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.websocket("/ws/company/{company_id}/email")
async def company_email_ws(websocket: WebSocket, company_id: int):
    print(f"[DEBUG] WebSocket client connected for company {company_id}")
    await websocket.accept()
    company_id = int(company_id)
    if company_id not in company_email_ws_clients:
        company_email_ws_clients[company_id] = []
    company_email_ws_clients[company_id].append(websocket)
    try:
        while True:
            await asyncio.sleep(10)  # Keep the connection alive
    except WebSocketDisconnect:
        print(f"[DEBUG] WebSocket client disconnected for company {company_id}")
        company_email_ws_clients[company_id].remove(websocket)
        if not company_email_ws_clients[company_id]:
            del company_email_ws_clients[company_id]

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
