#!/usr/bin/env python
"""
Run all tests for the table seating optimization project.
"""

import unittest
import sys


def run_tests():
    """Run all tests for the table seating optimization."""
    # Create a test suite with all the test modules
    test_suite = unittest.TestSuite()
    
    # Unit tests
    unit_tests = unittest.defaultTestLoader.discover('.', pattern='test_table_seating_*.py')
    test_suite.addTest(unit_tests)
    
    # Input validation tests
    input_tests = unittest.defaultTestLoader.loadTestsFromName('test_input_validation')
    test_suite.addTest(input_tests)
    
    # CLI tests
    cli_tests = unittest.defaultTestLoader.loadTestsFromName('test_cli')
    test_suite.addTest(cli_tests)
    
    # Run the tests with a text test runner
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return an exit code based on test results
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests()) 