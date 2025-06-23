import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import io
import time
import re
import json

load_dotenv()

def setup_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("ERROR: Please set your Gemini API key in a .env file.")
    try:
        genai.configure(api_key=api_key)
        model_name = 'gemini-1.5-flash'
        model = genai.GenerativeModel(model_name)
        return model, model_name
    except Exception as e:
        print(f"Error setting up Gemini: {str(e)}")
        raise

def classify_and_locate_objects(model: genai.GenerativeModel, image_bytes: bytes):
    """
    Detects all waste objects in an image, classifies them, and returns their coordinates.
    """
    pil_img = Image.open(io.BytesIO(image_bytes))
    
    prompt = """
    Analyze the provided image of a scene. Identify every piece of waste.
    For each piece of waste, provide its classification and its center coordinates.
    The categories are:
    - paper
    - plastic
    - glass
    - metal
    - E-waste
    - organic
    - other

    Return the data as a single, clean JSON object. The object should contain a single key "objects_found" which is a list of all detected items.
    Each item in the list should be an object with three keys: "label" (the category), "x" (the horizontal coordinate of the center), and "y" (the vertical coordinate of the center).
    Example response for an image with two items:
    {
      "objects_found": [
        { "label": "paper", "x": 120, "y": 450 },
        { "label": "plastic", "x": 350, "y": 200 }
      ]
    }
    If no waste is found, return an empty list:
    {
      "objects_found": []
    }
    """
    
    try:
        start_time = time.time()
        response = model.generate_content([prompt, pil_img])
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Use regex to find the JSON block, even with markdown backticks
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        
        if json_match:
            json_string = json_match.group(0)
            # The entire JSON object is the result
            classification_data = json.loads(json_string)
        else:
            # Fallback if no JSON is found
            classification_data = {"objects_found": [], "error": "No valid JSON found in model response"}

        return {
            "result": classification_data,
            "response_time": f"{response_time:.2f}s"
        }
        
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error during classification or parsing: {str(e)}")
        # Return the raw text on failure for debugging
        return {
            "result": {"objects_found": [], "error": f"parsing_error: {response.text.strip()}"},
            "response_time": f"{time.time() - start_time:.2f}s"
        } 