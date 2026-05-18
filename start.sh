#!/bin/bash
# Start Flask API backend + Vite dev server
cd "$(dirname "$0")"

echo "Starting Flask API on :5050..."
python3 api/server.py &
FLASK_PID=$!

echo "Starting Vite on :5173..."
npm run dev -- --host 0.0.0.0

kill $FLASK_PID 2>/dev/null
