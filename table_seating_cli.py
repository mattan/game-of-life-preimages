from typing import List, Dict, Tuple
from ortools.linear_solver import pywraplp
import random
import argparse
import sys


class Family:
    """Class representing a family with a name and size."""
    
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size
    
    def __str__(self) -> str:
        return f"{self.name} ({self.size} people)"


class Table:
    """Class representing a table with assigned families."""
    
    def __init__(self, capacity: int = 12):
        self.capacity = capacity
        self.remaining_capacity = capacity
        self.families: List[Family] = []
    
    def add_family(self, family: Family) -> None:
        """Add a family to the table."""
        self.families.append(family)
        self.remaining_capacity -= family.size
    
    def get_total_guests(self) -> int:
        """Get the total number of guests at this table."""
        return self.capacity - self.remaining_capacity
    
    def __str__(self) -> str:
        """String representation of the table."""
        families_str = ", ".join(str(family) for family in self.families)
        return f"Table (capacity: {self.capacity}, used: {self.get_total_guests()}, remaining: {self.remaining_capacity})\n" \
               f"Families: {families_str}"


class SeatingArrangement:
    """Class to manage the seating arrangement for families using OR-Tools."""
    
    def __init__(self, table_capacity: int = 12):
        self.table_capacity = table_capacity
        self.tables: List[Table] = []
    
    def assign_families_optimal(self, families: List[Family]) -> None:
        """Assign families to tables using OR-Tools for optimal bin packing."""
        # If no families, nothing to do
        if not families:
            return
        
        # Create the solver
        solver = pywraplp.Solver.CreateSolver('CBC')
        if not solver:
            raise ValueError("Could not create solver")
        
        num_families = len(families)
        # Maximum number of tables we might need is equal to the number of families
        max_tables = num_families
        
        # Decision variables
        # x[i][j] = 1 if family i is assigned to table j
        x = {}
        for i in range(num_families):
            for j in range(max_tables):
                x[i, j] = solver.BoolVar(f'x_{i}_{j}')
        
        # y[j] = 1 if table j is used
        y = {}
        for j in range(max_tables):
            y[j] = solver.BoolVar(f'y_{j}')
        
        # Constraint: Each family must be assigned to exactly one table
        for i in range(num_families):
            solver.Add(sum(x[i, j] for j in range(max_tables)) == 1)
        
        # Constraint: The sum of family sizes at each table cannot exceed the table capacity
        for j in range(max_tables):
            solver.Add(
                sum(families[i].size * x[i, j] for i in range(num_families)) <= self.table_capacity * y[j]
            )
        
        # Objective: Minimize the number of tables used
        solver.Minimize(sum(y[j] for j in range(max_tables)))
        
        # Solve the problem
        status = solver.Solve()
        
        # Check if a solution was found
        if status == pywraplp.Solver.OPTIMAL:
            # Create tables based on the solution
            for j in range(max_tables):
                if y[j].solution_value() > 0.5:  # Table is used
                    table = Table(self.table_capacity)
                    self.tables.append(table)
                    
                    # Assign families to this table
                    for i in range(num_families):
                        if x[i, j].solution_value() > 0.5:  # Family i is assigned to table j
                            table.add_family(families[i])
        else:
            raise ValueError("The solver could not find an optimal solution.")
    
    def get_table_assignments(self) -> str:
        """Get a formatted string of all table assignments."""
        if not self.tables:
            return "No tables assigned yet."
        
        result = f"Total tables used: {len(self.tables)}\n\n"
        for i, table in enumerate(self.tables, 1):
            result += f"Table {i}:\n"
            result += f"  Occupancy: {table.get_total_guests()}/{table.capacity}\n"
            result += "  Families:\n"
            for family in table.families:
                result += f"    - {family}\n"
            result += "\n"
        
        return result


def generate_random_families(num_families: int, max_family_size: int = 8) -> List[Family]:
    """Generate random families for testing."""
    family_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", 
                    "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", 
                    "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson"]
    
    families = []
    for i in range(num_families):
        name = random.choice(family_names) + f"_{i+1}"
        size = random.randint(1, max_family_size)
        families.append(Family(name, size))
    
    return families


def parse_family_string(family_str: str) -> Family:
    """Parse a family string in the format 'name:size'."""
    try:
        name, size_str = family_str.split(':')
        size = int(size_str)
        if size <= 0:
            raise ValueError("Family size must be positive")
        return Family(name, size)
    except ValueError as e:
        print(f"Error parsing family '{family_str}': {e}")
        print("Format should be 'name:size' where size is a positive integer.")
        sys.exit(1)


def main():
    """Main entry point for the command-line application."""
    parser = argparse.ArgumentParser(description='Optimize seating arrangements for families at tables.')
    parser.add_argument('--table-capacity', type=int, default=12,
                        help='Maximum capacity of each table (default: 12)')
    parser.add_argument('--families', nargs='+', metavar='NAME:SIZE',
                        help='List of families in the format "name:size" (e.g., "Smith:4")')
    parser.add_argument('--random', type=int, metavar='NUM',
                        help='Generate random data with the specified number of families')
    parser.add_argument('--max-size', type=int, default=8,
                        help='Maximum family size for random generation (default: 8)')
    
    args = parser.parse_args()
    
    # Get families
    families = []
    if args.families:
        families = [parse_family_string(f) for f in args.families]
    elif args.random:
        families = generate_random_families(args.random, args.max_size)
        print("Generated random families:")
        for family in families:
            print(f"- {family}")
        print()
    else:
        parser.print_help()
        print("\nError: Either --families or --random must be provided.")
        sys.exit(1)
    
    # Create and run the optimizer
    seating = SeatingArrangement(table_capacity=args.table_capacity)
    try:
        seating.assign_families_optimal(families)
        print(seating.get_table_assignments())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 