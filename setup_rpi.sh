#!/bin/bash
# Setup script for Raspberry Pi
echo "Updating system..."
sudo apt-get update && sudo apt-get upgrade -y

echo "Installing dependencies for OpenCV and MediaPipe..."
sudo apt-get install -y libv4l-dev libatlas-base-dev libopenblas-dev libqt5gui5 libqt5core5a libqt5widgets5 libjasper-dev libhdf5-dev libhdf5-serial-dev libpangocairo-1.0-0 libpango-1.0-0 libavcodec-dev libavformat-dev libswscale-dev

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing Python requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# MediaPipe special install for RPi (uncomment if standard fails)
# pip install mediapipe-rpi 

echo "Setup complete! Run the app using: source venv/bin/activate && python web_app.py"
