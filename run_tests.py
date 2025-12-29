#!/usr/bin/env python3
"""
Test runner for StarWeb command tests.
Run all tests or specific test suites.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py parsing            # Run only parsing tests
    python run_tests.py validation         # Run only validation tests
    python run_tests.py execution          # Run only execution tests
    python run_tests.py -v                 # Verbose output
"""
import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import test modules
from tests import test_command_parsing, test_command_validation, test_command_execution


def run_all_tests(verbosity=1):
    """Run all test suites."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test modules
    suite.addTests(loader.loadTestsFromModule(test_command_parsing))
    suite.addTests(loader.loadTestsFromModule(test_command_validation))
    suite.addTests(loader.loadTestsFromModule(test_command_execution))

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_parsing_tests(verbosity=1):
    """Run only parsing tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_command_parsing)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_validation_tests(verbosity=1):
    """Run only validation tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_command_validation)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_execution_tests(verbosity=1):
    """Run only execution tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_command_execution)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    return result.wasSuccessful()


def main():
    """Main test runner."""
    verbosity = 2 if '-v' in sys.argv or '--verbose' in sys.argv else 1

    # Remove flags from argv for test selection
    args = [arg for arg in sys.argv[1:] if not arg.startswith('-')]

    if not args or args[0] == 'all':
        print("Running all tests...\n")
        success = run_all_tests(verbosity)
    elif args[0] == 'parsing':
        print("Running parsing tests...\n")
        success = run_parsing_tests(verbosity)
    elif args[0] == 'validation':
        print("Running validation tests...\n")
        success = run_validation_tests(verbosity)
    elif args[0] == 'execution':
        print("Running execution tests...\n")
        success = run_execution_tests(verbosity)
    else:
        print(f"Unknown test suite: {args[0]}")
        print(__doc__)
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
