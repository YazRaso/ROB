#!/bin/bash
# Start the backend server
cd "$(dirname "$0")/src/backend"
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
