#!/bin/bash

# Start backend in background
echo "Starting backend..."
cd app/backend && python -m srt.main &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend..."
cd app/frontend && npm run dev &
FRONTEND_PID=$!

# Handle cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Press Ctrl+C to stop both services"

# Wait for both processes
wait
