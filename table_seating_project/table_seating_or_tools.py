import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List, Dict, Tuple
from ortools.linear_solver import pywraplp


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


class SeatingArrangementApp:
    """GUI application for managing table seating arrangements."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Optimal Table Seating Arrangement (OR-Tools)")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        self.families: List[Family] = []
        self.seating_arrangement = SeatingArrangement()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for family input
        left_panel = ttk.LabelFrame(main_frame, text="Add Families", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Family name input
        ttk.Label(left_panel, text="Family Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.family_name_entry = ttk.Entry(left_panel, width=20)
        self.family_name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Family size input
        ttk.Label(left_panel, text="Family Size:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.family_size_entry = ttk.Spinbox(left_panel, from_=1, to=12, width=5)
        self.family_size_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Add family button
        add_button = ttk.Button(left_panel, text="Add Family", command=self.add_family)
        add_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # List of added families
        ttk.Label(left_panel, text="Added Families:").grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.family_listbox = tk.Listbox(left_panel, width=30, height=10)
        self.family_listbox.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Scrollbar for family listbox
        scrollbar = ttk.Scrollbar(left_panel, orient=tk.VERTICAL, command=self.family_listbox.yview)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        self.family_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Remove family button
        remove_button = ttk.Button(left_panel, text="Remove Selected Family", command=self.remove_family)
        remove_button.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Generate random families button
        random_button = ttk.Button(left_panel, text="Generate 10 Random Families", command=self.generate_random_families)
        random_button.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Right panel for seating arrangement
        right_panel = ttk.LabelFrame(main_frame, text="Optimal Seating Arrangement (OR-Tools)", padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Seating arrangement result
        self.arrangement_text = scrolledtext.ScrolledText(right_panel, wrap=tk.WORD, width=40, height=20)
        self.arrangement_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.arrangement_text.config(state=tk.DISABLED)
        
        # Assign button
        assign_button = ttk.Button(right_panel, text="Find Optimal Assignment", command=self.assign_families)
        assign_button.pack(pady=10)
        
        # Reset button
        reset_button = ttk.Button(right_panel, text="Reset All", command=self.reset_all)
        reset_button.pack(pady=5)
        
        # Configure grid weights
        left_panel.columnconfigure(0, weight=1)
        left_panel.columnconfigure(1, weight=1)
        left_panel.rowconfigure(4, weight=1)
    
    def add_family(self):
        """Add a family to the list."""
        name = self.family_name_entry.get().strip()
        
        if not name:
            messagebox.showerror("Input Error", "Please enter a family name.")
            return
        
        try:
            size = int(self.family_size_entry.get())
            if size <= 0:
                raise ValueError("Family size must be positive")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid family size (a positive integer).")
            return
        
        # Add the family to the list
        family = Family(name, size)
        self.families.append(family)
        
        # Update the listbox
        self.family_listbox.insert(tk.END, str(family))
        
        # Clear the input fields
        self.family_name_entry.delete(0, tk.END)
        self.family_size_entry.delete(0, tk.END)
        self.family_size_entry.insert(0, "1")
    
    def remove_family(self):
        """Remove the selected family from the list."""
        selected_indices = self.family_listbox.curselection()
        
        if not selected_indices:
            messagebox.showinfo("No Selection", "Please select a family to remove.")
            return
        
        # Remove in reverse order to avoid index shifting
        for index in sorted(selected_indices, reverse=True):
            del self.families[index]
            self.family_listbox.delete(index)
    
    def generate_random_families(self):
        """Generate 10 random families for testing."""
        import random
        
        # Clear existing families
        self.families = []
        self.family_listbox.delete(0, tk.END)
        
        # Generate random families
        family_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", 
                        "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", 
                        "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson"]
        
        for i in range(10):
            name = random.choice(family_names) + f"_{i+1}"
            size = random.randint(1, 8)  # Random size between 1 and 8
            family = Family(name, size)
            self.families.append(family)
            self.family_listbox.insert(tk.END, str(family))
    
    def assign_families(self):
        """Assign families to tables optimally and display the result."""
        if not self.families:
            messagebox.showinfo("No Families", "Please add at least one family before assigning tables.")
            return
        
        try:
            # Assign families to tables optimally
            self.seating_arrangement = SeatingArrangement()
            self.seating_arrangement.assign_families_optimal(self.families)
            
            # Display the result
            self.arrangement_text.config(state=tk.NORMAL)
            self.arrangement_text.delete(1.0, tk.END)
            self.arrangement_text.insert(tk.END, self.seating_arrangement.get_table_assignments())
            self.arrangement_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def reset_all(self):
        """Reset the application state."""
        self.families = []
        self.family_listbox.delete(0, tk.END)
        self.arrangement_text.config(state=tk.NORMAL)
        self.arrangement_text.delete(1.0, tk.END)
        self.arrangement_text.config(state=tk.DISABLED)
        self.family_name_entry.delete(0, tk.END)
        self.family_size_entry.delete(0, tk.END)
        self.family_size_entry.insert(0, "1")


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = SeatingArrangementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main() 