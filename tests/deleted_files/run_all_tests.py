#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner for Deleted Files
Runs all tests for files that were deleted in the current branch
"""

import sys
import pytest
from pathlib import Path


def main():
    """Run all test suites"""
    test_dir = Path(__file__).parent
    
    print("=" * 70)
    print("COMPREHENSIVE TEST SUITE FOR DELETED FILES")
    print("=" * 70)
    print()
    print("This test suite validates the functionality of files deleted in")
    print("the current branch, ensuring historical functionality was correct")
    print("and the system remains stable after deletion.")
    print()
    print("Test Files:")
    print("  1. test_scriptable_widgets.py - JavaScript widget tests")
    print("  2. test_azure_workflows.py - Azure Logic Apps workflow tests")
    print("  3. test_transaction_csvs.py - CSV transaction data tests")
    print("  4. test_file_deletion_regression.py - System regression tests")
    print()
    print("=" * 70)
    print()
    
    # Run pytest with verbose output
    test_files = [
        test_dir / "test_scriptable_widgets.py",
        test_dir / "test_azure_workflows.py",
        test_dir / "test_transaction_csvs.py",
        test_dir / "test_file_deletion_regression.py"
    ]
    
    # Filter to only existing files
    existing_tests = [str(f) for f in test_files if f.exists()]
    
    if not existing_tests:
        print("ERROR: No test files found!")
        return 1
    
    # Run with pytest
    args = [
        "-v",  # Verbose
        "--tb=short",  # Short traceback
        "--color=yes",  # Colored output
        "-ra",  # Show summary of all test outcomes
    ] + existing_tests
    
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(main())