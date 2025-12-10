#!/bin/bash

# Business Automation System X3.0 - Run Script
# Starts the application with proper configuration

set -e

echo "=================================================="
echo "Business Automation System X3.0"
echo "Starting application..."
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Run ./deploy.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Run ./deploy.sh first"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Create log directories if they don't exist
mkdir -p logs
mkdir -p /var/log/business-automation 2>/dev/null || mkdir -p logs/business-automation

# Check environment
ENVIRONMENT=${ENVIRONMENT:-development}
echo "Environment: $ENVIRONMENT"

if [ "$ENVIRONMENT" = "production" ]; then
    echo "Running in PRODUCTION mode with 25 workers"
    MAX_WORKERS=${MAX_WORKERS:-25}
else
    echo "Running in DEVELOPMENT mode"
    MAX_WORKERS=1
fi

# Check sandbox mode
if [ "$SANDBOX_MODE" = "True" ] || [ "$SANDBOX_MODE" = "true" ]; then
    echo "⚠️  SANDBOX MODE ENABLED - No real trades will be executed"
fi

echo ""
echo "Starting server on http://0.0.0.0:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop"
echo "=================================================="

# Run application
if [ "$ENVIRONMENT" = "production" ]; then
    # Production: Use Gunicorn with Uvicorn workers
    gunicorn main:app \
        --workers $MAX_WORKERS \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --access-logfile logs/access.log \
        --error-logfile logs/error.log \
        --timeout 120 \
        --graceful-timeout 30 \
        --keep-alive 5
else
    # Development: Use Uvicorn directly with reload
    uvicorn main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --log-level info
fi
