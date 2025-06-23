import cv2
import requests
import numpy as np
import argparse

def get_frame_from_phone(video_url):
    """
    Captures a single frame from the phone's IP camera stream.
    """
    try:
        cap = cv2.VideoCapture(video_url)
        if not cap.isOpened():
            print(f"Error: Could not open video stream at {video_url}")
            print("Please check the URL and ensure the IP Webcam app is running.")
            return None
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret or frame is None:
            print("Error: Failed to read frame from the stream.")
            return None
            
        return frame
    except Exception as e:
        print(f"An error occurred while getting the frame: {str(e)}")
        return None

def classify_frame(api_url, frame):
    """
    Sends a single frame to the classification API.
    """
    try:
        # Encode the frame as a JPEG image in memory
        is_success, buffer = cv2.imencode(".jpg", frame)
        if not is_success:
            print("Error: Could not encode frame to JPEG.")
            return None
        
        # Create the file-like object for the request
        files = {'file': ('image.jpg', buffer.tobytes(), 'image/jpeg')}
        
        # Send the request
        response = requests.post(api_url, files=files, timeout=10)
        
        # Check for successful response
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error sending request to API: {str(e)}")
        return None
    except Exception as e:
        print(f"An error occurred during classification: {str(e)}")
        return None

def main():
    # The API URL is now fixed since we've deployed to Render.
    API_BASE_URL = "https://auro-l4mh.onrender.com"

    parser = argparse.ArgumentParser(description="Live tester for AURo classification API using a phone as an IP camera.")
    parser.add_argument("--url", type=str, required=True, help="The full video stream URL from your IP camera app (e.g., http://192.168.1.10:8080/video)")
    args = parser.parse_args()

    video_url = args.url
    classify_url = f"{API_BASE_URL}/classify/"

    print("--- AURo Live Tester ---")
    print(f"Attempting to connect to phone at: {video_url}")
    print(f"Sending images to public API at: {API_BASE_URL}")
    print("\nPress SPACE to capture and classify a frame.")
    print("Press 'q' to quit.")

    cap = cv2.VideoCapture(video_url)
    if not cap.isOpened():
        print(f"\nFATAL: Could not connect to camera stream at {video_url}. Exiting.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Lost connection to camera stream. Retrying...")
            cap.release()
            cap = cv2.VideoCapture(video_url)
            cv2.waitKey(1000)
            continue

        cv2.imshow("Phone Camera Feed - Press SPACE to Classify", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '): # Spacebar
            print("\nCapturing frame...")
            
            # --- OPTIMIZATION: Resize the frame before sending ---
            # We don't need a high-resolution image for classification.
            # Resizing reduces upload time and can speed up processing.
            resized_frame = cv2.resize(frame, (640, 480))
            
            print("Sending frame to classification API...")
            # Send the smaller, resized frame for classification
            result = classify_frame(classify_url, resized_frame)
            
            if result:
                print("--- Classification Result ---")
                print(result)
                print("-----------------------------")
                
                # --- VISUAL VERIFICATION ---
                # Draw the results on a copy of the resized frame
                verification_frame = resized_frame.copy()
                objects = result.get("objects_found", [])
                
                if objects:
                    for obj in objects:
                        box = obj.get("box")
                        label = obj.get("label", "unknown")
                        
                        if box and len(box) == 4:
                            x_min, y_min, x_max, y_max = box
                            # Draw a rectangle using the bounding box coordinates
                            cv2.rectangle(verification_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                            # Put the label text near the top-left corner of the box
                            cv2.putText(verification_frame, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                    cv2.imshow("Verification - Press any key to close", verification_frame)
                    cv2.waitKey(0) # Wait for a key press to close the verification window
                    cv2.destroyWindow("Verification - Press any key to close")
                else:
                    print("No objects were found in the response.")

            else:
                print("--- Classification Failed ---")

    cap.release()
    cv2.destroyAllWindows()
    print("Tester stopped.")

if __name__ == "__main__":
    main() 