from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
from . import classifier

# Lifespan context manager to handle startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the model during startup
    try:
        model, model_name = classifier.setup_gemini()
        app.state.model = model
        app.state.model_name = model_name
        print("INFO:     Gemini model loaded successfully.")
    except ValueError as e:
        print(f"ERROR:    {e}")
        app.state.model = None
        app.state.model_name = "N/A"
    yield
    # Clean up resources on shutdown (if any)
    print("INFO:     Shutting down.")


app = FastAPI(
    title="AURo Waste Classifier API",
    description="API for classifying waste items for the Autonomous Urban Recycler.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Welcome to the AURo Waste Classifier API!"}

@app.post("/classify/")
async def classify_waste(file: UploadFile = File(...)):
    if app.state.model is None:
        raise HTTPException(status_code=500, detail="Gemini model is not available. Check server logs for API key issues.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="No image file uploaded.")

    try:
        # This now returns a dictionary
        result_dict = classifier.classify_image(app.state.model, contents)

        if "error" in result_dict:
             raise HTTPException(status_code=500, detail=result_dict["error"])
        
        # Add the model_used to the response and return
        final_response = {
            "model_used": app.state.model_name,
            **result_dict  # Unpack the classification and response_time
        }
        return JSONResponse(content=final_response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during classification: {str(e)}")

if __name__ == "__main__":
    # The "api.main:app" string tells Uvicorn where to find the app object
    # when using the reloader.
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True) 