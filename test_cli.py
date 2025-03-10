import unittest
import subprocess
import sys
import os


class TestCommandLineInterface(unittest.TestCase):
    """Test cases for the command-line interface."""
    
    def test_cli_help(self):
        """Test that the CLI provides help information."""
        result = subprocess.run(
            [sys.executable, "table_seating_cli.py", "--help"],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout.lower())
        self.assertIn("table-capacity", result.stdout)
        self.assertIn("families", result.stdout)
        self.assertIn("random", result.stdout)
    
    def test_cli_no_args(self):
        """Test that the CLI requires either --families or --random."""
        result = subprocess.run(
            [sys.executable, "table_seating_cli.py"],
            capture_output=True,
            text=True
        )
        
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("error", (result.stdout + result.stderr).lower())
    
    def test_cli_with_families(self):
        """Test the CLI with specific families."""
        result = subprocess.run(
            [
                sys.executable, 
                "table_seating_cli.py",
                "--families", "Family1:5", "Family2:4", "Family3:3"
            ],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Total tables used:", result.stdout)
        self.assertIn("Family1", result.stdout)
        self.assertIn("Family2", result.stdout)
        self.assertIn("Family3", result.stdout)
    
    def test_cli_with_random(self):
        """Test the CLI with random families."""
        result = subprocess.run(
            [sys.executable, "table_seating_cli.py", "--random", "5"],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Generated random families:", result.stdout)
        self.assertIn("Total tables used:", result.stdout)
    
    def test_cli_with_custom_table_capacity(self):
        """Test the CLI with a custom table capacity."""
        result = subprocess.run(
            [
                sys.executable, 
                "table_seating_cli.py",
                "--table-capacity", "8",
                "--families", "Family1:5", "Family2:4", "Family3:3"
            ],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Occupancy:", result.stdout)
        self.assertIn("/8", result.stdout)  # Table capacity is 8
    
    def test_cli_with_invalid_family(self):
        """Test the CLI with an invalid family specification."""
        result = subprocess.run(
            [
                sys.executable, 
                "table_seating_cli.py",
                "--families", "Family1:5", "InvalidFamily", "Family3:3"
            ],
            capture_output=True,
            text=True
        )
        
        combined_output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("InvalidFamily", combined_output)


if __name__ == "__main__":
    unittest.main() 