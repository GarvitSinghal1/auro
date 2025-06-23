#!/bin/bash

# This script is used by platforms like Glitch to start the application.
# We are being explicit with python3 and pip3 to avoid legacy system defaults.

echo "--- Ensuring pip for Python 3 is available ---"
python3 -m ensurepip
python3 -m pip install --upgrade pip

echo "--- Installing dependencies with pip3 ---"
pip3 install -r requirements.txt

echo "--- Starting Gunicorn server with Python 3 ---"
# Run gunicorn as a module of python3 to ensure we're using the correct one.
python3 -m gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app -b 0.0.0.0:$PORT 