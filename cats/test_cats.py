import unittest
from cats import Cats
import time


class TestsCat(unittest.TestCase):
    def test_case1(self):
        c = Cats("""
                 .....
                 .....
                 ...C.
                 ..C..
                 ....M
                """)
        no_of_moves = c.solve()
        self.assertEqual(no_of_moves,3)

    def test_case2(self):
        c = Cats("""
                 .....
                 .....
                 ...CX
                 ..CX.
                 ....M
                """)
        no_of_moves = c.solve()
        self.assertEqual(no_of_moves,4)

    
    def test_case9(self):
        c = Cats("""
                 ..X..
                 ..C..
                 ....X
                 ..CX.
                 ....M
                """)
        no_of_moves = c.solve()
        self.assertEqual(no_of_moves,4)


    
    def test_case10(self):
        c = Cats("""
                 .....
                 ..C..
                 ....X
                 ..CX.
                 ....M
                """)
        no_of_moves = c.solve()
        self.assertEqual(no_of_moves,4)

    def test_case3(self):
        c = Cats("""
                 .....
                 .....
                 ...CX
                 ..CX.
                 ..X.M
                """)
        no_of_moves = c.solve()
        self.assertEqual(no_of_moves,None)

    def test_case4(self):
        c = Cats("""
                 .....
                 ...C.
                 ...XX
                 ..XC.
                 ..X.M
                """)
        no_of_moves = c.solve()
        self.assertEqual(no_of_moves,None)
        
    def test_nodes_update_during_execution(self):
        """Test that nodes are updated progressively during execution."""
        # Create a slightly more complex board to ensure enough states
        c = Cats("""
                 .....
                 .....
                 ...C.
                 ..C..
                 ....M
                """)
        
        # Monkey patch generic_solver to check nodes count at two different points
        original_generic_solver = c.generic_solver
        node_counts = []
        non_inf_counts = []
        
        def patched_generic_solver(*args, **kwargs):
            # Call original but capture node counts during execution
            result = original_generic_solver(*args, **kwargs)
            return result
        
        # Add a checker to the solver function in fast_solver.py
        from solvers.fast_solver import two_steps_solver
        original_two_steps = two_steps_solver
        
        def patched_two_steps(*args, **kwargs):
            # Save the start state of nodes
            visited = args[0]
            print(f"Initial nodes count: {len(visited)}")
            node_counts.append(len(visited))
            
            # Count non-infinite values at start
            non_inf_start = sum(1 for v in visited.values() if v != float('inf') and v is not None)
            non_inf_counts.append(non_inf_start)
            print(f"Initial non-infinite values: {non_inf_start}")
            
            # Wait a bit to allow checking
            time.sleep(0.2)
            
            # Check halfway through 
            original_result = original_two_steps(*args, **kwargs)
            
            # After execution, check again
            print(f"Final nodes count: {len(visited)}")
            node_counts.append(len(visited))
            
            # Count non-infinite values at end
            non_inf_end = sum(1 for v in visited.values() if v != float('inf') and v is not None)
            non_inf_counts.append(non_inf_end)
            print(f"Final non-infinite values: {non_inf_end}")
            
            # Verify that nodes increased during execution
            self.assertGreater(node_counts[1], node_counts[0], 
                             "Number of nodes should increase during solver execution")
            
            # Verify that non-infinite values also increased
            self.assertGreater(non_inf_counts[1], non_inf_counts[0],
                             "Number of non-infinite values should increase during solver execution")
            
            return original_result
        
        # Replace the original function with our patched version
        import solvers.fast_solver
        solvers.fast_solver.two_steps_solver = patched_two_steps
        
        try:
            # Run the solver
            c.solve()
            
            # Perform the assertion again here to make it clear
            self.assertGreater(node_counts[1], node_counts[0],
                             "Number of nodes should increase during solver execution")
            self.assertGreater(non_inf_counts[1], non_inf_counts[0],
                             "Number of non-infinite values should increase during solver execution")
            print(f"PASSED: Nodes increased from {node_counts[0]} to {node_counts[1]} during execution")
            print(f"PASSED: Non-infinite values increased from {non_inf_counts[0]} to {non_inf_counts[1]} during execution")
            
        finally:
            # Restore the original function
            solvers.fast_solver.two_steps_solver = original_two_steps

