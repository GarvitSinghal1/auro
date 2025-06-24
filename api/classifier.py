import os
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from PIL import Image
import io

# This mapping helps translate the general concepts from the Clarifai model
# into the broader categories our robot needs.
CONCEPT_TO_CATEGORY_MAP = {
    # Paper
    "paper": "paper", "cardboard": "paper", "document": "paper", "newspaper": "paper", "box": "paper",
    # Plastic
    "plastic": "plastic", "bottle": "plastic", "plastic bag": "plastic", "container": "plastic", "cup": "plastic",
    # Glass
    "glass": "glass", "glass bottle": "glass", "jar": "glass",
    # Metal
    "metal": "metal", "can": "metal", "aluminum": "metal", "foil": "metal", "tin can": "metal",
    # E-waste
    "electronic": "e-waste", "cable": "e-waste", "remote control": "e-waste", "device": "e-waste", "cell phone": "e-waste", "circuit": "e-waste",
    # Organic
    "food": "organic", "fruit": "organic", "vegetable": "organic", "banana": "organic", "peel": "organic", "apple": "organic",
    # Other
    "pen": "other", "pencil": "other"
}

def classify_image(image: Image.Image, api_key: str, user_id: str, app_id: str):
    """
    Analyzes an image using the Clarifai General Detection model to find and locate trash.
    
    Args:
        image: A PIL Image object.
        api_key: The Clarifai Personal Access Token (PAT).
        user_id: The Clarifai User ID.
        app_id: The Clarifai App ID.
    """
    try:
        # Initialize the Clarifai client within the function call
        channel = ClarifaiChannel.get_grpc_channel()
        stub = service_pb2_grpc.V2Stub(channel)
        metadata = (('authorization', 'Key ' + api_key),)
        
        # Define the model details
        MODEL_ID = 'general-image-detection'
        MODEL_VERSION_ID = '1580bb1932594c93b7e2e04456af7c6f'

        # Convert PIL image to bytes
        byte_arr = io.BytesIO()
        image.save(byte_arr, format='JPEG')
        image_bytes = byte_arr.getvalue()

        post_model_outputs_response = stub.PostModelOutputs(
            service_pb2.PostModelOutputsRequest(
                user_app_id=resources_pb2.UserAppIDSet(user_id=user_id, app_id=app_id),
                model_id=MODEL_ID,
                version_id=MODEL_VERSION_ID,
                inputs=[resources_pb2.Input(data=resources_pb2.Data(image=resources_pb2.Image(base64=image_bytes)))]
            ),
            metadata=metadata
        )

        if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
            error_message = f"Clarifai API error: {post_model_outputs_response.status.description}"
            print(error_message)
            return {"error": error_message, "raw_response": str(post_model_outputs_response.status)}

        # Parse Clarifai Response
        trash_items = []
        regions = post_model_outputs_response.outputs[0].data.regions
        for region in regions:
            if not region.data.concepts:
                continue
            
            top_concept = region.data.concepts[0]
            concept_name = top_concept.name
            confidence = top_concept.value

            # Filter based on our concept map and a confidence threshold
            if concept_name in CONCEPT_TO_CATEGORY_MAP and confidence > 0.7:
                category = CONCEPT_TO_CATEGORY_MAP[concept_name]
                box = region.region_info.bounding_box
                
                trash_items.append({
                    "category": category,
                    "bounding_box": [box.left_col, box.top_row, box.right_col, box.bottom_row]
                })

        return {"trash_items": trash_items}

    except Exception as e:
        print(f"An error occurred during Clarifai classification: {str(e)}")
        return {"error": "An internal error occurred with the classification service."}


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
#     # The response.text often comes wrapped in ```json ... ```
#     cleaned_text = response.text.strip().replace("```json", "").replace("```", "").strip()
#     try:
#         return json.loads(cleaned_text)
#     except json.JSONDecodeError:
#         print(f"Error: Could not decode JSON from response: {cleaned_text}")
#         # Return a structured error or an empty list
#         return {"error": "Failed to parse AI response", "raw_response": cleaned_text} 