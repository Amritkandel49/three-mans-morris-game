#!/bin/bash

# Three Men's Morris Web Game Launcher

echo "Starting Three Men's Morris Web Game..."
echo "========================================="

# Check if requirements are installed
python3 -c "import fastapi, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

echo "Starting server on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
