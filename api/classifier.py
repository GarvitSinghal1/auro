import os
import json
from PIL import Image
import io

# Clarifai imports for object detection
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2

# Gemini import for visual analysis
import google.generativeai as genai

# This mapping helps translate the general concepts from the Clarifai model
# into the broader categories our robot needs.
CONCEPT_TO_CATEGORY_MAP = {
    # --- Paper ---
    "paper": "paper", "cardboard": "paper", "document": "paper", "newspaper": "paper", "box": "paper",
    "magazine": "paper", "envelope": "paper", "notebook": "paper", "pamphlet": "paper",

    # --- Plastic ---
    "plastic": "plastic", "bottle": "plastic", "plastic bag": "plastic", "container": "plastic",
    "cup": "plastic", "lid": "plastic", "wrapper": "plastic", "styrofoam": "plastic", "bottle cap": "plastic",

    # --- Glass ---
    "glass": "glass", "glass bottle": "glass", "jar": "glass",

    # --- Metal ---
    "metal": "metal", "can": "metal", "aluminum": "metal", "foil": "metal", "tin can": "metal",
    "key": "metal", "scrap metal": "metal",

    # --- E-waste ---
    "electronic": "e-waste", "cable": "e-waste", "remote control": "e-waste", "device": "e-waste",
    "cell phone": "e-waste", "circuit": "e-waste", "computer mouse": "e-waste", "mouse": "e-waste",
    "keyboard": "e-waste", "screen": "e-waste", "battery": "e-waste", "plug": "e-waste",

    # --- Organic ---
    "food": "organic", "fruit": "organic", "vegetable": "organic", "banana": "organic",
    "peel": "organic", "apple": "organic", "food scrap": "organic",

    # --- Other ---
    "pen": "other", "pencil": "other", "fabric": "other", "wood": "other"
}

def _get_material_from_gemini(cropped_image: Image.Image, api_key: str) -> str:
    """
    Uses Gemini Vision to classify a cropped image by its material.
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = """
    Analyze the object in this image and classify it by its primary material.
    You MUST respond with a single word from this strict list:
    `paper`, `plastic`, `glass`, `metal`, `e-waste`, `organic`, `other`.

    Do not provide any explanation or other text. Just the single-word category.
    """
    try:
        response = model.generate_content([prompt, cropped_image])
        category = response.text.strip().lower()
        # Basic validation to ensure the model returns a valid category
        valid_categories = {'paper', 'plastic', 'glass', 'metal', 'e-waste', 'organic', 'other'}
        if category in valid_categories:
            return category
        else:
            return "other" # Default to 'other' if the response is invalid
    except Exception as e:
        print(f"Error during Gemini material analysis: {e}")
        return "error"

def classify_image(image: Image.Image, clarifai_pat: str, gemini_api_key: str):
    """
    Orchestrates a two-step "crop and classify" process:
    1. Detects objects and their bounding boxes using Clarifai.
    2. For each detected object, crops it and sends the image to Gemini for material classification.
    """
    CONFIDENCE_THRESHOLD = 0.60
    trash_items = []
    debug_info = {
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "clarifai_detections": [],
        "final_classifications": []
    }

    # --- Step 1: Detect object locations with Clarifai ---
    try:
        channel = ClarifaiChannel.get_grpc_channel()
        stub = service_pb2_grpc.V2Stub(channel)
        metadata = (('authorization', 'Key ' + clarifai_pat),)
        
        byte_arr = io.BytesIO()
        image.save(byte_arr, format='JPEG')

        post_model_outputs_response = stub.PostModelOutputs(
            service_pb2.PostModelOutputsRequest(
                user_app_id=resources_pb2.UserAppIDSet(user_id="clarifai", app_id="main"),
                model_id='general-image-detection',
                version_id='1580bb1932594c93b7e2e04456af7c6f',
                inputs=[resources_pb2.Input(data=resources_pb2.Data(image=resources_pb2.Image(base64=byte_arr.getvalue())))]
            ),
            metadata=metadata
        )

        if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
            return {"error": f"Clarifai API error: {post_model_outputs_response.status.description}"}

        high_confidence_regions = []
        for region in post_model_outputs_response.outputs[0].data.regions:
            concept = region.data.concepts[0]
            confidence = concept.value
            debug_info["clarifai_detections"].append({"name": concept.name.lower(), "confidence": f"{confidence:.2f}"})
            if confidence > CONFIDENCE_THRESHOLD:
                high_confidence_regions.append(region)

    except Exception as e:
        return {"error": f"An internal error occurred during Clarifai detection: {str(e)}"}

    # --- Step 2: Crop and Classify each detected object with Gemini ---
    if not high_confidence_regions:
        debug_info["final_classifications"].append("No objects passed confidence threshold.")
        return {"trash_items": [], "debug_info": debug_info}

    img_width, img_height = image.size
    for region in high_confidence_regions:
        box = region.region_info.bounding_box
        
        left = int(box.left_col * img_width)
        top = int(box.top_row * img_height)
        right = int(box.right_col * img_width)
        bottom = int(box.bottom_row * img_height)
        
        cropped_image = image.crop((left, top, right, bottom))
        
        category = _get_material_from_gemini(cropped_image, gemini_api_key)
        
        clarifai_name = region.data.concepts[0].name.lower()
        debug_info["final_classifications"].append({"clarifai_name": clarifai_name, "gemini_category": category})

        if category != "error":
            trash_items.append({
                "category": category,
                "bounding_box": [box.left_col, box.top_row, box.right_col, box.bottom_row]
            })

    return {"trash_items": trash_items, "debug_info": debug_info}


# --- Old: Gemini Classifier (Commented Out) ---
# import google.generativeai as genai
# from PIL import Image
# import json

# def classify_image_gemini(image: Image.Image):
#     """
#     Analyzes an image to find and locate trash objects.

