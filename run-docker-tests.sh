#!/bin/bash

# Docker Test Execution Script
# Runs tests in containerized environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Helper functions
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Configuration
PROJECT_DIR=$(dirname "$(realpath "$0")")
COMPOSE_FILES="-f docker-compose.yml -f docker-compose.test.yml"
TEST_TYPE=${1:-"all"}

# Main function
main() {
    log "🐳 Starting Docker-based Testing Environment"
    log "Project Directory: $PROJECT_DIR"
    log "Test Type: $TEST_TYPE"
    
    cd "$PROJECT_DIR"
    
    # Ensure we have the latest images
    log "🔄 Building and starting services..."
    docker compose $COMPOSE_FILES up -d --build
    
    # Wait for all services to be healthy
    log "⏳ Waiting for services to be ready..."
    sleep 30
    
    # Check if all services are healthy
    if ! docker compose $COMPOSE_FILES ps --services --filter "status=running" | grep -q "api"; then
        error "API service not running"
        docker compose $COMPOSE_FILES logs api
        exit 1
    fi
    
    success "All services are running"
    
    # Create test results directory
    log "📁 Setting up test results directory..."
    mkdir -p ./test-results
    
    # Run tests inside the container
    log "🧪 Executing tests inside Docker container..."
    
    if docker compose $COMPOSE_FILES exec -T api python docker_run_tests.py "$TEST_TYPE"; then
        success "Tests completed successfully"
        exit_code=0
    else
        error "Tests failed"
        exit_code=1
    fi
    
    # Copy test results out of container
    log "📤 Extracting test results..."
    docker compose $COMPOSE_FILES exec -T api test -d /app/test-results && \
    docker compose $COMPOSE_FILES cp api:/app/test-results ./test-results/ || \
    warning "No test results to extract"
    
    # Show quick summary
    echo
    log "🎯 Test Execution Summary:"
    echo "   Check console output above for test results"
    
    # Cleanup (optional)
    if [ "${CLEANUP:-yes}" = "yes" ]; then
        log "🧹 Cleaning up test environment..."
        docker compose $COMPOSE_FILES down --volumes
    else
        log "🔧 Test environment left running for debugging"
        echo "   Use: docker compose $COMPOSE_FILES down --volumes"
    fi
    
    exit $exit_code
}

# Usage information
usage() {
    echo "Usage: $0 [test_type] [options]"
    echo ""
    echo "Test Types:"
    echo "  standard    - Run standard test suite (unit, integration, AI)"
    echo "  performance - Run performance and load tests" 
    echo "  chaos       - Run chaos engineering tests"
    echo "  all         - Run all test suites (default)"
    echo ""
    echo "Environment Variables:"
    echo "  CLEANUP=no  - Skip cleanup after tests (default: yes)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests"
    echo "  $0 standard           # Run standard tests only"
    echo "  CLEANUP=no $0 chaos   # Run chaos tests and leave environment running"
}

# Check for help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
    exit 0
fi

# Run main function
main "$@"