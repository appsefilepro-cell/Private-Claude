# Agent X5.0 - Enterprise Multi-Agent System
# Docker configuration for sandbox and production deployment

FROM python:3.11-slim

LABEL maintainer="APPS Holdings WY Inc."
LABEL version="5.0.0"
LABEL description="Agent X5.0 - 219 Agents Multi-Agent Orchestration System"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LIVE_TRADING=false
ENV LOG_LEVEL=INFO

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash agentx5
RUN chown -R agentx5:agentx5 /app
USER agentx5

# Expose ports
EXPOSE 8080 8081 8082

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command - Run Agent X5 Orchestrator
CMD ["python", "scripts/agent_x5_master_orchestrator.py"]
