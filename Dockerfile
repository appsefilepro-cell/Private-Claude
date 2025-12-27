# Multi-stage Dockerfile for Agent 5.0 Production Deployment
# Optimized for minimal image size and maximum security

# ==============================================================================
# Stage 1: Base Python Image with System Dependencies
# ==============================================================================
FROM python:3.11-slim-bullseye AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    postgresql-client \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# ==============================================================================
# Stage 2: Dependencies Installation
# ==============================================================================
FROM base AS dependencies

# Create app directory
WORKDIR /tmp

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
    psutil>=5.9.0 \
    redis>=5.0.0 \
    psycopg2-binary>=2.9.0 \
    pymongo>=4.5.0 \
    requests>=2.31.0 \
    aiohttp>=3.9.0 \
    python-dotenv>=1.0.0 \
    cryptography>=41.0.0 \
    pydantic>=2.5.0 \
    fastapi>=0.104.0 \
    uvicorn>=0.24.0 \
    sqlalchemy>=2.0.0 \
    alembic>=1.12.0 \
    celery>=5.3.0 \
    prometheus-client>=0.19.0

# ==============================================================================
# Stage 3: Final Production Image
# ==============================================================================
FROM python:3.11-slim-bullseye AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:$PATH" \
    APP_HOME=/app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /home/appuser -s /sbin/nologin -c "App user" appuser && \
    mkdir -p /home/appuser/.local /app/logs /app/data && \
    chown -R appuser:appuser /home/appuser /app

# Copy Python packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR $APP_HOME

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p \
    logs \
    data \
    backtest-results \
    test-results \
    config \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose ports
# 8000: Main application
# 8001: Trading bot
# 8002: Data ingestion
# 8003: Incident response
# 8004: Health monitoring
# 9090: Prometheus metrics
EXPOSE 8000 8001 8002 8003 8004 9090

# Health check configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Volume mount points
VOLUME ["/app/logs", "/app/data"]

# Default command (can be overridden by railway.json)
CMD ["python3", "agent_5_orchestrator.py"]

# ==============================================================================
# Build arguments and labels for metadata
# ==============================================================================
ARG BUILD_DATE
ARG VERSION=1.0.0
ARG VCS_REF

LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.title="Agent 5.0 Production System" \
      org.opencontainers.image.description="Complete AI agent orchestration platform with trading, legal research, and automation capabilities" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.vendor="Agent 5.0" \
      org.opencontainers.image.licenses="MIT" \
      maintainer="Agent 5.0 Team"

# ==============================================================================
# Development Stage (Optional - for local development)
# ==============================================================================
FROM production AS development

# Switch back to root to install dev dependencies
USER root

# Install development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    htop \
    net-tools \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN pip install --no-cache-dir \
    pytest>=7.4.0 \
    pytest-asyncio>=0.21.0 \
    pytest-cov>=4.1.0 \
    black>=23.10.0 \
    flake8>=6.1.0 \
    mypy>=1.6.0 \
    isort>=5.12.0 \
    ipython>=8.17.0

# Switch back to appuser
USER appuser

# Development command
CMD ["python3", "-u", "agent_5_orchestrator.py"]
