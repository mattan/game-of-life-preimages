"""
This package contains different solvers for the cats game.
"""

from .slow_solver import check_visited_consistency
from .fast_solver import (
    check_visited_consistency_fast_lifo,
    check_visited_consistency_fast_fifo,
    check_visited_consistency_two_steps
)

# Dictionary of all available solvers for easy access
SOLVERS = {
    "slow": check_visited_consistency,
    "fast_lifo": check_visited_consistency_fast_lifo,
    "fast_fifo": check_visited_consistency_fast_fifo,
    "two_steps": check_visited_consistency_two_steps
}

# List of all available solvers as (name, function) tuples
ALL_SOLVERS = list(SOLVERS.items()) 
BEST_SOLVER = [("two_steps", SOLVERS["two_steps"])] 