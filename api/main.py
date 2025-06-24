from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
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

# Load the keys and IDs once on startup.
CLARIFAI_API_KEY = os.getenv("CLARIFAI_API_KEY")
CLARIFAI_USER_ID = os.getenv("CLARIFAI_USER_ID")
CLARIFAI_APP_ID = os.getenv("CLARIFAI_APP_ID")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This is a good place for startup logic, like logging the key status.
    if not all([CLARIFAI_API_KEY, CLARIFAI_USER_ID, CLARIFAI_APP_ID]):
        print("Fatal: Clarifai credentials not fully configured in .env file. The API will not function.")
    else:
        print("Clarifai credentials loaded successfully.")
    yield
    print("Shutting down.")

app = FastAPI(
    title="AURo API",
    description="AI-powered waste classification for the Autonomous Urban Recycler.",
    version="1.5.2", # Fix: Use correct Clarifai User/App IDs
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the AURo API!",
        "version": app.version,
        "docs_url": "/docs"
    }

@app.post("/classify/")
async def classify_image_endpoint(file: UploadFile = File(...)):
    if not all([CLARIFAI_API_KEY, CLARIFAI_USER_ID, CLARIFAI_APP_ID]):
        raise HTTPException(status_code=500, detail="API credentials are not configured on the server.")

    try:
        contents = await file.read()
        pil_image = Image.open(io.BytesIO(contents))
        
        start_time = time.time()
        # Pass the loaded credentials to the classifier function
        result = classifier.classify_image(
            pil_image, 
            api_key=CLARIFAI_API_KEY, 
            user_id=CLARIFAI_USER_ID, 
            app_id=CLARIFAI_APP_ID
        )
        end_time = time.time()
        response_time = end_time - start_time

        if "error" in result:
            raise HTTPException(status_code=500, detail=f"AI model error: {result['error']} (Raw: {result.get('raw_response', '')})")

        return JSONResponse(content={
            "api_version": app.version,
            "model_used": "clarifai-general-detection",
            "response_time": f"{response_time:.2f}s",
            **result
        })

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during classification: {e}")
        # --- Old: Gemini Quota Handling (Commented Out) ---
        # # When a 429 happens, the exception message is long.
        # if "429" in str(e):
        #      raise HTTPException(status_code=429, detail="Quota exceeded for the current API key. Try again.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True) 