import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import io
import time
import re
import json
from itertools import cycle

load_dotenv()

def load_api_keys():
    """Loads all GEMINI_API_KEY_... from the environment and returns them as a list."""
    keys = []
    i = 1
    while True:
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            keys.append(key)
            i += 1
        else:
            break
    if not keys:
        raise ValueError("ERROR: No GEMINI_API_KEY_... found in .env file.")
    return keys

def setup_gemini(api_keys):
    """Initializes a list of Gemini models, one for each API key."""
    models = []
    for key in api_keys:
        genai.configure(api_key=key, transport='rest')
        # Using the "-latest" alias is more robust.
        model_name = 'gemini-1.5-pro-latest'
        model = genai.GenerativeModel(model_name)
        models.append(model)
    
    if not models:
        raise ValueError("Could not initialize any Gemini models.")

    model_name = 'gemini-1.5-pro-latest' # We assume all models are the same type
    return models, model_name

def classify_and_locate_objects(model: genai.GenerativeModel, image_bytes: bytes):
    """
    Detects all waste objects in an image, classifies them, and returns their coordinates.
    """
    pil_img = Image.open(io.BytesIO(image_bytes))
    
    prompt = """
    You are an expert system for a recycling robot. Your task is to analyze the image and identify all pieces of waste.

    Follow these steps precisely:
    1.  **Identify Distinct 3D Objects:** Look for tangible, physical objects. You MUST IGNORE the flat surface they are resting on (e.g., paper, table, ground).
    2.  **Classify Each Object:** Assign each object to one of the following categories:
        *   `paper`: Paper, cardboard, newspapers.
        *   `plastic`: Bottles, containers, bags, plastic items like markers.
        *   `glass`: Glass bottles, jars.
        *   `metal`: Cans, foil.
        *   `E-waste`: Electronic waste. Anything with circuits, batteries, screens, or wires. Examples: remote controls, phones, keyboards, cables.
        *   `organic`: Food scraps like fruit peels.
        *   `other`: Waste that does not fit into the other categories.
    3.  **Find Bounding Box:** For each object, determine the bounding box that encloses it. The box should be represented by four coordinates: [x_min, y_min, x_max, y_max].
    4.  **Format the Output:** Return the data as a single, clean JSON object with no other text, comments, or markdown formatting.

    **JSON Output Format:**
    The JSON object must contain a key "objects_found" which is a list. Each item in the list represents one object and must have two keys: "label" and "box".

    **Example:**
    {
      "objects_found": [
        { "label": "E-waste", "box": [290, 230, 400, 280] },
        { "label": "plastic", "box": [480, 240, 650, 290] }
      ]
    }

    If no waste is found, return the list as empty: `{"objects_found": []}`.
    
    Now, analyze the provided image.
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