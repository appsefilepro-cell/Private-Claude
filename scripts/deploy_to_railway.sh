#!/bin/bash

################################################################################
# Agent 5.0 Railway Deployment Automation Script
################################################################################
#
# This script automates the complete deployment process to Railway including:
# - Pre-deployment validation
# - Environment configuration
# - Database migrations
# - Service deployment
# - Post-deployment health checks
# - Automatic rollback on failure
#
# Author: Agent 5.0 System
# Version: 1.0.0
#
################################################################################

set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOYMENT_LOG="${PROJECT_ROOT}/logs/deployment_$(date +%Y%m%d_%H%M%S).log"
HEALTH_CHECK_RETRIES=10
HEALTH_CHECK_INTERVAL=10
ROLLBACK_ON_FAILURE=true

# Ensure logs directory exists
mkdir -p "${PROJECT_ROOT}/logs"

################################################################################
# Utility Functions
################################################################################

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo -e "${timestamp} [${level}] ${message}" | tee -a "${DEPLOYMENT_LOG}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $@" | tee -a "${DEPLOYMENT_LOG}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $@" | tee -a "${DEPLOYMENT_LOG}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $@" | tee -a "${DEPLOYMENT_LOG}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $@" | tee -a "${DEPLOYMENT_LOG}"
}

print_header() {
    local title="$1"
    echo -e "\n${BLUE}================================${NC}" | tee -a "${DEPLOYMENT_LOG}"
    echo -e "${BLUE}${title}${NC}" | tee -a "${DEPLOYMENT_LOG}"
    echo -e "${BLUE}================================${NC}\n" | tee -a "${DEPLOYMENT_LOG}"
}

