#!/bin/bash
echo "Starting Oasiz Chatbot Backend..."
echo "Python version: $(python3 --version)"
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port $PORT --log-level info