#     Args:
#         image: A PIL Image object.

#     Returns:
#         A dictionary containing the structured output from the AI.
#     """
    
#     # This ensures the model uses the latest API key configured in the main app.
#     model = genai.GenerativeModel('gemini-1.5-flash-latest')

#     prompt = """
#     Analyze the provided image from a robot's camera to identify and classify all pieces of waste.
#     Your goal is to be as accurate as possible. Carefully check for multiple distinct objects.
#     **Crucially, you must ignore the surfaces the objects are resting on, such as tables, floors, and backgrounds.** Focus only on the waste items themselves.

#     Your task has two parts:
#     1.  **Locate Waste:** For each *distinct* piece of trash you find, provide a normalized bounding box `[x_min, y_min, x_max, y_max]`.
#     2.  **Classify Waste:** Assign each piece of trash to one of the following strict categories. You MUST use one of these exact strings:
#         *   `paper` (includes items like crumpled paper, cardboard, newspapers)
#         *   `plastic` (bottles, containers, bags)
#         *   `glass` (bottles, jars)
#         *   `metal` (cans, foil)
#         *   `e-waste` (cables, remote controls, electronic components)
#         *   `organic` (food scraps)
#         *   `other` (waste that does not fit any other category, like pens)

#     Respond with a single JSON object containing a key "trash_items", which is a list of objects.
#     Each object in the list represents a single piece of trash and must have two keys:
#     1.  "category": A string with one of the predefined categories listed above.
#     2.  "bounding_box": A list of four numbers for the normalized bounding box.

#     Example Response for multiple items:
#     ```json
#     {
#       "trash_items": [
#         {
#           "category": "plastic",
#           "bounding_box": [0.25, 0.4, 0.35, 0.6]
#         },
#         {
#           "category": "paper",
#           "bounding_box": [0.7, 0.5, 0.75, 0.58]
#         }
#       ]
#     }
#     ```

#     If no trash is visible, return an empty list: `{"trash_items": []}`.
#     It is critical that you identify ALL items and provide a separate entry for each one.
#     """
    
#     response = model.generate_content([prompt, image])
    
#     # Clean up the response and parse it as JSON
#     # The response.text often comes wrapped in ```