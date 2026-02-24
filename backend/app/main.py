from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.api import auth, upload, analysis, history, capture, reports
from app.database import engine, Base, check_and_fix_columns
import os, logging
from fastapi.responses import JSONResponse
from starlette.requests import Request

# Configure logging to file
logging.basicConfig(
    filename="server_error.log",
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create all tables (Initial)
Base.metadata.create_all(bind=engine)
# Self-healing: Check for missing columns
try:
    check_and_fix_columns()
except Exception as e:
    print(f"--- DB WARNING: Column fix failed: {e} ---")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    debug=True # Keep true for development
)

# CREATE UPLOAD DIR IF MISSING
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    print(f"--- FOLDER: Created {settings.UPLOAD_DIR} ---")

# CORS - Allow frontend to connect
# CORS configuration
# In production, change this to your actual frontend URL (e.g., https://trustora.vercel.app)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True if allowed_origins[0] != "*" else False,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("--- CORS initialized for all origins ---")

# GLOBAL ERROR HANDLER - This prevents "Network Error" by never letting the app Die
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Global Error at {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. The team has been notified.",
            "type": type(exc).__name__,
            "msg": str(exc)
        }
    )

@app.on_event("startup")
async def startup_event():
    print("--- APP STARTUP: Pre-loading Forensic Models (Training Ready) ---")
    try:
        from app.ml.hf_detector import get_hf_pipeline, get_hf_audio_pipeline
        import asyncio
        loop = asyncio.get_event_loop()
        # Run loading in background thread to not block the event loop
        await loop.run_in_executor(None, get_hf_pipeline)
        await loop.run_in_executor(None, get_hf_audio_pipeline)
        print("✅ APP STARTUP: All Models Optimized & Loaded.")
    except Exception as e:
        print(f"❌ APP STARTUP ERROR: Model pre-load failed: {e}")

# Static files for uploads
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ALL API ROUTERS
app.include_router(auth.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(capture.router, prefix="/api")
app.include_router(reports.router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Trustora API - Running!",
        "version": settings.API_VERSION,
        "status": "running",
        "docs": "http://localhost:8000/docs",
        "endpoints": {
            "auth": {
                "register": "POST /api/auth/register",
                "login": "POST /api/auth/login",
                "logout": "POST /api/auth/logout",
                "me": "GET /api/auth/me",
                "refresh": "POST /api/auth/refresh"
            },
            "upload": {
                "image": "POST /api/upload/image",
                "video": "POST /api/upload/video",
                "audio": "POST /api/upload/audio",
                "status": "GET /api/upload/status/{id}"
            },
            "analysis": {
                "start": "POST /api/analyze/start/{scan_id}",
                "status": "GET /api/analyze/status/{job_id}",
                "result": "GET /api/analyze/result/{job_id}",
                "batch": "POST /api/analyze/batch"
            },
            "history": {
                "list": "GET /api/history",
                "detail": "GET /api/history/{scan_id}",
                "delete": "DELETE /api/history/{scan_id}"
            },
            "capture": {
                "start": "POST /api/capture/start",
                "seal": "POST /api/capture/seal",
                "verify": "GET /api/capture/verify/{capture_id}"
            },
            "reports": {
                "json": "GET /api/report/{scan_id}/json",
                "pdf": "GET /api/report/{scan_id}/pdf"
            }
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy", "version": settings.API_VERSION}

@app.get("/api/debug/env")
def debug_env():
    import sys
    try:
        import torch
        torch_status = f"Found: {torch.__version__}"
    except Exception as e:
        torch_status = f"Error: {e}"
    
    return {
        "python": sys.executable,
        "torch": torch_status,
        "env": {k: v for k, v in os.environ.items() if "TORCH" in k or "TRANSFORMERS" in k}
    }
