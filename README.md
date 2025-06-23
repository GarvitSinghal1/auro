# Autonomous Urban Recycler (AURo) - Classification API

![AURo Project](https://img.shields.io/badge/Project-AURo-blue)
![Language](https://img.shields.io/badge/Language-Python-blueviolet)
![Framework](https://img.shields.io/badge/Framework-FastAPI-green)
![Deployment](https://img.shields.io/badge/Deployment-Render-lightgrey)

This repository contains the backend classification API for the **Autonomous Urban Recycler (AURo)** project. It provides a web service that can classify images of waste into various categories, forming the core of the robot's "vision" system.

## Project Overview

AURo is an autonomous four-wheel mobile robot designed to enhance urban waste management. Equipped with a robotic arm and internal compartments, the robot can autonomously service smart dustbins, collecting and segregating waste using sensor and vision-based classification techniques.

This API serves as the cloud-based brain for the robot's classification pipeline.

## Live API

The API is currently deployed and live on Render.

**Public API URL:** `https://auro-l4mh.onrender.com`

You can view the interactive API documentation here:
**[https://auro-l4mh.onrender.com/docs](https://auro-l4mh.onrender.com/docs)**

## How to Use the API

The API exposes a single primary endpoint for classification.

### `POST /classify/`

This endpoint accepts a single image file and returns a JSON object with the classification result.

**Request:**
- **Method:** `POST`
- **URL:** `https://auro-l4mh.onrender.com/classify/`
- **Body:** `multipart/form-data` with a single file field named `file`.

**Success Response (200 OK):**
```json
{
  "model_used": "gemini-1.5-flash",
  "classification": "plastic",
  "response_time": "1.87s"
}
```

## Local Testing with `live_tester.py`

To test the live API with a continuous video feed (e.g., from a phone), you can use the `live_tester.py` script.

### Prerequisites
- Python 3 installed
- An IP camera app running on your phone

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/GarvitSinghal1/auro.git
   cd auro
   ```
2. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Tester
1. Start the IP camera app on your phone and note the video stream URL.
2. Run the script from your terminal, providing the video URL:
   ```bash
   python live_tester.py --url http://<your-phone-ip>:<port>/video
   ```
3. A window will appear showing the live camera feed. Press the **SPACEBAR** to capture the current frame and send it to the live API for classification. The result will be printed in your terminal.
4. Press **'q'** to quit.

## Deployment

This project is configured for continuous deployment on [Render](https://render.com). Any push to the `main` branch of this GitHub repository will automatically trigger a new deployment of the API. 