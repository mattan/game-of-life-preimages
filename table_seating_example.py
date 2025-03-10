from table_seating_cli import Family, SeatingArrangement

def main():
    """Example showing how to use the table seating optimizer programmatically."""
    # Create some families
    families = [
        Family("Cohen", 4),
        Family("Levy", 2),
        Family("Goldberg", 5),
        Family("Friedman", 3),
        Family("Rosenberg", 6),
        Family("Schwartz", 1),
        Family("Kaplan", 7),
        Family("Weiss", 2),
        Family("Gordon", 4),
        Family("Klein", 3),
        Family("Shapiro", 5),
        Family("Blum", 6),
        Family("Berman", 2),
        Family("Stern", 4),
        Family("Katz", 3),
    ]
    
    # Print the list of families
    print("Families to be seated:")
    for i, family in enumerate(families, 1):
        print(f"{i}. {family}")
    print()
    
    # Calculate the total number of guests
    total_guests = sum(family.size for family in families)
    print(f"Total number of guests: {total_guests}")
    
    # Calculate the minimum number of tables required (simple lower bound)
    table_capacity = 12
    min_tables = (total_guests + table_capacity - 1) // table_capacity
    print(f"Minimum number of tables required (simple calculation): {min_tables}")
    print("Note: The actual number may be higher due to bin packing constraints.")
    print()
    
    # Create the seating arrangement optimizer
    seating = SeatingArrangement(table_capacity=table_capacity)
    
    # Assign families to tables optimally
    print("Finding optimal seating arrangement...")
    seating.assign_families_optimal(families)
    
    # Print the results
    print(seating.get_table_assignments())
    
    # Calculate table utilization
    if seating.tables:
        total_capacity = len(seating.tables) * table_capacity
        utilization = (total_guests / total_capacity) * 100
        print(f"Table utilization: {utilization:.2f}%")


if __name__ == "__main__":
    main() 