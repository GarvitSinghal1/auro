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

def classify_image(model: genai.GenerativeModel, image_bytes: bytes):
    """
    Classifies the object in the image using the Gemini model and measures response time.
    """
    pil_img = Image.open(io.BytesIO(image_bytes))
    
    prompt = """
    Classify the object in this image into one of these categories:
    - paper
    - plastic
    - glass
    - metal
    - nothing
    - E-waste
    - mixed (and the categories of the objects in the image)
    
    Return ONLY the category name as a single-word JSON response, like {"classification": "plastic"}.
    If the background is plain or empty, classify it as "nothing".
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
            # Parse the JSON to extract the actual classification
            classification_data = json.loads(json_string)
            classification_text = classification_data.get("classification", "unknown")
        else:
            # Fallback if no JSON is found
            classification_text = response.text.strip()

        return {
            "classification": classification_text,
            "response_time": f"{response_time:.2f}s"
        }
        
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error during classification or parsing: {str(e)}")
        # Return the raw text on failure for debugging
        return {
            "classification": f"parsing_error: {response.text.strip()}",
            "response_time": f"{time.time() - start_time:.2f}s"
        } 