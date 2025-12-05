#!/usr/bin/env python3
"""
Test runner script for Pet Health API unit tests
"""
import subprocess
import sys
import os
from pathlib import Path


def is_docker_environment():
    """Check if we're running inside a Docker container"""
    return os.path.exists('/.dockerenv')


def get_environment_info():
    """Get information about the current environment"""
    if is_docker_environment():
        return {
            "type": "docker",
            "api_url": os.getenv("API_BASE_URL", "http://api:8000"),
            "description": "Docker container environment"
        }
    else:
        return {
            "type": "local",
            "api_url": "http://localhost:8000", 
            "description": "Local development environment"
        }


def run_tests():
    """Run the test suite"""
    # Change to the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    env_info = get_environment_info()
    
    print("🧪 Running Pet Health API Unit Tests")
    print("=" * 50)
    print(f"Environment: {env_info['description']}")
    print(f"API URL: {env_info['api_url']}")
    print("=" * 50)
    
    # Set environment variables for tests
    test_env = os.environ.copy()
    test_env["API_BASE_URL"] = env_info["api_url"]
    
    # Basic pytest command
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker checking
        "--asyncio-mode=auto",  # Auto async mode
    ]
    
    try:
        # Run the tests
        result = subprocess.run(cmd, capture_output=False, text=True, env=test_env)
        
        print("\n" + "=" * 50)
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
            
        return result.returncode == 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running tests: {e}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest pytest-asyncio")
        return False


def run_tests_with_coverage():
    """Run tests with coverage reporting"""
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🧪 Running Pet Health API Unit Tests with Coverage")
    print("=" * 60)
    
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--asyncio-mode=auto",
        "--cov=app",  # Coverage for app module
        "--cov-report=html:htmlcov",  # HTML coverage report
        "--cov-report=term-missing",  # Terminal report with missing lines
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        print("\n" + "=" * 60)
        if result.returncode == 0:
            print("✅ All tests passed!")
            print("📊 Coverage report generated in htmlcov/index.html")
        else:
            print("❌ Some tests failed!")
            
        return result.returncode == 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running tests: {e}")
        return False
    except FileNotFoundError:
        print("❌ pytest or pytest-cov not found.")
        print("Install with: pip install pytest pytest-asyncio pytest-cov")
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "pytest",
        "pytest-asyncio", 
        "httpx",
        "sqlalchemy",
        "fastapi"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True


def run_performance_tests():
    """Run performance tests only"""
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🚀 Running Performance Tests")
    print("=" * 40)
    
    cmd = [
        "python", "-m", "pytest",
        "tests/performance/",
        "-v",
        "-m", "performance",
        "--tb=short",
        "--asyncio-mode=auto",
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Performance tests failed: {e}")
        return False


def run_chaos_tests():
    """Run chaos engineering tests"""
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🔥 Running Chaos Engineering Tests")
    print("=" * 45)
    print("⚠️  Warning: These tests will stop/restart Docker containers")
    
    cmd = [
        "python", "-m", "pytest",
        "tests/chaos/",
        "-v",
        "-m", "chaos",
        "--tb=short", 
        "--asyncio-mode=auto",
        "-s",  # Don't capture output for chaos tests
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Chaos tests failed: {e}")
        return False


def run_all_tests_including_performance():
    """Run all tests including performance and chaos tests"""
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🧪 Running Complete Test Suite (Including Performance & Chaos)")
    print("=" * 65)
    
    # Run standard tests first
    success = run_tests()
    if not success:
        print("❌ Standard tests failed, skipping performance tests")
        return False
    
    # Run performance tests
    print("\n" + "=" * 65)
    perf_success = run_performance_tests()
    if not perf_success:
        print("❌ Performance tests failed")
    
    # Ask user before running chaos tests
    print("\n" + "=" * 65)
    print("🔥 Chaos engineering tests will stop/restart Docker containers")
    user_input = input("Run chaos tests? (y/N): ").strip().lower()
    
    chaos_success = True
    if user_input in ['y', 'yes']:
        chaos_success = run_chaos_tests()
    else:
        print("⏭️  Skipping chaos tests")
    
    return success and perf_success and chaos_success


def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == "--coverage":
            # Run with coverage
            if not check_dependencies():
                sys.exit(1)
            
            # Also check for coverage package
            try:
                import coverage
            except ImportError:
                print("❌ pytest-cov not found. Install with: pip install pytest-cov")
                sys.exit(1)
                
            success = run_tests_with_coverage()
            
        elif test_type == "--performance":
            # Run performance tests
            if not check_dependencies():
                sys.exit(1)
            success = run_performance_tests()
            
        elif test_type == "--chaos":
            # Run chaos tests
            if not check_dependencies():
                sys.exit(1)
            success = run_chaos_tests()
            
        elif test_type == "--all":
            # Run all tests including performance and chaos
            if not check_dependencies():
                sys.exit(1)
            success = run_all_tests_including_performance()
            
        else:
            print("❌ Unknown test type. Available options:")
            print("   --coverage    Run tests with coverage")
            print("   --performance Run performance tests")
            print("   --chaos       Run chaos engineering tests")
            print("   --all         Run all tests including performance and chaos")
            sys.exit(1)
    else:
        # Run basic tests
        if not check_dependencies():
            sys.exit(1)
        
        success = run_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()