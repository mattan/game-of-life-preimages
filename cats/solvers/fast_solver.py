"""
Fast solver implementations for the cats game.
"""
from collections import deque

class Node:
    """Node class for representing a game state in the fast solver."""
    def __init__(self, key, turn):
        self.key = key
        self.score = float('inf')
        self.parents = []
        self.children = []
        self.is_updated = False
        self.did_call_get_next_states = False
        self.turn = turn
    
    def update(self):
        """Update the node's score based on its children's scores."""
        expected = max([child.score for child in self.children], default=0) if self.turn == 0 else min([child.score for child in self.children], default=0)
        expected += 1
        if expected != self.score:
            self.is_updated = True
        self.score = expected
    
    def __repr__(self):
        return f"Node(key={self.key}, score={self.score}, is_updated={self.is_updated}, did_call_get_next_states={self.did_call_get_next_states})"

def check_visited_consistency_fast_lifo(visited, get_next_states, board, is_caught):
    """
    Fast solver implementation using LIFO (Last In, First Out) queue.
    
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
    """
    blocks, m, n = board
    return _check_visited_consistency_fast(visited, get_next_states, blocks, m, n, is_caught, use_popleft=False)

def check_visited_consistency_fast_fifo(visited, get_next_states, board, is_caught):
    """
    Fast solver implementation using FIFO (First In, First Out) queue.
    
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
    """
    blocks, m, n = board
    return _check_visited_consistency_fast(visited, get_next_states, blocks, m, n, is_caught, use_popleft=True)

def _check_visited_consistency_fast(visited, get_next_states, blocks, m, n, is_caught, use_popleft=False):
    """
    Helper function implementing the fast solver algorithm.
    
    Parameters:
    -----------
    visited : dict
        Dictionary where keys are states (tuples) and values are scores
    get_next_states : function
        Function that returns possible next states
    blocks : frozenset
        Set of blocked cells
    m : int
        Number of rows in the board
    n : int
        Number of columns in the board
    is_caught : function
        Function that checks if mice are caught
    use_popleft : bool
        If True, uses popleft (FIFO), otherwise uses pop (LIFO)
        
    Returns:
    --------
    dict
        The updated visited dictionary
    """
    # Create a dictionary of nodes
    nodes = {}
    for state in visited.keys():
        turn = state[2]
        node = Node(state, turn)
        nodes[state] = node
    
    # Initialize the queue
    queue = deque(nodes.values())
    
    while queue:
        # Choose whether to use popleft (FIFO) or pop (LIFO)                   
        x = queue.popleft() if use_popleft else queue.pop()
        
        if not x.did_call_get_next_states:
            x.did_call_get_next_states = True
            mice, cats, turn = x.key
            
            if is_caught(mice, cats):
                x.score = 1
                x.is_updated = True
                next_states = []
            else:
                next_states = get_next_states(mice, cats, turn, blocks, m, n)
                
            for y_key in next_states:
                if y_key not in nodes:
                    y_turn = y_key[2]
                    y = Node(y_key, y_turn)
                    nodes[y_key] = y     
                    queue.append(y)  
                else:
                    y = nodes[y_key]
                x.children.append(y)
                y.parents.append(x)
            x.update()

        # Update parents if x was updated
        if x.is_updated:
            x.is_updated = False
            for parent in x.parents:
                parent.update()
                queue.append(parent)

    # Generate result dictionary
    result = {k: node.score for k, node in nodes.items()}
    return result 

def check_visited_consistency_two_steps(visited, get_next_states, board, is_caught):
    """
    Fast solver implementation using a two-step approach:
    1. Build the complete graph
    2. Update scores in a separate pass
    
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
    """
    blocks, m, n = board
    return two_steps_solver(visited, get_next_states, blocks, m, n, is_caught, use_popleft=True)

def two_steps_solver(visited, get_next_states, blocks, m, n, is_caught, use_popleft=True):
    """
    Helper function implementing the fast solver algorithm with two steps:
    1. Build the complete graph
    2. Update scores in a separate pass
    
    Parameters:
    -----------
    visited : dict
        Dictionary where keys are states (tuples) and values are scores
    get_next_states : function
        Function that returns possible next states
    blocks : frozenset
        Set of blocked cells
    m : int
        Number of rows in the board
    n : int
        Number of columns in the board
    is_caught : function
        Function that checks if mice are caught
    use_popleft : bool
        If True, uses popleft (FIFO), otherwise uses pop (LIFO)
        
    Returns:
    --------
    dict
        The updated visited dictionary
    """
    # Create a dictionary of nodes
    nodes = visited
    for state in visited.keys():
        turn = state[2]
        node = Node(state, turn)
        nodes[state] = node
    
    # Initialize the queue
    queue = deque(nodes.values())
    queue_step2 = deque()
    
    while queue:
        # Choose whether to use popleft (FIFO) or pop (LIFO)                   
        x = queue.popleft() if use_popleft else queue.pop()
        
        if not x.did_call_get_next_states:
            x.did_call_get_next_states = True
            mice, cats, turn = x.key
            
            if is_caught(mice, cats):
                x.score = 1
                x.is_updated = True
                next_states = []
                queue_step2.append(x)
            else:
                next_states = get_next_states(mice, cats, turn, blocks, m, n)
                
            for y_key in next_states:
                if y_key not in nodes:
                    y_turn = y_key[2]
                    y = Node(y_key, y_turn)
                    nodes[y_key] = y     
                    queue.append(y)  
                else:
                    y = nodes[y_key]
                x.children.append(y)
                y.parents.append(x)

    while queue_step2:
        x = queue_step2.popleft() if use_popleft else queue_step2.pop()
        # Update parents if x was updated
        if x.is_updated:
            x.is_updated = False
            for parent in x.parents:
                parent.update()
                queue_step2.append(parent)

    # Generate result dictionary
    result = {k: node.score for k, node in nodes.items()}
    return result 