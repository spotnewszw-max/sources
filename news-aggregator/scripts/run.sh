#!/bin/bash

# Activate the virtual environment
source venv/bin/activate  # For Unix-based systems
# venv\Scripts\activate  # Uncomment this line for Windows

# Run the FastAPI application
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload