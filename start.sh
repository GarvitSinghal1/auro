#!/bin/bash

# This script is used by platforms like Glitch to start the application.

# Install dependencies
pip install -r requirements.txt

# Start the Gunicorn server
# It will run the 'app' object from the 'api.main' module.
# We bind it to 0.0.0.0 and a port provided by the hosting environment.
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app -b 0.0.0.0:$PORT 