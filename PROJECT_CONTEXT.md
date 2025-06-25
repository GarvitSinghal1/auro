# AURo Project Context & State

**Document Purpose:** This file serves as a persistent memory and state tracker for the AURo project. It is intended for any AI assistant or human developer who joins the project to understand its history, current status, established workflow rules, and future direction.

**Last Updated:** Version 1.7.3

---

## 1. Project Goal

To build the complete software stack for the Autonomous Urban Recycler (AURo), a robot that can automatically identify, pick up, and sort waste items into different categories.

---

## 2. Current State & Architecture (Where We Are)

The project is currently focused on the cloud-based "brain" of the robot. The core API is feature-complete and deployed.

- **API Version:** 1.7.3
- **Deployment:** The API is live and publicly accessible on Render at [https://auro-l4mh.onrender.com](https://auro-l4mh.onrender.com).
- **Architecture:** We have implemented a sophisticated **"crop-and-classify" hybrid AI model**:
    1.  **Detection (Clarifai):** The API receives an image and sends it to Clarifai's `general-image-detection` model to get the bounding boxes of potential objects.
    2.  **Analysis (Gemini Vision):** For each object found with a confidence above a set threshold, the API crops the object from the original image and sends the small, focused image to the `gemini-1.5-flash-latest` model for accurate material classification.
- **Testing:** The `live_tester.py` script is our primary tool for local and remote testing of the API. It uses a phone as an IP camera.
- **Documentation:**
    - `README.md` is fully updated with the current architecture and setup instructions.
    - The `/docs` page on the API is automatically generated and includes detailed response models for clarity.

---

## 3. Collaboration Rules (How We Work)

We have established a clear and effective development workflow. **These rules must be followed.**

- **Rule 1: AI Develops, User Tests.** My role (as the AI assistant) is to write and modify the code. The user's role is to run the local server (`python -m api.main`) and test the changes using `live_tester.py`.
- **Rule 2: User Pushes to Deploy.** I **must not** use `git push`. The user has the sole responsibility and privilege of pushing the code to the `main` GitHub branch, which automatically triggers the deployment to Render.
- **Rule 3: AI Manages Versions.** For any significant change to the API logic or response, I am responsible for incrementing the version number in `api/main.py`.
- **Rule 4: AI Manages Documentation.** I am responsible for keeping the `README.md` file and any other documentation (like the `/docs` page models in `api/main.py`) up-to-date with the latest changes.

---

## 4. Future Direction (Where We Are Going)

The cloud API is now stable and powerful. The project's focus must now shift entirely to **Hardware Integration and Control**.

The immediate next steps are to work on the **`esp32_client/esp32_client.ino`** file. The goal is to replace `live_tester.py` with the actual robot hardware.

### Key Tasks:
1.  **ESP32 Image Capture:** Implement the C++/Arduino code to capture an image from the attached ESP32-CAM.
2.  **ESP32 API Call:** Implement the code to connect the ESP32 to Wi-Fi and make a `POST` request to the public API endpoint (`https://auro-l4mh.onrender.com/classify/`) with the captured image.
3.  **ESP32 JSON Parsing:** Implement a JSON parsing library on the ESP32 to understand the response from the API. The most important fields are `category` and `bounding_box`.
4.  **Servo Control Logic:** This is the ultimate goal. Based on the parsed JSON data, implement the logic to control the robotic arm's servos to physically sort the identified object. 