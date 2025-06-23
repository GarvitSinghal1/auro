from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
from . import classifier
from itertools import cycle

# --- API Version ---
API_VERSION = "1.4.0"

# Lifespan context manager to handle startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the model during startup
    try:
        api_keys = classifier.load_api_keys()
        models, model_name = classifier.setup_gemini(api_keys)
        # Create a cycle iterator to rotate through models
        app.state.model_cycler = cycle(models)
        app.state.model_name = model_name
        print(f"INFO:     Successfully loaded {len(models)} Gemini models.")
    except ValueError as e:
        print(f"ERROR:    {e}")
        app.state.model_cycler = None
        app.state.model_name = "N/A"
    yield
    # Clean up resources on shutdown (if any)
    print("INFO:     Shutting down.")


app = FastAPI(
    title="AURo Waste Classifier API",
    description="API for classifying waste items for the Autonomous Urban Recycler.",
    version=API_VERSION,
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": f"Welcome to the AURo Waste Classifier API! Version: {API_VERSION}"}

@app.post("/classify/")
async def classify_waste(file: UploadFile = File(...)):
    if app.state.model_cycler is None:
        raise HTTPException(status_code=500, detail="Gemini models not available. Check server logs for API key issues.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="No image file uploaded.")

    try:
        # Get the next model from our rotating cycle
        current_model = next(app.state.model_cycler)

        # This now returns a dictionary with 'result' and 'response_time'
        result_dict = classifier.classify_and_locate_objects(current_model, contents)

        # The main result is now nested in the 'result' key
        classification_result = result_dict.get("result", {})
        
        if "error" in classification_result:
             # Pass along any errors from the classifier
             raise HTTPException(status_code=500, detail=classification_result["error"])
        
        # Add the model_used and response_time to the final response
        final_response = {
            "api_version": API_VERSION,
            "model_used": app.state.model_name,
            "response_time": result_dict.get("response_time", "N/A"),
            **classification_result  # Unpack "objects_found"
        }
        return JSONResponse(content=final_response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during classification: {str(e)}")

if __name__ == "__main__":
    # The "api.main:app" string tells Uvicorn where to find the app object
    # when using the reloader.
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True) 