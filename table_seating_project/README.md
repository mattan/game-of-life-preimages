# Table Seating Arrangement Application

This application helps optimize table assignments for events, minimizing the number of tables required while ensuring all families are seated properly.

## Features

- Add multiple families with their names and sizes
- Automatically assign families to tables (12 people per table)
- Optimize table usage to minimize the number of tables needed
- View detailed seating arrangements
- Simple, user-friendly interface
- Comprehensive unit tests to verify functionality

## How It Works

The application uses a bin packing algorithm (first-fit decreasing) to efficiently assign families to tables:

1. Families are sorted by size in decreasing order
2. Each family is assigned to the first table that can accommodate it
3. If no existing table has enough space, a new table is created
4. This approach minimizes the total number of tables required

## Using the Application

1. Run the application with `python table_seating.py`
2. Add families by entering a family name and size, then click "Add Family"
3. Continue adding all families that need to be seated
4. Click "Assign Families to Tables" to generate the seating arrangement
5. View the results in the right panel
6. Use "Reset All" to start over if needed

## Running the Tests

To run the unit tests:

```
python -m unittest test_table_seating.py
```

The test suite includes tests for:
- The Family class
- The Table class
- The SeatingArrangement class and its optimization algorithm
- Edge cases like large families and optimal packing scenarios

## Requirements

- Python 3.6 or higher
- Tkinter (included in standard Python installation)

No additional packages are required beyond the Python standard library. 