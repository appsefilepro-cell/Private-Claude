#!/bin/bash

################################################################################
# Cloud Environment Setup Script
################################################################################
#
# This script automates the complete setup of cloud environments including:
# - E2B sandbox configuration and deployment
# - Railway platform setup and configuration
# - Environment variable configuration
# - Database initialization and migrations
# - Service health checks and validation
# - Network configuration and security
#
# Supported Platforms:
# - E2B (Code Execution Sandboxes)
# - Railway (Production Deployment)
# - PostgreSQL (Database)
# - Redis (Cache)
#
# Author: Agent 5.0 System
# Version: 2.0.0
#
################################################################################

set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SETUP_LOG="${PROJECT_ROOT}/logs/cloud_setup_$(date +%Y%m%d_%H%M%S).log"
ENV_FILE="${PROJECT_ROOT}/.env"
ENV_TEMPLATE="${PROJECT_ROOT}/.env.template"

# Ensure logs directory exists
mkdir -p "${PROJECT_ROOT}/logs"

################################################################################
# Utility Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $@" | tee -a "${SETUP_LOG}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $@" | tee -a "${SETUP_LOG}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $@" | tee -a "${SETUP_LOG}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $@" | tee -a "${SETUP_LOG}"
}

print_header() {
    local title="$1"
    echo -e "\n${CYAN}================================================================${NC}" | tee -a "${SETUP_LOG}"
    echo -e "${CYAN}${title}${NC}" | tee -a "${SETUP_LOG}"
    echo -e "${CYAN}================================================================${NC}\n" | tee -a "${SETUP_LOG}"
}

print_banner() {
    cat << 'EOF' | tee -a "${SETUP_LOG}"

   █████╗  ██████╗ ███████╗███╗   ██╗████████╗██╗  ██╗███████╗
  ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝╚██╗██╔╝██╔════╝
  ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║    ╚███╔╝ ███████╗
  ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║    ██╔██╗ ╚════██║
  ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ██╔╝ ██╗███████║
  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚══════╝

  Cloud Environment Setup - Complete Automation Platform

EOF
}

