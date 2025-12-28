FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    libpq-dev \
    redis-tools \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production

# Expose ports
EXPOSE 8000 8001 8002 8003 8004

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "agent_5_orchestrator.py"]
