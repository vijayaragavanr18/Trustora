"""
FastAPI Application for Deepfake Detection and Trusted Capture
"""
import asyncio
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from pathlib import Path
import shutil

from deepfake_detector import get_detector
from blockchain.trusted_capture import get_trusted_capture
from config import APIConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Deepfake Detection & Trusted Capture API",
    description="AI/ML-powered deepfake detection with blockchain verification",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
detector = get_detector()
trusted_capture = get_trusted_capture()

# Ensure upload directory exists
APIConfig.TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    success: bool
    file_type: str
    results: dict
    error: Optional[str] = None


class TrustedCaptureRequest(BaseModel):
    """Request model for trusted capture"""
    user_id: str
    device_info: Optional[dict] = None
    location: Optional[dict] = None


@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    logger.info("Starting Deepfake Detection API...")
    logger.info("Loading AI/ML models...")
    await detector.load_models()
    logger.info("Models loaded successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Deepfake Detection & Trusted Capture API",
        "version": "1.0.0",
        "endpoints": {
            "analyze_image": "/api/analyze/image",
            "analyze_video": "/api/analyze/video",
            "analyze_audio": "/api/analyze/audio",
            "create_trusted_capture": "/api/trusted-capture/create",
            "verify_trusted_capture": "/api/trusted-capture/verify",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": detector._models_loaded,
        "blockchain_initialized": trusted_capture.blockchain._initialized
    }


@app.post("/api/analyze/image", response_model=AnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze an image for deepfake artifacts
    
    Args:
        file: Image file to analyze
        
    Returns:
        Analysis results with deepfake score and details
    """
    try:
        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in APIConfig.ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {APIConfig.ALLOWED_IMAGE_EXTENSIONS}"
            )
        
        # Save uploaded file temporarily
        temp_file_path = APIConfig.TEMP_UPLOAD_DIR / f"temp_{file.filename}"
        
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Check file size
        if temp_file_path.stat().st_size > APIConfig.MAX_FILE_SIZE_BYTES:
            temp_file_path.unlink()
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {APIConfig.MAX_FILE_SIZE_MB}MB"
            )
        
        logger.info(f"Analyzing image: {file.filename}")
        
        # Analyze image
        results = await detector.analyze_image(str(temp_file_path))
        
        # Clean up
        temp_file_path.unlink()
        
        return AnalysisResponse(
            success=True,
            file_type="image",
            results=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze/video", response_model=AnalysisResponse)
async def analyze_video(file: UploadFile = File(...)):
    """
    Analyze a video for deepfake artifacts
    
    Args:
        file: Video file to analyze
        
    Returns:
        Analysis results with deepfake score and details
    """
    try:
        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in APIConfig.ALLOWED_VIDEO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {APIConfig.ALLOWED_VIDEO_EXTENSIONS}"
            )
        
        # Save uploaded file temporarily
        temp_file_path = APIConfig.TEMP_UPLOAD_DIR / f"temp_{file.filename}"
        
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Check file size
        if temp_file_path.stat().st_size > APIConfig.MAX_FILE_SIZE_BYTES:
            temp_file_path.unlink()
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {APIConfig.MAX_FILE_SIZE_MB}MB"
            )
        
        logger.info(f"Analyzing video: {file.filename}")
        
        # Analyze video (this might take a while)
        results = await detector.analyze_video(str(temp_file_path))
        
        # Clean up
        temp_file_path.unlink()
        
        return AnalysisResponse(
            success=True,
            file_type="video",
            results=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing video: {str(e)}")
        # Clean up on error
        if temp_file_path.exists():
            temp_file_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze/audio", response_model=AnalysisResponse)
async def analyze_audio(file: UploadFile = File(...)):
    """
    Analyze audio for synthesis artifacts
    
    Args:
        file: Audio file to analyze
        
    Returns:
        Analysis results with synthesis detection score
    """
    try:
        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in APIConfig.ALLOWED_AUDIO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {APIConfig.ALLOWED_AUDIO_EXTENSIONS}"
            )
        
        # Save uploaded file temporarily
        temp_file_path = APIConfig.TEMP_UPLOAD_DIR / f"temp_{file.filename}"
        
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Check file size
        if temp_file_path.stat().st_size > APIConfig.MAX_FILE_SIZE_BYTES:
            temp_file_path.unlink()
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {APIConfig.MAX_FILE_SIZE_MB}MB"
            )
        
        logger.info(f"Analyzing audio: {file.filename}")
        
        # Analyze audio
        results = await detector.analyze_audio(str(temp_file_path))
        
        # Clean up
        temp_file_path.unlink()
        
        return AnalysisResponse(
            success=True,
            file_type="audio",
            results=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/trusted-capture/create")
async def create_trusted_capture_endpoint(
    file: UploadFile = File(...),
    user_id: str = "anonymous"
):
    """
    Create a trusted capture with blockchain timestamp
    
    Args:
        file: Media file to timestamp
        user_id: ID of the user creating the capture
        
    Returns:
        Capture information including blockchain hash
    """
    try:
        # Save uploaded file
        temp_file_path = APIConfig.TEMP_UPLOAD_DIR / f"capture_{file.filename}"
        
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Creating trusted capture for: {file.filename}")
        
        # Create trusted capture
        result = await trusted_capture.create_trusted_capture(
            file_path=str(temp_file_path),
            user_id=user_id
        )
        
        # Keep file for now (in production, move to permanent storage)
        # temp_file_path.unlink()
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating trusted capture: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/trusted-capture/verify")
async def verify_trusted_capture_endpoint(
    file: UploadFile = File(...),
    capture_id: Optional[str] = None
):
    """
    Verify if a file has a valid trusted capture timestamp
    
    Args:
        file: Media file to verify
        capture_id: Optional capture ID
        
    Returns:
        Verification results
    """
    try:
        # Save uploaded file temporarily
        temp_file_path = APIConfig.TEMP_UPLOAD_DIR / f"verify_{file.filename}"
        
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Verifying trusted capture for: {file.filename}")
        
        # Verify
        result = await trusted_capture.verify_trusted_capture(
            file_path=str(temp_file_path),
            capture_id=capture_id
        )
        
        # Clean up
        temp_file_path.unlink()
        
        return result
        
    except Exception as e:
        logger.error(f"Error verifying trusted capture: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/blockchain/info")
async def get_blockchain_info():
    """Get blockchain network information"""
    try:
        info = trusted_capture.blockchain.get_network_info()
        return info
    except Exception as e:
        logger.error(f"Error getting blockchain info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "api:app",
        host=APIConfig.HOST,
        port=APIConfig.PORT,
        reload=True,
        log_level="info"
    )
