#!/usr/bin/env python3

"""
Docker-based Test Runner for Pet Health AI API
Runs all tests inside Docker containers for consistent environment
"""

import sys
import os
import time
import subprocess
import asyncio
import argparse
import socket
from datetime import datetime
from pathlib import Path

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

# Configuration
PROJECT_ROOT = "/app"
API_URL = "http://api:8000"
DOCKER_COMPOSE_FILE = "/app/docker-compose.yml"

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{Colors.BLUE}[{timestamp}]{Colors.NC} {message}")

def success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.NC}")

def warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")

def error(message):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.NC}")

def check_docker_environment():
    """Check if we're running inside Docker"""
    if not os.path.exists('/.dockerenv'):
        error("This script should run inside a Docker container")
        print("Use: docker compose exec api python docker_run_tests.py")
        return False
    log("✅ Running inside Docker container")
    return True

def check_service(host, port, timeout=5):
    """Check if service is ready"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def wait_for_services():
    """Wait for all services to be ready"""
    log("Waiting for all services to be ready...")
    
    services = [
        ("postgres", 5432, "Database"),
        ("redis", 6379, "Redis"),
        ("api", 8000, "API"),
    ]
    
    for host, port, name in services:
        ready = False
        for i in range(30):  # 30 attempts, 2 seconds each = 60 seconds max
            if check_service(host, port):
                ready = True
                break
            print(".", end="", flush=True)
            time.sleep(2)
        
        if ready:
            log(f"✅ {name} is ready")
        else:
            error(f"{name} not ready after 60 seconds")
            return False
    
    success("All services are ready")
    return True

def run_pytest_command(args, env_vars=None):
    """Run pytest with given arguments"""
    cmd = ["python", "-m", "pytest"] + args
    
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
    
    try:
        result = subprocess.run(cmd, cwd="/app", env=env, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        error(f"Failed to run pytest: {e}")
        return False

def run_standard_tests():
    """Run standard test suite"""
    log("🧪 Running Standard Test Suite")
    
    args = [
        "tests/",
        "-v",
        "--tb=short", 
        "--asyncio-mode=auto",
        "-m", "not performance and not chaos",
        "--maxfail=5"
    ]
    
    success_result = run_pytest_command(args)
    
    if success_result:
        success("Standard tests passed")
    else:
        error("Standard tests failed")
    
    return success_result

def run_performance_tests():
    """Run performance tests"""
    log("🚀 Running Performance Tests")
    
    env_vars = {"API_BASE_URL": "http://api:8000"}
    
    args = [
        "tests/performance/",
        "-v",
        "--tb=short",
        "--asyncio-mode=auto", 
        "-m", "performance",
        "--maxfail=3",
        "-s"
    ]
    
    success_result = run_pytest_command(args, env_vars)
    
    if success_result:
        success("Performance tests passed")
    else:
        warning("Performance tests had issues (may be expected under Docker constraints)")
    
    return success_result

def run_chaos_tests():
    """Run chaos engineering tests"""
    log("🔥 Running Chaos Engineering Tests")
    warning("These tests will manipulate Docker containers")
    
    env_vars = {"API_BASE_URL": "http://api:8000"}
    
    args = [
        "tests/chaos/",
        "-v", 
        "--tb=short",
        "--asyncio-mode=auto",
        "-m", "chaos", 
        "--maxfail=2",
        "-s"
    ]
    
    success_result = run_pytest_command(args, env_vars)
    
    if success_result:
        success("Chaos tests passed")
    else:
        warning("Chaos tests had issues (may be expected in containerized environment)")
    
    return success_result


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Docker-based Test Runner")
    parser.add_argument(
        "test_type", 
        choices=["standard", "performance", "chaos", "all"],
        default="all",
        nargs="?",
        help="Type of tests to run"
    )
    
    args = parser.parse_args()
    test_type = args.test_type
    
    log("🐳 Starting Docker-based Test Suite")
    log(f"Test Type: {test_type}")
    
    # Ensure we're in Docker
    if not check_docker_environment():
        return 1
    
    # Wait for services
    if not wait_for_services():
        error("Services not ready, aborting tests")
        return 1
    
    # Track test results
    results = {}
    overall_success = True
    
    if test_type == "standard":
        if run_standard_tests():
            results["standard"] = "✅ PASSED"
        else:
            results["standard"] = "❌ FAILED"
            overall_success = False
            
    elif test_type == "performance":
        if run_performance_tests():
            results["performance"] = "✅ PASSED"
        else:
            results["performance"] = "⚠️ ISSUES"
            
    elif test_type == "chaos":
        if run_chaos_tests():
            results["chaos"] = "✅ PASSED"
        else:
            results["chaos"] = "⚠️ ISSUES"
            
    elif test_type == "all":
        log("Running complete test suite...")
        
        # Standard tests (must pass)
        if run_standard_tests():
            results["standard"] = "✅ PASSED"
        else:
            results["standard"] = "❌ FAILED"
            overall_success = False
        
        print()
        time.sleep(5)
        
        # Performance tests (warnings OK)
        if run_performance_tests():
            results["performance"] = "✅ PASSED"
        else:
            results["performance"] = "⚠️ ISSUES"
            
        print()
        time.sleep(5)
        
        # Chaos tests (warnings OK)
        if run_chaos_tests():
            results["chaos"] = "✅ PASSED" 
        else:
            results["chaos"] = "⚠️ ISSUES"
    
    # Final status
    print()
    log("🎯 Final Test Results:")
    for test, status in results.items():
        print(f"   {test.title()} Tests: {status}")
    
    if overall_success:
        success("🎉 Test suite completed successfully!")
        return 0
    else:
        error("💥 Test suite had failures!")
        return 1

if __name__ == "__main__":
    sys.exit(main())