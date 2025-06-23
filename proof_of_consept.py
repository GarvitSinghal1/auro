import cv2
import os
import time
import sys
from PIL import Image
import io
import google.generativeai as genai
import argparse
import threading
from dotenv import load_dotenv

load_dotenv()



def setup_gemini(api_key):
 if not api_key or api_key == "YOUR_GEMINI_API_KEY":
  print("ERROR: Please set your Gemini API key.")
  sys.exit(1)
 try:
  genai.configure(api_key=api_key)
  model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
  return model
 except Exception as e:
  print(f"Error setting up Gemini: {str(e)}")
  sys.exit(1)

def get_frame_from_ip_camera(ip_address, debug=False):
 url = f'http://{ip_address}/video'
 print(f"Connecting to camera at {url}")
 try:
  if debug:
   print("Debug mode: Using test image instead of camera")
   frame = create_test_image()
   return True, frame
  cap = cv2.VideoCapture(url)
  if not cap.isOpened():
   print(f"Failed to open video stream at {url}")
   print("Check that your camera is on and accessible at this address")
   return False, None
  ret, frame = cap.read()
  cap.release()
  if not ret or frame is None:
   print("Camera connected but failed to read frame")
   return False, None
  return ret, frame
 except Exception as e:
  print(f"Error accessing camera: {str(e)}")
  return False, None

def create_test_image():
 img = np.zeros((480, 640, 3), np.uint8)
 img.fill(200)
 font = cv2.FONT_HERSHEY_SIMPLEX
 cv2.putText(img, 'TEST IMAGE', (220, 100), font, 1, (0, 0, 0), 2)
 cv2.putText(img, 'Paper', (100, 200), font, 1, (0, 0, 255), 2)
 cv2.putText(img, 'Plastic', (100, 300), font, 1, (255, 0, 0), 2)
 cv2.putText(img, 'Glass', (100, 400), font, 1, (0, 255, 0), 2)
 return img

def classify_object(model, image):
 img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
 pil_img = Image.fromarray(img_rgb)
 img_byte_arr = io.BytesIO()
 pil_img.save(img_byte_arr, format='JPEG')
 img_byte_arr = img_byte_arr.getvalue()
 prompt = """
 Classify the object in this image into one of these categories:
 - paper
 - plastic
 - glass
 - metal
 - nothing
 - others
 - E-waste
 - If mixed then send mixed(and the categories of the objects in the image)
 Return ONLY the category name without any additional text.
 If its just a white background then its nothing.
 """
 response = model.generate_content([prompt, pil_img])
 return response.text.strip()

def main():
 parser = argparse.ArgumentParser(description='Object classifier using Gemini AI')
 parser.add_argument('--debug', action='store_true', help='Run in debug mode with test images')
 parser.add_argument('--ip', type=str, default="192.168.29.56:8080", help='IP camera address')
 parser.add_argument('--key', type=str, help='Gemini API key')
 parser.add_argument('--rate-limit', type=int, default=6, help='Time in seconds between API requests (default: 6)')
 args = parser.parse_args()
 GEMINI_API_KEY = args.key or os.getenv("GEMINI_API_KEY")
 ip_camera_address = args.ip
 debug_mode = args.debug
 request_interval = args.rate_limit
 print(f"API request interval set to {request_interval} seconds")
 if debug_mode:
  global np
  import numpy as np
  print("Running in DEBUG mode with test images")
 model = setup_gemini(GEMINI_API_KEY)
 print("Starting object classification...")
 def classify_in_background(model, image):
  nonlocal is_processing, last_classification
  try:
   result = classify_object(model, image)
   last_classification = result
   print(f"Object classified as: {result}")
  except Exception as e:
   print(f"Classification error: {str(e)}")
   last_classification = "Error: Classification failed"
  finally:
   is_processing = False
 try:
  last_request_time = 0
  last_classification = None
  is_processing = False
  processing_frames = 0
  while True:
   ret, frame = get_frame_from_ip_camera(ip_camera_address, debug_mode)
   if not ret:
    print("Failed to capture frame from IP camera")
    print("Retrying in 2 seconds...")
    time.sleep(2)
    continue
   display_frame = frame.copy()
   font = cv2.FONT_HERSHEY_SIMPLEX
   if is_processing:
    processing_frames = (processing_frames + 1) % 8
    dots = "." * (processing_frames // 2 + 1)
    cv2.putText(display_frame, f"Processing{dots}", (10, 30), font, 1, (0, 0, 255), 2)
   elif last_classification:
    cv2.putText(display_frame, f"Object: {last_classification}", (10, 30), font, 1, (0, 255, 0), 2)
   if not is_processing:
    time_since_last = time.time() - last_request_time
    time_to_next = max(0, request_interval - time_since_last)
    cv2.putText(display_frame, f"Next scan in: {time_to_next:.1f}s", (10, 70), font, 0.7, (0, 200, 255), 2)
   status_bar_height = 30
   status_bar = display_frame[-status_bar_height:, :].copy()
   status_bar.fill(50)
   if is_processing:
    status_text = "Status: PROCESSING - Please wait..."
    status_color = (0, 165, 255)
   else:
    status_text = "Status: READY - Press 'c' to classify now, 'q' to quit"
    status_color = (0, 255, 0)
   cv2.putText(status_bar, status_text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)
   display_frame[-status_bar_height:, :] = status_bar
   cv2.imshow('IP Camera Feed', display_frame)
   current_time = time.time()
   if not is_processing and current_time - last_request_time >= request_interval:
    is_processing = True
    last_request_time = current_time
    process_frame = frame.copy()
    thread = threading.Thread(target=classify_in_background, args=(model, process_frame))
    thread.daemon = True
    thread.start()
   key = cv2.waitKey(1) & 0xFF
   if key == ord('q'):
    print("Quitting...")
    break
   elif key == ord('c') and not is_processing:
    print("Manual classification triggered")
    is_processing = True
    last_request_time = time.time()
    process_frame = frame.copy()
    thread = threading.Thread(target=classify_in_background, args=(model, process_frame))
    thread.daemon = True
    thread.start()
   time.sleep(0.1)
 except KeyboardInterrupt:
  print("Stopping...")
 finally:
  cv2.destroyAllWindows()

if __name__ == "__main__":
 print("Starting Object Classification with Gemini AI")
 print("----------------------------------------------")
 print("Press 'q' to quit at any time")
 print("Run with --debug flag to use test images instead of camera")
 print("Example: python main.py --debug")
 print("----------------------------------------------")
 main() 