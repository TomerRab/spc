#!/usr/bin/env python3
"""
Simple test runner script for the GitLab Project Creator.

To run tests properly, first install the test dependencies:
    pip install -r requirements-test.txt

Then run:
    python run_tests.py

Or use pytest directly:
    pytest

For coverage report:
    pytest --cov=app --cov-report=html
"""

import sys
import subprocess
import os


def main():
    """Run the test suite."""
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ pytest not found. Please install test dependencies:")
        print("   pip install -r requirements-test.txt")
        sys.exit(1)
    
    # Run pytest with configuration
    os.environ["PYTHONPATH"] = os.getcwd()
    
    args = [
        "pytest",
        "-v",
        "--tb=short", 
        "tests/"
    ]
    
    # Add coverage if available
    try:
        import pytest_cov
        args.extend(["--cov=app", "--cov-report=term-missing"])
    except ImportError:
        print("ℹ️  pytest-cov not found, running without coverage")
    
    print("🧪 Running test suite...")
    result = subprocess.run(args)
    
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())