confirm_action() {
    local prompt="$1"
    local default="${2:-n}"

    if [[ "${AUTO_CONFIRM:-false}" == "true" ]]; then
        return 0
    fi

    read -p "${prompt} [y/N]: " response
    response=${response:-$default}

    if [[ "$response" =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

check_command() {
    local cmd="$1"
    if command -v "$cmd" &> /dev/null; then
        log_success "Found: $cmd"
        return 0
    else
        log_error "Missing: $cmd"
        return 1
    fi
}

################################################################################
# Prerequisite Checks
################################################################################

check_prerequisites() {
    print_header "Checking Prerequisites"

    log_info "Checking required commands..."

    local required_commands=(
        "git"
        "python3"
        "pip"
        "curl"
        "jq"
        "node"
        "npm"
    )

    local missing_commands=()

    for cmd in "${required_commands[@]}"; do
        if ! check_command "$cmd"; then
            missing_commands+=("$cmd")
        fi
    done

    if [ ${#missing_commands[@]} -ne 0 ]; then
        log_error "Missing required commands: ${missing_commands[*]}"
        log_info "Please install missing dependencies and try again"
        return 1
    fi

    log_info "Checking Python version..."
    python_version=$(python3 --version | cut -d' ' -f2)
    required_version="3.11"

    if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
        log_error "Python version $python_version is below required $required_version"
        return 1
    fi

    log_success "Python version: $python_version"

    log_info "Checking Node.js version..."
    node_version=$(node --version | cut -d'v' -f2)
    log_success "Node.js version: $node_version"

    log_success "All prerequisites satisfied"
}

################################################################################
# Environment Variable Setup
################################################################################

setup_environment_variables() {
    print_header "Environment Variables Setup"

    log_info "Setting up environment variables..."

    # Create .env.template if it doesn't exist
    if [[ ! -f "$ENV_TEMPLATE" ]]; then
        log_info "Creating .env.template..."

        cat > "$ENV_TEMPLATE" << 'EOF'
# Agent 5.0 Environment Configuration
# =====================================

# Application Settings
APP_NAME=AgentX5
APP_ENV=production
APP_DEBUG=false
APP_VERSION=5.0.0

# Railway Configuration
RAILWAY_TOKEN=
RAILWAY_PROJECT_ID=
RAILWAY_ENVIRONMENT=production

# E2B Sandbox Configuration
E2B_API_KEY=
E2B_SANDBOX_ID=
E2B_SANDBOX_ENABLED=true

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/agentx5
POSTGRES_USER=agentx5
POSTGRES_PASSWORD=
POSTGRES_DB=agentx5
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# API Keys
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
BINANCE_API_KEY=
BINANCE_SECRET_KEY=

# GitLab Configuration
GITLAB_TOKEN=
GITLAB_PROJECT_ID=
CI_SERVER_URL=https://gitlab.com

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
EMAIL_FROM=noreply@agentx5.com

# Security
SECRET_KEY=
JWT_SECRET=
ENCRYPTION_KEY=

# Monitoring
SENTRY_DSN=
DATADOG_API_KEY=

# Feature Flags
GITLAB_DUO_ENABLED=true
COPILOT_ENABLED=true
AUTO_FIX_ENABLED=true
TRADING_ENABLED=true

# Service Ports
ORCHESTRATOR_PORT=8000
TRADING_PORT=8001
DATA_INGESTION_PORT=8002
INCIDENT_RESPONSE_PORT=8003
HEALTH_MONITOR_PORT=8004

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/agentx5/app.log

EOF
        log_success ".env.template created"
    fi

    # Create .env if it doesn't exist
    if [[ ! -f "$ENV_FILE" ]]; then
        log_info "Creating .env from template..."
        cp "$ENV_TEMPLATE" "$ENV_FILE"
        log_success ".env created"

        log_warning "Please update .env file with your actual configuration values"
        log_info "Edit: $ENV_FILE"
    else
        log_info ".env file already exists"
    fi

    # Generate secrets if needed
    log_info "Generating missing secrets..."

    if ! grep -q "^SECRET_KEY=.\+$" "$ENV_FILE"; then
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        echo "SECRET_KEY=$SECRET_KEY" >> "$ENV_FILE"
        log_success "Generated SECRET_KEY"
    fi

    if ! grep -q "^JWT_SECRET=.\+$" "$ENV_FILE"; then
        JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        echo "JWT_SECRET=$JWT_SECRET" >> "$ENV_FILE"
        log_success "Generated JWT_SECRET"
    fi

    if ! grep -q "^ENCRYPTION_KEY=.\+$" "$ENV_FILE"; then
        ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        echo "ENCRYPTION_KEY=$ENCRYPTION_KEY" >> "$ENV_FILE"
        log_success "Generated ENCRYPTION_KEY"
    fi

    log_success "Environment variables configured"
}

################################################################################
# E2B Sandbox Setup
################################################################################

setup_e2b_sandbox() {
    print_header "E2B Sandbox Setup"

    log_info "Setting up E2B sandbox environment..."

    # Check if E2B CLI is installed
    if ! command -v e2b &> /dev/null; then
        log_info "Installing E2B CLI..."
        npm install -g @e2b/cli || {
            log_error "Failed to install E2B CLI"
            return 1
        }
        log_success "E2B CLI installed"
    else
        log_success "E2B CLI already installed"
    fi

    # Check for E2B API key
    source "$ENV_FILE"

    if [[ -z "$E2B_API_KEY" ]]; then
        log_warning "E2B_API_KEY not set in .env file"
        log_info "Please obtain an API key from https://e2b.dev"
        log_info "Then update E2B_API_KEY in: $ENV_FILE"
        return 0
    fi

    export E2B_API_KEY

    # Create E2B configuration
    log_info "Creating E2B sandbox template..."

    cat > "${PROJECT_ROOT}/e2b.toml" << 'EOF'
[sandbox]
name = "agentx5-sandbox"
template = "base"

[sandbox.build]
dockerfile = "e2b.Dockerfile"

[sandbox.resources]
memory = 4096
cpu = 2
disk = 10240

[sandbox.ports]
8000 = { public = true }
8001 = { public = true }
8002 = { public = false }
8003 = { public = false }
8004 = { public = false }

[sandbox.env]
PYTHONUNBUFFERED = "1"
APP_ENV = "production"
EOF

    log_success "E2B configuration created"

    # Create Dockerfile for E2B
    if [[ ! -f "${PROJECT_ROOT}/e2b.Dockerfile" ]]; then
        log_info "Creating E2B Dockerfile..."

        cat > "${PROJECT_ROOT}/e2b.Dockerfile" << 'EOF'
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
EOF

        log_success "E2B Dockerfile created"
    fi

    log_success "E2B sandbox setup completed"
    log_info "To build sandbox: e2b sandbox build"
    log_info "To create sandbox: e2b sandbox create agentx5-sandbox"
}

################################################################################
# Railway Setup
################################################################################

setup_railway() {
    print_header "Railway Platform Setup"

    log_info "Setting up Railway deployment..."

    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        log_info "Installing Railway CLI..."
        npm install -g @railway/cli || {
            log_error "Failed to install Railway CLI"
            return 1
        }
        log_success "Railway CLI installed"
    else
        log_success "Railway CLI already installed"
    fi

    # Create railway.json if it doesn't exist
    if [[ ! -f "${PROJECT_ROOT}/railway.json" ]]; then
        log_info "Creating railway.json..."

        cat > "${PROJECT_ROOT}/railway.json" << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "python agent_5_orchestrator.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF

        log_success "railway.json created"
    fi

    # Create Procfile for Railway
    if [[ ! -f "${PROJECT_ROOT}/Procfile" ]]; then
        log_info "Creating Procfile..."

        cat > "${PROJECT_ROOT}/Procfile" << 'EOF'
web: python agent_5_orchestrator.py
worker: python scripts/agentx5_24_7_supervisor.py
EOF

        log_success "Procfile created"
    fi

    log_success "Railway setup completed"
    log_info "To link project: railway link"
    log_info "To deploy: railway up"
}

################################################################################
# Database Setup
################################################################################

setup_database() {
    print_header "Database Initialization"

    log_info "Setting up PostgreSQL database..."

    source "$ENV_FILE"

    # Create database initialization script
    cat > "${PROJECT_ROOT}/scripts/init_database.sql" << 'EOF'
-- Agent 5.0 Database Schema
-- ===========================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS trading;
CREATE SCHEMA IF NOT EXISTS legal;
CREATE SCHEMA IF NOT EXISTS financial;
CREATE SCHEMA IF NOT EXISTS audit;

-- Create tables
CREATE TABLE IF NOT EXISTS audit.agent_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id VARCHAR(255) UNIQUE NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    role VARCHAR(255),
    status VARCHAR(50),
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    success BOOLEAN,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trading.transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    side VARCHAR(10) NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    status VARCHAR(50),
    executed_at TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS legal.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id VARCHAR(255) UNIQUE NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    title VARCHAR(500),
    content TEXT,
    status VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS financial.reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id VARCHAR(255) UNIQUE NOT NULL,
    report_type VARCHAR(100) NOT NULL,
    period_start DATE,
    period_end DATE,
    data JSONB,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_agent_executions_status ON audit.agent_executions(status);
CREATE INDEX idx_agent_executions_started_at ON audit.agent_executions(started_at);
CREATE INDEX idx_transactions_symbol ON trading.transactions(symbol);
CREATE INDEX idx_transactions_executed_at ON trading.transactions(executed_at);
CREATE INDEX idx_documents_type ON legal.documents(document_type);
CREATE INDEX idx_reports_type ON financial.reports(report_type);

-- Create views
CREATE OR REPLACE VIEW audit.execution_summary AS
SELECT
    DATE(started_at) as execution_date,
    agent_name,
    COUNT(*) as total_executions,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_executions,
    SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as failed_executions,
    AVG(duration_seconds) as avg_duration_seconds
FROM audit.agent_executions
GROUP BY DATE(started_at), agent_name
ORDER BY execution_date DESC;

EOF

    log_success "Database initialization script created"

    log_info "To initialize database, run:"
    log_info "  psql -U $POSTGRES_USER -d $POSTGRES_DB -f ${PROJECT_ROOT}/scripts/init_database.sql"

    # Create database migration directory
    mkdir -p "${PROJECT_ROOT}/migrations/versions"

    log_success "Database setup completed"
}

################################################################################
# Service Health Checks
################################################################################

perform_health_checks() {
    print_header "Service Health Checks"

    log_info "Performing service health checks..."

    source "$ENV_FILE"

    # Check Python dependencies
    log_info "Checking Python dependencies..."
    if [[ -f "${PROJECT_ROOT}/requirements.txt" ]]; then
        if pip check &> /dev/null; then
            log_success "Python dependencies are satisfied"
        else
            log_warning "Some Python dependencies have issues"
        fi
    fi

    # Check PostgreSQL connection
    if [[ -n "$POSTGRES_HOST" ]] && command -v psql &> /dev/null; then
        log_info "Checking PostgreSQL connection..."
        if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1" &> /dev/null; then
            log_success "PostgreSQL connection successful"
        else
            log_warning "PostgreSQL connection failed (may not be configured yet)"
        fi
    fi

    # Check Redis connection
    if [[ -n "$REDIS_HOST" ]] && command -v redis-cli &> /dev/null; then
        log_info "Checking Redis connection..."
        if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping &> /dev/null; then
            log_success "Redis connection successful"
        else
            log_warning "Redis connection failed (may not be configured yet)"
        fi
    fi

    log_success "Health checks completed"
}

################################################################################
# Security Setup
################################################################################

setup_security() {
    print_header "Security Configuration"

    log_info "Configuring security settings..."

    # Create .gitignore if it doesn't exist
    if [[ ! -f "${PROJECT_ROOT}/.gitignore" ]]; then
        log_info "Creating .gitignore..."

        cat > "${PROJECT_ROOT}/.gitignore" << 'EOF'
# Environment files
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/

# Secrets
secrets/
*.pem
*.key

# Database
*.db
*.sqlite

# OS
.DS_Store
Thumbs.db
EOF

        log_success ".gitignore created"
    fi

    # Set proper permissions
    log_info "Setting file permissions..."
    chmod 600 "$ENV_FILE" || log_warning "Could not set .env permissions"

    log_success "Security configuration completed"
}

################################################################################
# Final Setup Report
################################################################################

generate_setup_report() {
    print_header "Setup Report"

    cat << EOF | tee -a "${SETUP_LOG}"

================================================================================
                        CLOUD ENVIRONMENT SETUP COMPLETE
================================================================================

Configuration Files Created:
  - Environment: ${ENV_FILE}
  - E2B Config: ${PROJECT_ROOT}/e2b.toml
  - Railway Config: ${PROJECT_ROOT}/railway.json
  - Database Schema: ${PROJECT_ROOT}/scripts/init_database.sql

Next Steps:
  1. Update environment variables in: ${ENV_FILE}
  2. Initialize database: psql -f scripts/init_database.sql
  3. Deploy to E2B: e2b sandbox build && e2b sandbox create agentx5-sandbox
  4. Deploy to Railway: railway link && railway up
  5. Start supervisor: python scripts/agentx5_24_7_supervisor.py

Useful Commands:
  - View logs: tail -f logs/*.log
  - Railway status: railway status
  - Railway logs: railway logs
  - E2B status: e2b sandbox list
  - Database: psql -U $POSTGRES_USER -d $POSTGRES_DB

Documentation:
  - E2B: https://e2b.dev/docs
  - Railway: https://docs.railway.app
  - Agent 5.0: ${PROJECT_ROOT}/README.md

Setup Log: ${SETUP_LOG}

================================================================================
EOF

    log_success "Setup report generated"
}

################################################################################
# Main Setup Flow
################################################################################

main() {
    local start_time=$(date '+%Y-%m-%d %H:%M:%S')

    print_banner

    log_info "Starting cloud environment setup..."
    log_info "Start time: $start_time"
    log_info "Project root: $PROJECT_ROOT"
    log_info "Setup log: $SETUP_LOG"

    # Run setup steps
    check_prerequisites || exit 1
    setup_environment_variables || exit 1
    setup_e2b_sandbox || log_warning "E2B setup had issues (non-fatal)"
    setup_railway || log_warning "Railway setup had issues (non-fatal)"
    setup_database || log_warning "Database setup had issues (non-fatal)"
    setup_security || log_warning "Security setup had issues (non-fatal)"
    perform_health_checks || log_warning "Health checks had issues (non-fatal)"

    # Generate report
    generate_setup_report

    log_success "Cloud environment setup completed successfully!"
    log_info "Total time: $(($(date +%s) - $(date -d "$start_time" +%s))) seconds"
}

################################################################################
# Script Entry Point
################################################################################

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --auto-confirm|-y)
            AUTO_CONFIRM=true
            shift
            ;;
        --help|-h)
            cat << EOF
Usage: $0 [OPTIONS]

Options:
  --auto-confirm, -y    Skip confirmation prompts
  --help, -h            Show this help message

Examples:
  $0                    # Interactive setup
  $0 -y                 # Automated setup

EOF
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            log_info "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main setup
main

exit 0
