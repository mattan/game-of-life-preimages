# Optimal Table Seating Arrangement

This application solves a table seating optimization problem using Google OR-Tools. The goal is to assign families to tables in an optimal way, minimizing the number of tables used.

## Problem Description

You have:
- A list of families, each with a name and size (number of people)
- Tables with fixed capacity (default: 12 people per table)
- The goal is to assign all families to tables while minimizing the total number of tables used
- Each family must be assigned to exactly one table
- The total number of people at each table cannot exceed the table's capacity

## Solution Approach

This program uses Google OR-Tools' linear solver to model the problem as a bin packing optimization. The mathematical formulation is:

1. **Decision Variables**:
   - x[i,j] = 1 if family i is assigned to table j, 0 otherwise
   - y[j] = 1 if table j is used, 0 otherwise

2. **Constraints**:
   - Each family must be assigned to exactly one table
   - The sum of family sizes at each table cannot exceed the table capacity

3. **Objective Function**:
   - Minimize the total number of tables used

## Installation

1. Install the required dependencies:
```bash
pip install -r table_seating_or_tools_requirements.txt
```

## Usage

Run the application:
```bash
python table_seating_or_tools.py
```

The application features a GUI where you can:
1. Add families with their names and sizes
2. Generate random families for testing
3. Find the optimal assignment of families to tables
4. View the detailed seating arrangement showing which families are assigned to which tables

## Features

- Optimal table assignment using mathematical optimization
- Interactive GUI for data input and result visualization
- Option to generate random test data
- Visual representation of table assignments

## Technical Details

The program is built using:
- Python's Tkinter for the GUI
- Google OR-Tools for solving the optimization problem
- A bin packing approach to minimize resource usage (tables) 