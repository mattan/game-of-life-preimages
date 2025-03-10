import unittest
from table_seating_cli import Family, Table, SeatingArrangement


class TestFamily(unittest.TestCase):
    """Test cases for the Family class."""

    def test_family_creation(self):
        """Test that a family can be created with correct attributes."""
        family = Family("Test", 5)
        self.assertEqual(family.name, "Test")
        self.assertEqual(family.size, 5)
    
    def test_family_string_representation(self):
        """Test the string representation of a family."""
        family = Family("Cohen", 4)
        self.assertEqual(str(family), "Cohen (4 people)")
        
        # Test singular form
        family_single = Family("Smith", 1)
        self.assertEqual(str(family_single), "Smith (1 people)")


class TestTable(unittest.TestCase):
    """Test cases for the Table class."""
    
    def test_table_creation(self):
        """Test that a table is created with correct default values."""
        table = Table()
        self.assertEqual(table.capacity, 12)
        self.assertEqual(table.remaining_capacity, 12)
        self.assertEqual(len(table.families), 0)
    
    def test_table_with_custom_capacity(self):
        """Test that a table can be created with a custom capacity."""
        table = Table(capacity=8)
        self.assertEqual(table.capacity, 8)
        self.assertEqual(table.remaining_capacity, 8)
    
    def test_add_family(self):
        """Test adding a family to a table."""
        table = Table()
        family = Family("Test", 5)
        table.add_family(family)
        
        self.assertEqual(len(table.families), 1)
        self.assertEqual(table.families[0].name, "Test")
        self.assertEqual(table.remaining_capacity, 7)
    
    def test_add_multiple_families(self):
        """Test adding multiple families to a table."""
        table = Table()
        families = [Family("Family1", 3), Family("Family2", 2), Family("Family3", 4)]
        
        for family in families:
            table.add_family(family)
        
        self.assertEqual(len(table.families), 3)
        self.assertEqual(table.remaining_capacity, 3)
        self.assertEqual(table.get_total_guests(), 9)
    
    def test_table_overflow(self):
        """Test adding families that exceed the table capacity."""
        table = Table(capacity=10)
        
        # Add families that will fill the table
        table.add_family(Family("Family1", 6))
        table.add_family(Family("Family2", 4))
        
        # Table should be full
        self.assertEqual(table.remaining_capacity, 0)
        
        # Add another family - this will overflow but the method doesn't check capacity
        table.add_family(Family("Family3", 3))
        
        # Table should be overflowed
        self.assertEqual(table.remaining_capacity, -3)
        self.assertEqual(table.get_total_guests(), 13)
    
    def test_get_total_guests(self):
        """Test getting the total number of guests at a table."""
        table = Table()
        
        self.assertEqual(table.get_total_guests(), 0)
        
        table.add_family(Family("Family1", 5))
        self.assertEqual(table.get_total_guests(), 5)
        
        table.add_family(Family("Family2", 3))
        self.assertEqual(table.get_total_guests(), 8)
    
    def test_table_string_representation(self):
        """Test the string representation of a table."""
        table = Table()
        table.add_family(Family("Cohen", 4))
        table.add_family(Family("Levy", 2))
        
        expected_str = "Table (capacity: 12, used: 6, remaining: 6)\nFamilies: Cohen (4 people), Levy (2 people)"
        self.assertEqual(str(table), expected_str)


