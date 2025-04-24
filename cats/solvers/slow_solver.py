"""
Slow solver implementation for the cats game.
"""

def check_visited_consistency(visited, get_next_states, board, is_caught):
    """
    Checks and corrects for each state in visited whether its value is indeed the maximum/minimum
    of all next states (if they all exist in visited).
    Continues in a loop until there are no more inconsistencies.
    Counts how many iterations were required.
    
    Parameters:
    -----------
    visited : dict
        Dictionary where keys are states (tuples) and values are scores
    get_next_states : function
        Function that returns possible next states
    board : tuple
        A tuple containing (blocks, m, n) representing the game board
    is_caught : function
        Function that checks if mice are caught
        
    Returns:
    --------
    dict
        The updated visited dictionary
    int
        Number of consistency loops performed
    """
    blocks, m, n = board
    consistency_loops = 0
    fixed = True
    while fixed:
        consistency_loops += 1
        fixed = False
        for state, score in list(visited.items()):
            mice, cats, turn = state
            if is_caught(mice, cats):
                if score != 1:
                    visited[state] = 1
                    fixed = True
                continue
            next_states = get_next_states(mice, cats, turn, blocks, m, n)
            next_scores = []
            all_in_visited = True
            for next_state in next_states:
                nmice, ncats, nturn = next_state
                nstate = (nmice, ncats, nturn)
                if nstate in visited:
                    next_scores.append(visited[nstate])
                else:
                    visited[nstate] = float('inf')  # Add missing states
                    fixed = True
                    all_in_visited = False
            if not all_in_visited or not next_scores:
                continue  # Do not check incomplete states
            expected = max(next_scores) if turn == 0 else min(next_scores)
            expected += 1
            if score != expected:
                visited[state] = expected
                fixed = True
    
    return visited, consistency_loops 