#!/usr/bin/env python3
"""
Test runner for the MCP adapter project.

This script runs unit tests and reports code coverage.
"""

import unittest
import coverage
import sys
import os
from pathlib import Path

def run_tests_with_coverage():
    """Run tests with coverage measurement."""
    # Start coverage measurement
    cov = coverage.Coverage(
        source=['src'],
        omit=[
            '*/tests/*',
            '*/site-packages/*',
            '*/__pycache__/*',
            '*/dist/*',
            '*/build/*',
        ],
    )
    cov.start()

    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests')
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Stop coverage measurement
    cov.stop()
    cov.save()

    # Report coverage
    print("\nCoverage Report:")
    cov.report()
    
    # Create HTML report
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    cov.html_report(directory=reports_dir / 'coverage_html')
    print(f"\nHTML coverage report saved to: {reports_dir / 'coverage_html/index.html'}")

    # Return test result status
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs('reports', exist_ok=True)
    
    # Run tests with coverage
    sys.exit(run_tests_with_coverage())