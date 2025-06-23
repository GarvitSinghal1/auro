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
    # --- Configuration ---
    PUBLIC_API_URL = "https://auro-l4mh.onrender.com"
    LOCAL_API_URL = "http://127.0.0.1:8000"
    DEFAULT_PHONE_IP = "192.168.29.56:8080" 

    parser = argparse.ArgumentParser(description="Live tester for AURo classification API using a phone as an IP camera.")
    parser.add_argument("--ip", type=str, default=DEFAULT_PHONE_IP, help=f"The IP address and port of the phone camera (default: {DEFAULT_PHONE_IP})")
    parser.add_argument("--local", action="store_true", help="Use the local API server instead of the public one.")
    args = parser.parse_args()

    api_base_url = LOCAL_API_URL if args.local else PUBLIC_API_URL
    
    video_url = f"http://{args.ip}/video"
    classify_url = f"{api_base_url}/classify/"

    print("--- AURo Live Tester ---")
    print(f"Attempting to connect to phone at: {video_url}")
    print(f"Sending images to API at: {api_base_url}")
    print("\nPress SPACE to capture and classify a frame.")
    print("Press 'q' to quit.")

    cap = cv2.VideoCapture(video_url)
    if not cap.isOpened():
        print(f"\nFATAL: Could not connect to camera stream at {video_url}. Exiting.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from video stream.")
            break
            
        # Get frame dimensions
        height, width, _ = frame.shape

        cv2.imshow('Live Feed', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '): # Spacebar
            print("\nCapturing frame...")
            
            # --- OPTIMIZATION: Resize the frame before sending ---
            # We don't need a high-resolution image for classification.
            # Resizing reduces upload time and can speed up processing.
            resized_frame = cv2.resize(frame, (640, 480))
            height, width, _ = resized_frame.shape
            
            print("Sending frame to classification API...")
            # Send the smaller, resized frame for classification
            result = classify_frame(classify_url, resized_frame)
            
            if result:
                print("--- Classification Result ---")
                print(result)
                print("-----------------------------")
                
                # Updated to handle the new API response format
                # The key is now 'trash_items' and the box is 'bounding_box'
                objects_found = result.get("trash_items", [])

                if not objects_found:
                    print("No objects were found in the response.")
                
                # Draw the bounding boxes on the verification frame
                verification_frame = resized_frame.copy()
                for obj in objects_found:
                    # The new API provides normalized coordinates
                    box = obj.get("bounding_box")
                    label = obj.get("category", "unknown")
                    
                    if box and len(box) == 4:
                        # Denormalize the coordinates
                        x_min = int(box[0] * width)
                        y_min = int(box[1] * height)
                        x_max = int(box[2] * width)
                        y_max = int(box[3] * height)
                        
                        # Draw the rectangle and label
                        cv2.rectangle(verification_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                        cv2.putText(verification_frame, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
                
                cv2.imshow('Verification', verification_frame)

            else:
                print("--- Classification Failed ---")

    cap.release()
    cv2.destroyAllWindows()
    print("Tester stopped.")

if __name__ == "__main__":
    main() 