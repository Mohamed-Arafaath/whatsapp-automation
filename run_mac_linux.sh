#!/bin/bash
echo "Starting WhatsApp Automation..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed! Please install it first."
    exit 1
fi

echo "Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Starting the application..."
echo "Open http://localhost:5001 in your browser"
echo ""

python3 app.py
