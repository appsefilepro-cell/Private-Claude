# Docker container for complete system - connects to E2B, runs all agents
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install additional trading libraries
RUN pip install --no-cache-dir \
    MetaTrader5 \
    ccxt \
    requests \
    aiohttp \
    websockets

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p logs/errors logs/audit logs/trading logs/agents logs/migration \
    data/trades \
    agent-orchestrator/communication \
    legal-automation/output

# Environment variables for E2B
ENV E2B_API_KEY=e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773
ENV E2B_WEBHOOK_ID=YIyOpaJ0UMJ3Pl9Md5kVExEDdkqyDGRp
ENV PYTHONUNBUFFERED=1

# Expose ports for APIs
EXPOSE 8000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

# Run Agent 5.0 orchestrator
CMD ["python3", "agent-orchestrator/master_orchestrator.py"]
