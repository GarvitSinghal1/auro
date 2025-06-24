from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from PIL import Image
import io
import os
from dotenv import load_dotenv
# import google.generativeai as genai (No longer needed here)
from contextlib import asynccontextmanager
from . import classifier
import uvicorn
import time

# Load environment variables at the very top to ensure they are available for all modules.
load_dotenv()

# Load all credentials on startup
CLARIFAI_API_KEY = os.getenv("CLARIFAI_API_KEY")# CLARIFAI_USER_ID = os.getenv("CLARIFAI_USER_ID") # No longer needed
# CLARIFAI_APP_ID = os.getenv("CLARIFAI_APP_ID")   # No longer needed

# --- Pydantic Models for Documentation ---
# These models define the structure of the API response for the auto-generated docs.

class TrashItem(BaseModel):
    category: str
    bounding_box: List[float]

class DebugInfo(BaseModel):
    confidence_threshold: float
    clarifai_detections: List[Dict[str, Any]]
    final_classifications: List[Dict[str, Any]]

class ClassificationResponse(BaseModel):
    api_version: str
    model_used: str
    response_time: str
    trash_items: List[TrashItem]
    debug_info: DebugInfo

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Load Gemini Keys ---
    gemini_keys = []
    key1 = os.getenv("GEMINI_API_KEY")
    if key1:
        gemini_keys.append(key1)
    
    i = 2
    while True:
        key = os.getenv(f"GEMINI_API_KEY_{i}") or os.getenv(f"GEMINI_API_KEY{i}")
        if key:
            gemini_keys.append(key)
            i += 1
        else:
            break
            
    app.state.gemini_keys = gemini_keys
    app.state.current_key_index = 0

    # --- Log Status of All Credentials ---
    if not CLARIFAI_API_KEY:
        print("Warning: CLARIFAI_API_KEY not found.")
    else:
        print("Clarifai credentials loaded successfully.")

    if not app.state.gemini_keys:
        print("Warning: No Gemini API keys found.")
    else:
        print(f"Successfully loaded {len(app.state.gemini_keys)} Gemini API keys.")

    yield
    print("Shutting down.")

app = FastAPI(
    title="AURo API",
    description="AI-powered waste classification for the Autonomous Urban Recycler.",
    version="1.7.2", # Added response models for documentation
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the AURo API!",
        "version": app.version,
        "docs_url": "/docs"
    }

@app.post("/classify/", response_model=ClassificationResponse)
async def classify_image_endpoint(file: UploadFile = File(...)):
    """
    Receives an image file, analyzes it to find and classify waste, and returns the results.

    This endpoint orchestrates a powerful two-stage AI process:
    1.  **Detection:** Uses the Clarifai General Detection model to identify the location of all potential objects in the image.
    2.  **Analysis:** For each high-confidence detection, it crops the object and uses the Gemini Vision model to perform a detailed material analysis.

    The response includes a list of classified trash items and detailed debug information about the process.
    """
    if not CLARIFAI_API_KEY or not app.state.gemini_keys:
        raise HTTPException(status_code=500, detail="API credentials are not fully configured on the server.")

    try:
        # Get the next Gemini API key for this request
        key_index = app.state.current_key_index
        gemini_key = app.state.gemini_keys[key_index]
        
        # Rotate key index for the NEXT request
        app.state.current_key_index = (key_index + 1) % len(app.state.gemini_keys)
        
        contents = await file.read()
        pil_image = Image.open(io.BytesIO(contents))
        
        start_time = time.time()
        result = classifier.classify_image(
            pil_image, 
            clarifai_pat=CLARIFAI_API_KEY, 
            gemini_api_key=gemini_key
        )
        end_time = time.time()
        response_time = end_time - start_time

        if "error" in result:
            raise HTTPException(status_code=500, detail=f"AI model error: {result['error']}")

        # The classifier now returns both trash_items and debug_info
        trash_items = result.get("trash_items", [])
        debug_info = result.get("debug_info", {})

        return {
            "api_version": app.version,
            "model_used": "clarifai-detection + gemini-vision",
            "response_time": f"{response_time:.2f}s",
            "trash_items": trash_items,
            "debug_info": debug_info
        }

    except Exception as e:
        print(f"Error during classification: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True) 