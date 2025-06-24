import google.generativeai as genai
from PIL import Image
import json

def classify_image(image: Image.Image):
    """
    Analyzes an image to find and locate trash objects.

    Args:
        image: A PIL Image object.

    Returns:
        A dictionary containing the structured output from the AI.
    """
    
    # This ensures the model uses the latest API key configured in the main app.
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = """
    Analyze the provided image from a robot's camera to identify and classify all pieces of waste.
    Your goal is to be as accurate as possible. Carefully check for multiple distinct objects.

    Your task has two parts:
    1.  **Locate Waste:** For each *distinct* piece of trash you find, provide a normalized bounding box `[x_min, y_min, x_max, y_max]`.
    2.  **Classify Waste:** Assign each piece of trash to one of the following strict categories. You MUST use one of these exact strings:
        *   `paper` (includes items like crumpled paper, cardboard, newspapers)
        *   `plastic` (bottles, containers, bags)
        *   `glass` (bottles, jars)
        *   `metal` (cans, foil)
        *   `e-waste` (cables, electronic components)
        *   `organic` (food scraps)
        *   `other` (waste that does not fit any other category, like pens)

    Respond with a single JSON object containing a key "trash_items", which is a list of objects.
    Each object in the list represents a single piece of trash and must have two keys:
    1.  "category": A string with one of the predefined categories listed above.
    2.  "bounding_box": A list of four numbers for the normalized bounding box.

    Example Response for multiple items:
    ```json
    {
      "trash_items": [
        {
          "category": "plastic",
          "bounding_box": [0.25, 0.4, 0.35, 0.6]
        },
        {
          "category": "paper",
          "bounding_box": [0.7, 0.5, 0.75, 0.58]
        }
      ]
    }
    ```

    If no trash is visible, return an empty list: `{"trash_items": []}`.
    It is critical that you identify ALL items and provide a separate entry for each one.
    """
    
    response = model.generate_content([prompt, image])
    
    # Clean up the response and parse it as JSON
    # The response.text often comes wrapped in ```json ... ```
    cleaned_text = response.text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from response: {cleaned_text}")
        # Return a structured error or an empty list
        return {"error": "Failed to parse AI response", "raw_response": cleaned_text} 