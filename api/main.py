from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io
import os
from dotenv import load_dotenv
import google.generativeai as genai
from contextlib import asynccontextmanager
from . import classifier
import uvicorn
import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load environment variables from .env file
    load_dotenv()
    api_keys = []
    # Load primary key
    key1 = os.getenv("GEMINI_API_KEY")
    if key1:
        api_keys.append(key1)
    
    # Load numbered keys (e.g., GEMINI_API_KEY_2, GEMINI_API_KEY_3)
    i = 2
    while True:
        # Standard format GEMINI_API_KEY_NUM
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if not key:
            # Fallback for format GEMINI_API_KEYNUM
            key = os.getenv(f"GEMINI_API_KEY{i}")

        if key:
            api_keys.append(key)
            i += 1
        else:
            break

    app.state.api_keys = api_keys
    app.state.current_key_index = 0
    
    if not app.state.api_keys:
        print("Warning: No API keys found. Please set GEMINI_API_KEY and/or GEMINI_API_KEY_n in your .env file.")
    else:
        print(f"Successfully loaded {len(app.state.api_keys)} API keys.")
        
    yield
    # Clean up resources if needed
    print("Shutting down.")

app = FastAPI(
    title="AURo API",
    description="AI-powered waste classification for the Autonomous Urban Recycler.",
    version="1.4.3", # Version bump for the category fix
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
    if not app.state.api_keys:
        raise HTTPException(status_code=500, detail="API keys not configured on the server.")

    try:
        # Get the next API key
        key_index = app.state.current_key_index
        api_key = app.state.api_keys[key_index]
        
        # Configure the genai client with the current key FOR THIS REQUEST
        genai.configure(api_key=api_key)

        # Rotate key index for the NEXT request
        app.state.current_key_index = (key_index + 1) % len(app.state.api_keys)
        print(f"Using API key index: {key_index}")

        contents = await file.read()
        pil_image = Image.open(io.BytesIO(contents))
        
        # Time the classifier call
        start_time = time.time()
        result = classifier.classify_image(pil_image)
        end_time = time.time()
        response_time = end_time - start_time

        # Check if the classifier returned an error
        if "error" in result:
            raise HTTPException(status_code=500, detail=f"AI model error: {result['error']} (Raw: {result.get('raw_response', '')})")

        return JSONResponse(content={
            "api_version": app.version,
            "model_used": "gemini-2.0-flash",
            "response_time": f"{response_time:.2f}s",
            **result
        })

    except HTTPException:
        # Re-raise HTTPException to avoid being caught by the generic Exception handler
        raise
    except Exception as e:
        # Catch-all for other errors (e.g., image parsing)
        print(f"Error during classification: {e}")
        # When a 429 happens, the exception message is long.
        if "429" in str(e):
             raise HTTPException(status_code=429, detail="Quota exceeded for the current API key. Try again.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True) 