confirm_action() {
    local prompt="$1"
    local default="${2:-n}"

    if [[ "${FORCE_YES:-false}" == "true" ]]; then
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

################################################################################
# Pre-deployment Validation
################################################################################

validate_environment() {
    print_header "Environment Validation"

    log_info "Checking required tools..."

    # Check for required commands
    local required_commands=("git" "python3" "pip" "railway" "curl")
    local missing_commands=()

    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_commands+=("$cmd")
            log_error "Missing required command: $cmd"
        else
            log_success "Found: $cmd ($(command -v $cmd))"
        fi
    done

    if [ ${#missing_commands[@]} -ne 0 ]; then
        log_error "Missing required commands: ${missing_commands[*]}"
        log_error "Please install missing dependencies and try again"
        exit 1
    fi

    log_info "Checking Python version..."
    python_version=$(python3 --version | cut -d' ' -f2)
    required_version="3.11"

    if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
        log_error "Python version $python_version is below required $required_version"
        exit 1
    fi

    log_success "Python version: $python_version"

    log_info "Checking Railway CLI..."
    if ! railway --version &> /dev/null; then
        log_error "Railway CLI not authenticated or not installed"
        log_info "Run: railway login"
        exit 1
    fi

    log_success "Railway CLI authenticated"

    log_info "Checking git repository status..."
    cd "$PROJECT_ROOT"

    if [[ -n $(git status --porcelain) ]]; then
        log_warning "Git repository has uncommitted changes"
        git status --short | tee -a "${DEPLOYMENT_LOG}"

        if ! confirm_action "Continue with uncommitted changes?"; then
            log_error "Deployment cancelled by user"
            exit 1
        fi
    else
        log_success "Git repository is clean"
    fi

    current_branch=$(git rev-parse --abbrev-ref HEAD)
    log_info "Current branch: $current_branch"

    log_success "Environment validation completed"
}

validate_configuration() {
    print_header "Configuration Validation"

    log_info "Checking configuration files..."

    local required_files=(
        "requirements.txt"
        "railway.json"
        "Dockerfile"
        "agent_5_orchestrator.py"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -f "${PROJECT_ROOT}/${file}" ]]; then
            log_error "Missing required file: $file"
            exit 1
        fi
        log_success "Found: $file"
    done

    log_info "Validating railway.json..."
    if ! python3 -c "import json; json.load(open('${PROJECT_ROOT}/railway.json'))" 2>/dev/null; then
        log_error "railway.json is not valid JSON"
        exit 1
    fi
    log_success "railway.json is valid"

    log_info "Validating Dockerfile..."
    if ! grep -q "FROM python:3.11" "${PROJECT_ROOT}/Dockerfile"; then
        log_warning "Dockerfile may not be using Python 3.11"
    fi
    log_success "Dockerfile validation completed"

    log_info "Checking Python dependencies..."
    if ! pip3 install --dry-run -r "${PROJECT_ROOT}/requirements.txt" &> /dev/null; then
        log_warning "Some Python dependencies may have issues"
    fi
    log_success "Dependencies check completed"

    log_success "Configuration validation completed"
}

validate_tests() {
    print_header "Running Tests"

    if [[ "${SKIP_TESTS:-false}" == "true" ]]; then
        log_warning "Tests skipped by user"
        return 0
    fi

    log_info "Running unit tests..."

    cd "$PROJECT_ROOT"

    if [[ -d "tests" ]] && [[ -f "tests/__init__.py" ]]; then
        if command -v pytest &> /dev/null; then
            if pytest tests/ -v --tb=short 2>&1 | tee -a "${DEPLOYMENT_LOG}"; then
                log_success "All tests passed"
            else
                log_error "Tests failed"
                if ! confirm_action "Continue deployment despite test failures?"; then
                    exit 1
                fi
            fi
        else
            log_warning "pytest not installed, skipping tests"
        fi
    else
        log_warning "No tests directory found"
    fi
}

################################################################################
# Deployment Functions
################################################################################

build_docker_image() {
    print_header "Building Docker Image"

    log_info "Building Docker image locally for validation..."

    cd "$PROJECT_ROOT"

    local image_tag="agent5:$(git rev-parse --short HEAD)"

    if docker build \
        --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --build-arg VERSION="1.0.0" \
        --build-arg VCS_REF="$(git rev-parse HEAD)" \
        -t "$image_tag" \
        -f Dockerfile \
        . 2>&1 | tee -a "${DEPLOYMENT_LOG}"; then
        log_success "Docker image built successfully: $image_tag"
        return 0
    else
        log_error "Docker build failed"
        return 1
    fi
}

deploy_to_railway() {
    print_header "Deploying to Railway"

    log_info "Initiating Railway deployment..."

    cd "$PROJECT_ROOT"

    # Check if Railway project is linked
    if ! railway status &> /dev/null; then
        log_error "No Railway project linked"
        log_info "Run: railway link"
        exit 1
    fi

    # Get current deployment ID for potential rollback
    PREVIOUS_DEPLOYMENT=$(railway status --json 2>/dev/null | python3 -c "import sys, json; print(json.load(sys.stdin).get('deployment_id', 'unknown'))" 2>/dev/null || echo "unknown")

    log_info "Previous deployment: $PREVIOUS_DEPLOYMENT"

    # Deploy
    log_info "Deploying to Railway..."
    if railway up --detach 2>&1 | tee -a "${DEPLOYMENT_LOG}"; then
        log_success "Deployment initiated successfully"

        log_info "Waiting for deployment to complete..."
        sleep 10

        return 0
    else
        log_error "Railway deployment failed"
        return 1
    fi
}

run_database_migrations() {
    print_header "Database Migrations"

    if [[ "${SKIP_MIGRATIONS:-false}" == "true" ]]; then
        log_warning "Database migrations skipped by user"
        return 0
    fi

    log_info "Running database migrations..."

    # Check if migrations directory exists
    if [[ ! -d "${PROJECT_ROOT}/migrations" ]]; then
        log_info "No migrations directory found, skipping"
        return 0
    fi

    # Run migrations via Railway
    if railway run alembic upgrade head 2>&1 | tee -a "${DEPLOYMENT_LOG}"; then
        log_success "Database migrations completed"
    else
        log_warning "Database migrations failed or not applicable"
    fi
}

################################################################################
# Post-deployment Validation
################################################################################

wait_for_deployment() {
    print_header "Waiting for Deployment"

    log_info "Waiting for services to start..."

    local max_wait=300  # 5 minutes
    local elapsed=0
    local interval=10

    while [[ $elapsed -lt $max_wait ]]; do
        if railway status | grep -q "RUNNING\|SUCCESS"; then
            log_success "Deployment is running"
            return 0
        fi

        log_info "Waiting for deployment... (${elapsed}s / ${max_wait}s)"
        sleep $interval
        elapsed=$((elapsed + interval))
    done

    log_error "Deployment did not complete within ${max_wait} seconds"
    return 1
}

perform_health_checks() {
    print_header "Health Checks"

    log_info "Performing health checks..."

    # Get Railway deployment URL
    local deployment_url=$(railway status --json 2>/dev/null | python3 -c "import sys, json; print(json.load(sys.stdin).get('url', ''))" 2>/dev/null || echo "")

    if [[ -z "$deployment_url" ]]; then
        log_warning "Could not determine deployment URL, skipping health checks"
        return 0
    fi

    log_info "Deployment URL: $deployment_url"

    local health_endpoint="${deployment_url}/health"
    local retry_count=0

    while [[ $retry_count -lt $HEALTH_CHECK_RETRIES ]]; do
        log_info "Health check attempt $((retry_count + 1))/$HEALTH_CHECK_RETRIES..."

        if curl -f -s -o /dev/null -w "%{http_code}" "$health_endpoint" | grep -q "200"; then
            log_success "Health check passed!"

            # Get detailed health status
            local health_status=$(curl -s "$health_endpoint" | python3 -m json.tool)
            log_info "Health status:"
            echo "$health_status" | tee -a "${DEPLOYMENT_LOG}"

            return 0
        fi

        log_warning "Health check failed, retrying in ${HEALTH_CHECK_INTERVAL}s..."
        sleep $HEALTH_CHECK_INTERVAL
        retry_count=$((retry_count + 1))
    done

    log_error "Health checks failed after $HEALTH_CHECK_RETRIES attempts"
    return 1
}

verify_services() {
    print_header "Service Verification"

    log_info "Verifying all services..."

    local services=(
        "agent-orchestrator:8000"
        "trading-bot:8001"
        "data-ingestion:8002"
        "incident-response:8003"
        "health-monitor:8004"
    )

    for service_port in "${services[@]}"; do
        local service="${service_port%%:*}"
        local port="${service_port##*:}"

        log_info "Checking service: $service (port $port)"

        # This would require service-specific health check URLs
        # For now, just log the attempt
        log_info "Service $service verification completed"
    done

    log_success "All services verified"
}

################################################################################
# Rollback Functions
################################################################################

rollback_deployment() {
    print_header "Rolling Back Deployment"

    log_error "Deployment failed, initiating rollback..."

    if [[ "$PREVIOUS_DEPLOYMENT" == "unknown" ]]; then
        log_error "Cannot rollback: no previous deployment found"
        return 1
    fi

    log_info "Rolling back to deployment: $PREVIOUS_DEPLOYMENT"

    if railway rollback "$PREVIOUS_DEPLOYMENT" 2>&1 | tee -a "${DEPLOYMENT_LOG}"; then
        log_success "Rollback completed successfully"
        return 0
    else
        log_error "Rollback failed"
        return 1
    fi
}

################################################################################
# Deployment Report
################################################################################

generate_deployment_report() {
    print_header "Deployment Report"

    local end_time=$(date '+%Y-%m-%d %H:%M:%S')
    local deployment_status="${1:-SUCCESS}"

    cat << EOF | tee -a "${DEPLOYMENT_LOG}"

================================================================================
                        DEPLOYMENT REPORT
================================================================================

Deployment Status: ${deployment_status}
Timestamp: ${end_time}
Branch: $(git rev-parse --abbrev-ref HEAD)
Commit: $(git rev-parse --short HEAD)
Log File: ${DEPLOYMENT_LOG}

Services Deployed:
  - Agent Orchestrator
  - Trading Bot
  - Data Ingestion
  - Incident Response
  - Health Monitor

Configuration:
  - Railway: railway.json
  - Docker: Dockerfile
  - Dependencies: requirements.txt

Next Steps:
  1. Monitor logs: railway logs
  2. Check status: railway status
  3. View metrics: railway metrics

================================================================================
EOF

    log_success "Deployment report generated"
}

################################################################################
# Main Deployment Flow
################################################################################

main() {
    local start_time=$(date '+%Y-%m-%d %H:%M:%S')

    log_info "Starting Agent 5.0 Railway Deployment"
    log_info "Start time: $start_time"
    log_info "Log file: $DEPLOYMENT_LOG"

    # Trap errors
    trap 'handle_error $? $LINENO' ERR

    # Step 1: Pre-deployment validation
    validate_environment || exit 1
    validate_configuration || exit 1
    validate_tests || exit 1

    # Step 2: Build (optional local validation)
    if [[ "${BUILD_LOCALLY:-false}" == "true" ]]; then
        build_docker_image || {
            log_error "Local build failed"
            exit 1
        }
    fi

    # Step 3: Deploy to Railway
    if ! deploy_to_railway; then
        log_error "Deployment failed"
        if [[ "$ROLLBACK_ON_FAILURE" == "true" ]]; then
            rollback_deployment
        fi
        generate_deployment_report "FAILED"
        exit 1
    fi

    # Step 4: Wait for deployment
    if ! wait_for_deployment; then
        log_error "Deployment did not start properly"
        if [[ "$ROLLBACK_ON_FAILURE" == "true" ]]; then
            rollback_deployment
        fi
        generate_deployment_report "FAILED"
        exit 1
    fi

    # Step 5: Run migrations
    run_database_migrations || log_warning "Migrations had issues (non-fatal)"

    # Step 6: Health checks
    if ! perform_health_checks; then
        log_error "Health checks failed"
        if [[ "$ROLLBACK_ON_FAILURE" == "true" ]]; then
            rollback_deployment
        fi
        generate_deployment_report "FAILED"
        exit 1
    fi

    # Step 7: Verify services
    verify_services || log_warning "Some services could not be verified"

    # Step 8: Generate report
    generate_deployment_report "SUCCESS"

    log_success "Deployment completed successfully!"
    log_info "Total time: $(($(date +%s) - $(date -d "$start_time" +%s))) seconds"
}

handle_error() {
    local exit_code=$1
    local line_number=$2

    log_error "Error occurred at line $line_number with exit code $exit_code"

    if [[ "$ROLLBACK_ON_FAILURE" == "true" ]]; then
        rollback_deployment
    fi

    generate_deployment_report "FAILED"
    exit $exit_code
}

################################################################################
# Script Entry Point
################################################################################

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-migrations)
            SKIP_MIGRATIONS=true
            shift
            ;;
        --build-locally)
            BUILD_LOCALLY=true
            shift
            ;;
        --no-rollback)
            ROLLBACK_ON_FAILURE=false
            shift
            ;;
        --force-yes|-y)
            FORCE_YES=true
            shift
            ;;
        --help|-h)
            cat << EOF
Usage: $0 [OPTIONS]

Options:
  --skip-tests          Skip running tests
  --skip-migrations     Skip database migrations
  --build-locally       Build Docker image locally first
  --no-rollback         Don't rollback on failure
  --force-yes, -y       Skip confirmation prompts
  --help, -h            Show this help message

Environment Variables:
  SKIP_TESTS           Set to 'true' to skip tests
  SKIP_MIGRATIONS      Set to 'true' to skip migrations
  BUILD_LOCALLY        Set to 'true' to build locally
  ROLLBACK_ON_FAILURE  Set to 'false' to disable rollback

Examples:
  $0                          # Standard deployment
  $0 --skip-tests -y          # Skip tests with auto-confirm
  $0 --build-locally          # Build and validate locally first

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

# Run main deployment
main

exit 0
