import unittest
from table_seating_cli import Family, parse_family_string


class TestInputValidation(unittest.TestCase):
    """Tests for input validation and handling of invalid inputs."""
    
    def test_family_creation_with_valid_input(self):
        """Test creating a family with valid input."""
        family = Family("Test", 5)
        self.assertEqual(family.name, "Test")
        self.assertEqual(family.size, 5)
    
    def test_family_creation_with_zero_size(self):
        """Test that a family with size 0 can still be created (though it should be validated elsewhere)."""
        family = Family("Test", 0)
        self.assertEqual(family.size, 0)
    
    def test_family_creation_with_negative_size(self):
        """Test that a family with negative size can still be created (though it should be validated elsewhere)."""
        family = Family("Test", -3)
        self.assertEqual(family.size, -3)
    
    def test_parse_family_string_valid(self):
        """Test parsing a valid family string."""
        try:
            family = parse_family_string("Smith:4")
            self.assertEqual(family.name, "Smith")
            self.assertEqual(family.size, 4)
        except SystemExit:
            self.fail("parse_family_string raised SystemExit unexpectedly!")
    
    def test_parse_family_string_invalid_format(self):
        """Test parsing an invalid family string (wrong format)."""
        with self.assertRaises(SystemExit):
            parse_family_string("Smith-4")  # Using - instead of :
    
    def test_parse_family_string_invalid_size(self):
        """Test parsing an invalid family string (non-integer size)."""
        with self.assertRaises(SystemExit):
            parse_family_string("Smith:abc")  # Non-integer size
    
    def test_parse_family_string_negative_size(self):
        """Test parsing a family string with negative size."""
        with self.assertRaises(SystemExit):
            parse_family_string("Smith:-5")  # Negative size
    
    def test_parse_family_string_zero_size(self):
        """Test parsing a family string with zero size."""
        with self.assertRaises(SystemExit):
            parse_family_string("Smith:0")  # Zero size
    
    def test_parse_family_string_missing_parts(self):
        """Test parsing a family string with missing parts."""
        with self.assertRaises(SystemExit):
            parse_family_string("Smith")  # Missing size
    
    def test_parse_family_string_empty_name(self):
        """Test parsing a family string with empty name."""
        # The current implementation doesn't specifically check for empty names,
        # but it should still handle the input without crashing
        family = parse_family_string(":5")
        self.assertEqual(family.name, "")  # Empty name is allowed
        self.assertEqual(family.size, 5)
    
    def test_parse_family_string_too_many_parts(self):
        """Test parsing a family string with too many parts."""
        with self.assertRaises(SystemExit):
            parse_family_string("Smith:5:extra")  # Too many parts


if __name__ == "__main__":
    unittest.main() 