class TestSeatingArrangement(unittest.TestCase):
    """Test cases for the SeatingArrangement class."""
    
    def test_empty_arrangement(self):
        """Test that a seating arrangement is initialized correctly."""
        arrangement = SeatingArrangement()
        self.assertEqual(arrangement.table_capacity, 12)
        self.assertEqual(len(arrangement.tables), 0)
    
    def test_empty_family_list(self):
        """Test that assigning an empty list of families results in no tables."""
        arrangement = SeatingArrangement()
        arrangement.assign_families_optimal([])
        self.assertEqual(len(arrangement.tables), 0)
    
    def test_single_family_assignment(self):
        """Test assigning a single family to tables."""
        arrangement = SeatingArrangement()
        family = Family("Test", 5)
        
        arrangement.assign_families_optimal([family])
        
        self.assertEqual(len(arrangement.tables), 1)
        self.assertEqual(len(arrangement.tables[0].families), 1)
        self.assertEqual(arrangement.tables[0].families[0].name, "Test")
    
    def test_multiple_families_one_table(self):
        """Test assigning multiple families that can fit in one table."""
        arrangement = SeatingArrangement()
        families = [
            Family("Family1", 3),
            Family("Family2", 4),
            Family("Family3", 2)
        ]
        
        arrangement.assign_families_optimal(families)
        
        self.assertEqual(len(arrangement.tables), 1)
        self.assertEqual(len(arrangement.tables[0].families), 3)
        self.assertEqual(arrangement.tables[0].get_total_guests(), 9)
    
    def test_multiple_families_multiple_tables(self):
        """Test assigning families that require multiple tables."""
        arrangement = SeatingArrangement(table_capacity=10)
        families = [
            Family("Family1", 6),
            Family("Family2", 7),
            Family("Family3", 4),
            Family("Family4", 3)
        ]
        
        arrangement.assign_families_optimal(families)
        
        self.assertEqual(len(arrangement.tables), 2)
        self.assertEqual(arrangement.tables[0].get_total_guests() + 
                        arrangement.tables[1].get_total_guests(), 20)
    
    def test_optimal_packing(self):
        """Test that the optimization produces the minimal number of tables."""
        arrangement = SeatingArrangement(table_capacity=10)
        
        # This set of families can be optimally packed into 2 tables (10+10)
        # but a greedy algorithm would use 3 tables
        families = [
            Family("Family1", 6),  # Table 1
            Family("Family2", 6),  # Table 2
            Family("Family3", 4),  # Could fit with Family1 in an optimal solution
            Family("Family4", 4)   # Could fit with Family2 in an optimal solution
        ]
        
        arrangement.assign_families_optimal(families)
        
        # Optimal solution should use 2 tables
        self.assertEqual(len(arrangement.tables), 2)
        
        # Each table should have 10 people (full capacity)
        self.assertEqual(arrangement.tables[0].get_total_guests(), 10)
        self.assertEqual(arrangement.tables[1].get_total_guests(), 10)
    
    def test_large_family(self):
        """Test a family larger than the table capacity."""
        arrangement = SeatingArrangement(table_capacity=10)
        family = Family("LargeFamily", 15)
        
        # The optimization should still work, but the family won't fit at a single table
        # In a real application, we'd want to validate this before calling the optimizer
        with self.assertRaises(ValueError):
            arrangement.assign_families_optimal([family])
    
    def test_table_assignments_string(self):
        """Test the string representation of table assignments."""
        arrangement = SeatingArrangement()
        families = [
            Family("Family1", 5),
            Family("Family2", 4)
        ]
        
        arrangement.assign_families_optimal(families)
        result = arrangement.get_table_assignments()
        
        # Check that the string contains expected elements
        self.assertIn("Total tables used: 1", result)
        self.assertIn("Table 1:", result)
        self.assertIn("Family1 (5 people)", result)
        self.assertIn("Family2 (4 people)", result)
        self.assertIn("Occupancy: 9/12", result)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios."""
    
    def test_exact_capacity_families(self):
        """Test families that are exactly the table capacity."""
        arrangement = SeatingArrangement(table_capacity=10)
        families = [
            Family("Family1", 10),
            Family("Family2", 10),
            Family("Family3", 10)
        ]
        
        arrangement.assign_families_optimal(families)
        
        self.assertEqual(len(arrangement.tables), 3)
        for table in arrangement.tables:
            self.assertEqual(table.get_total_guests(), 10)
            self.assertEqual(table.remaining_capacity, 0)
    
    def test_many_small_families(self):
        """Test many small families that should be packed efficiently."""
        arrangement = SeatingArrangement(table_capacity=10)
        families = [Family(f"Family{i}", 1) for i in range(20)]  # 20 single-person families
        
        arrangement.assign_families_optimal(families)
        
        # Should use exactly 2 tables
        self.assertEqual(len(arrangement.tables), 2)
        
        # Each table should have 10 families
        self.assertEqual(len(arrangement.tables[0].families) + 
                        len(arrangement.tables[1].families), 20)


if __name__ == "__main__":
    unittest.main() 