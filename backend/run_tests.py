#!/usr/bin/env python3
"""
Test runner script for Pet Health API unit tests
"""
import subprocess
import sys
import os
from pathlib import Path


def run_tests():
    """Run the test suite"""
    # Change to the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🧪 Running Pet Health API Unit Tests")
    print("=" * 50)
    
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
        result = subprocess.run(cmd, capture_output=False, text=True)
        
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


def main():
    """Main test runner"""
    if len(sys.argv) > 1 and sys.argv[1] == "--coverage":
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
    else:
        # Run basic tests
        if not check_dependencies():
            sys.exit(1)
        
        success = run_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()