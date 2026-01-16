from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from config import settings
from models.database import init_db
from routes import auth_router, chat_router, admin_router, company_router, resource_router
from websocket import client_router, admin_router as ws_admin_router
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Application shutting down")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include REST API routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(admin_router)
app.include_router(company_router)
app.include_router(resource_router)

# Include WebSocket routers
app.include_router(client_router)
app.include_router(ws_admin_router)

# Serve static files (frontend)
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
async def root():
    """Root endpoint - serve demo page."""
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/admin")
async def admin_page():
    """Serve admin dashboard."""
    admin_path = os.path.join(os.path.dirname(__file__), "frontend", "admin.html")
    if os.path.exists(admin_path):
        return FileResponse(admin_path)
    return {"error": "Admin page not found"}


@app.get("/chatbot-widget.js")
async def widget_script():
    """Serve chatbot widget script."""
    widget_path = os.path.join(os.path.dirname(__file__), "frontend", "chatbot-widget.js")
    if os.path.exists(widget_path):
        return FileResponse(widget_path, media_type="application/javascript")
    return {"error": "Widget not found"}


@app.get("/styles.css")
async def styles():
    """Serve styles."""
    styles_path = os.path.join(os.path.dirname(__file__), "frontend", "styles.css")
    if os.path.exists(styles_path):
        return FileResponse(styles_path, media_type="text/css")
    return {"error": "Styles not found"}


@app.get("/admin-styles.css")
async def admin_styles():
    """Serve admin styles."""
    styles_path = os.path.join(os.path.dirname(__file__), "frontend", "admin-styles.css")
    if os.path.exists(styles_path):
        return FileResponse(styles_path, media_type="text/css")
    return {"error": "Admin styles not found"}


@app.get("/admin.js")
async def admin_js():
    """Serve admin JavaScript."""
    js_path = os.path.join(os.path.dirname(__file__), "frontend", "admin.js")
    if os.path.exists(js_path):
        return FileResponse(js_path, media_type="application/javascript")
    return {"error": "Admin JS not found"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/register")
async def company_register_page():
    """Serve company registration page."""
    register_path = os.path.join(os.path.dirname(__file__), "frontend", "company-register.html")
    if os.path.exists(register_path):
        return FileResponse(register_path)
    return {"error": "Registration page not found"}


@app.get("/company-register.css")
async def company_register_css():
    """Serve company registration styles."""
    css_path = os.path.join(os.path.dirname(__file__), "frontend", "company-register.css")
    if os.path.exists(css_path):
        return FileResponse(css_path, media_type="text/css")
    return {"error": "CSS not found"}


@app.get("/company-register.js")
async def company_register_js():
    """Serve company registration JavaScript."""
    js_path = os.path.join(os.path.dirname(__file__), "frontend", "company-register.js")
    if os.path.exists(js_path):
        return FileResponse(js_path, media_type="application/javascript")
    return {"error": "JS not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
