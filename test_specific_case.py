import unittest
from table_seating_cli import Family, SeatingArrangement


class TestSpecificCase(unittest.TestCase):
    """Test case for a specific configuration of family sizes."""
    
    def test_specific_family_sizes(self):
        """Test the number of tables needed for the specific family sizes [8,8,3,3,2,2,2,2,2,2,2]."""
        # Create families with the specified sizes
        family_sizes = [8, 8, 3, 3, 2, 2, 2, 2, 2, 2, 2]
        families = [Family(f"Family{i+1}", size) for i, size in enumerate(family_sizes)]
        
        # Calculate the total number of people
        total_people = sum(family_sizes)
        print(f"Total number of people: {total_people}")
        
        # Calculate theoretical minimum based on total people
        table_capacity = 12
        theoretical_min_tables = (total_people + table_capacity - 1) // table_capacity
        print(f"Theoretical minimum tables needed: {theoretical_min_tables}")
        
        # Use our optimal algorithm to find the actual number of tables needed
        seating = SeatingArrangement(table_capacity=table_capacity)
        seating.assign_families_optimal(families)
        
        # Get the actual number of tables used
        actual_tables = len(seating.tables)
        print(f"Actual tables needed with optimal assignment: {actual_tables}")
        
        # Print the detailed assignment
        print("\nDetailed assignment:")
        print(seating.get_table_assignments())
        
        # Assert that the number of tables is at least the theoretical minimum
        self.assertGreaterEqual(actual_tables, theoretical_min_tables)
        
        # Print utilization
        utilization = (total_people / (actual_tables * table_capacity)) * 100
        print(f"Table utilization: {utilization:.2f}%")


if __name__ == "__main__":
    unittest.main() 