import itertools
from collections import deque
import time

# Import solvers from solvers package
from solvers import ALL_SOLVERS, BEST_SOLVER

class Cats:
    def __init__(self, state):
        self.state = state

    def parse_state(self):
        board = [list(line.strip().replace(' ', '')) for line in self.state.strip().splitlines() if line.strip()]
        if not board:
            return None, None, None, None, None
        n = max(len(row) for row in board)
        m = len(board)
        for row in board:
            while len(row) < n:
                row.append('.')
        cats = []
        mice = []
        blocks = set()
        for y, row in enumerate(board):
            for x, cell in enumerate(row):
                if cell == 'C':
                    cats.append((y, x))
                elif cell == 'M':
                    mice.append((y, x))
                elif cell == 'X':
                    blocks.add((y, x))
        return tuple(sorted(mice)), tuple(sorted(cats)), frozenset(blocks), m, n

    def is_caught(self, mice_pos, cats_pos):
        return bool(set(mice_pos) & set(cats_pos))

    def get_next_states(self, mice_pos, cats_pos, turn, blocks, m, n):
        DIRS = [(-1,0),(1,0),(0,-1),(0,1),(0,0)]
        def in_bounds(y, x):
            return 0 <= y < m and 0 <= x < n
        def is_free(pos, others, blocks):
            # During mice's turn, others = other mice + cats (can't move into either)
            # During cats' turn, others = other cats only (can move into mice's cell)
            return pos not in others and pos not in blocks and in_bounds(*pos)
        next_states = []
        if turn == 0:
            mice_moves = []
            for pos in mice_pos:
                options = []
                for dy, dx in DIRS:
                    ny, nx = pos[0]+dy, pos[1]+dx
                    npos = (ny, nx)
                    # Mice can't move into other mice or cats
                    if is_free(npos, set(mice_pos)-{pos} | set(cats_pos), blocks):
                        options.append(npos)
                mice_moves.append(options)
            for new_mice in itertools.product(*mice_moves):
                if len(set(new_mice)) < len(mice_pos):
                    continue
                # Always flip turn to 1 (cat's turn)
                next_states.append((tuple(sorted(new_mice)), cats_pos, 1))
        else:
            cats_moves = []
            for pos in cats_pos:
                options = []
                for dy, dx in DIRS:
                    ny, nx = pos[0]+dy, pos[1]+dx
                    npos = (ny, nx)
                    # Cats can't move into other cats, but CAN move into mice
                    if is_free(npos, set(cats_pos)-{pos}, blocks):
                        options.append(npos)
                cats_moves.append(options)
            for new_cats in itertools.product(*cats_moves):
                if len(set(new_cats)) < len(cats_pos):
                    continue
                # Always flip turn to 0 (mouse's turn)
                next_states.append((mice_pos, tuple(sorted(new_cats)), 0))
        # Filter out any state that doesn't flip the turn (shouldn't happen, but for safety)
        next_states = [s for s in next_states if s[2] != turn]
        return next_states

    def print_queue_states(self, queue, visited, queue_max_size=10):
        if not hasattr(self, 'iteration_count'):
            self.iteration_count = 0
        self.iteration_count += 1
        if len(queue) > queue_max_size:
            return
        print(f"\n--- Iteration {self.iteration_count+1} ---")
        print("Current queue:")
        for idx, qstate in enumerate(queue):
            mice, cats, turn = qstate
            score = visited.get(qstate, None)
            print(f"  {idx+1}. mice={mice}, cats={cats}, turn={'cat' if turn==1 else 'mouse'}, score={score}")
            # הדפסת כל המהלכים הבאים האפשריים והציון שלהם
            # ננסה לשלוף את blocks, m, n מהמצב הראשון בתור (בהנחה שהם קבועים)
            if hasattr(self, 'parse_state') and hasattr(self, 'get_next_states'):
                # נניח שהאיבר הראשון בתור הוא המצב ההתחלתי, ממנו נוכל לשלוף את blocks, m, n
                # ננסה לשלוף אותם מהאובייקט אם קיימים
                if hasattr(self, 'last_blocks') and hasattr(self, 'last_m') and hasattr(self, 'last_n'):
                    blocks, m, n = self.last_blocks, self.last_m, self.last_n
                else:
                    # ננסה לשלוף מהמצב הראשון בתור
                    try:
                        mice0, cats0, turn0 = qstate
                        # נניח שהאיבר הראשון בתור הוא המצב ההתחלתי
                        mice_init, cats_init, blocks, m, n = self.parse_state()
                        self.last_blocks, self.last_m, self.last_n = blocks, m, n
                    except Exception:
                        blocks, m, n = None, None, None
                if blocks is not None:
                    next_states = self.get_next_states(mice, cats, turn, blocks, m, n)
                    for j, next_state in enumerate(next_states):
                        nmice, ncats, nturn = next_state
                        nscore = visited.get((nmice, ncats, nturn), None)
                        print(f"      -> next {j+1}: mice={nmice}, cats={ncats}, turn={'cat' if nturn==1 else 'mouse'}, score={nscore}")
        print("----------------------")
        
    def generic_solver(self, start_state, get_next_states, is_caught, solvers=None):
        """
        Generic solver that uses multiple solver implementations to find a solution.
        
        Parameters:
        -----------
        start_state : tuple
            A tuple containing (mice_pos, cats_pos, turn, blocks, m, n)
        get_next_states : function
            Function that returns possible next states
        is_caught : function
            Function that checks if mice are caught
        solvers : list
            List of solver functions to use. Each function should accept
            (visited, get_next_states, board, is_caught) as parameters.
            If None, default solvers will be used.
            
        Returns:
        --------
        float
            The solution score, or None if no solution
        """
        # Default solvers if none provided
        if solvers is None:
            solvers = ALL_SOLVERS
        
        queue = deque()
        visited = dict()
        mice_pos, cats_pos, turn, blocks, m, n = start_state
        result_state = (mice_pos, cats_pos, turn)
        visited[result_state] = float('inf')
        
        # Combine blocks, m, n into a board tuple for the solver interface
        board = (blocks, m, n)
        
        # Dictionary to store results from each solver
        results = {}
        durations = {}
        
        # Run each solver and measure time
        for solver_name, solver_func in solvers:
            self.last_visited = visited_copy = visited.copy()
            start_time = time.time()
            
            if solver_name == "slow":
                visited_result, consistency_loops = solver_func(visited_copy, get_next_states, board, is_caught)
                print(f"consistency_loops={consistency_loops}")
            else:
                visited_result = solver_func(visited_copy, get_next_states, board, is_caught)
                
            end_time = time.time()
            duration = end_time - start_time
            
            results[solver_name] = visited_result
            durations[solver_name] = duration
            
            print(f"{solver_name} solver duration: {duration:.4f} seconds")
        
        # Print performance comparisons
        for i, (solver1_name, _) in enumerate(solvers):
            for solver2_name, _ in solvers[i+1:]:
                duration1 = durations[solver1_name]
                duration2 = durations[solver2_name]
                
                if duration1 == 0 or duration2 == 0:
                    print(f"One or both algorithms ({solver1_name}, {solver2_name}) ran too quickly to measure differences (0s)")
                elif duration1 > duration2:
                    print(f"{solver1_name} is slower than {solver2_name} by {(duration1/duration2 - 1)*100:.2f}%")
                else:
                    print(f"{solver1_name} is faster than {solver2_name} by {(duration2/duration1 - 1)*100:.2f}%")
        
        # Check for consistency across results
        result_scores = {name: results[name].get(result_state, float('inf')) for name in results}
        print("\nResults from all solvers:")
        for name, score in result_scores.items():
            print(f"  {name} solver score: {score}")
        
        # Check for inconsistencies
        # Use the slow solver as reference if available, otherwise use the first solver
        reference_name = "slow" if "slow" in result_scores else list(result_scores.keys())[0]
        reference_score = result_scores[reference_name]
        inconsistencies = [name for name, score in result_scores.items() if score != reference_score]
        
        if inconsistencies:
            print(f"\nWARNING: Inconsistencies detected in solvers: {', '.join(inconsistencies)}")
            print(f"Using {reference_name} solver's result ({reference_score}) as the correct one.")
        
        # Store the results from the reference solver
        self.last_visited = results[reference_name]
        
        return (reference_score - 1) / 2

    def solve(self, turn=0):
        """
        Solve the cats game starting with the given turn.
        
        Parameters:
        -----------
        turn : int
            0 for mice's turn, 1 for cats' turn
            
        Returns:
        --------
        float
            The solution score, or None if no solution
        """
        mice, cats, blocks, m, n = self.parse_state()
        start_state = (mice, cats, turn, blocks, m, n)
        
        # Use all available solvers from the solvers package
        result = self.generic_solver(start_state, self.get_next_states, self.is_caught, BEST_SOLVER)

        if result == float('inf'):
            result = None

        print()
        print("testing this board:")
        print(self.state)
        print(f"{result=}")

        return result

    def get_last_visited(self):
        """Return the last visited dictionary from the most recent solver run."""
        visited = getattr(self, 'last_visited', None)
        if visited and '_nodes' in visited:
            # Extract the nodes data and make it available separately
            self._nodes = visited.pop('_nodes')
            # Add any missing states from nodes to visited
            for key, node in self._nodes.items():
                if key not in visited:
                    visited[key] = node.score
        return visited




