import itertools
from collections import deque
import tkinter as tk


class Cats:
    def __init__(self, state):
        self.state = state
        self.turn = tk.IntVar(value=0)

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
        
    def generic_solver(self, start_state, get_next_states, is_caught):
        from collections import deque
        queue = deque()
        self.last_visited = visited = dict()
        mice_pos, cats_pos, turn, blocks, m, n = start_state
        result_state = (mice_pos, cats_pos, turn)
        queue.append((mice_pos, cats_pos, turn))

        while queue:
            #self.print_queue_states(queue, visited)
            mice_pos, cats_pos, turn = queue.pop()
            state = (mice_pos, cats_pos, turn)
            visited[state] = float('inf')
            if is_caught(mice_pos, cats_pos):
                score = 0
            else:
                #print(f"{len(visited)=} {len(queue)=}")
                next_scores = []
                all_next_known = True
                queue.append((mice_pos, cats_pos, turn))
                for next_state in get_next_states(mice_pos, cats_pos, turn, blocks, m, n):
                    nmice, ncats, nturn = next_state
                    nstate = (nmice, ncats, nturn)
                    if nstate in visited:
                        next_scores.append(visited[nstate])
                    else:
                        all_next_known = False
                        queue.append((nmice, ncats, nturn))
                if not all_next_known:
                    score = float('inf')
                else:
                    queue.pop()
                    if turn == 1:  # תור החתול - רוצה מינימום
                        score = min(next_scores)
                    else:  # תור העכבר - רוצה מקסימום
                        score = max(next_scores)
            visited[state] = score + 1

        # After computing the result, print the optimal path if result is not infinity
        result_score = visited.get(result_state)
        print(f"wrong score={result_score}")

        self.check_visited_consistency(visited, get_next_states, blocks, m, n, is_caught)

        result_score = visited.get(result_state)
        print(f"correct score={result_score}")

        self.last_visited = visited  # <--- save visited for later use
        return (result_score -1 )/2

    def solve(self, turn=0):
        mice, cats, blocks, m, n = self.parse_state()
        start_state = (mice, cats, turn, blocks, m, n)
        result = self.generic_solver(start_state, self.get_next_states, self.is_caught)

        if result == float('inf'):
            result = None

        print()
        print("testing this board:")
        print(self.state)
        print(f"{result=}")

        return result

    def check_visited_consistency(self, visited, get_next_states, blocks, m, n, is_caught):
        """
        בודקת ומתקנת עבור כל מצב ב-visited האם הערך שלו הוא אכן המקסימום/מינימום של כל המצבים הבאים (אם כולם קיימים ב-visited).
        ממשיכה בלולאה עד שאין יותר אי-התאמות.
        סופרת כמה איטרציות נדרשו.
        """
        self.consistency_loops = 0
        while True:
            self.consistency_loops += 1
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
                        all_in_visited = False
                        break
                if not all_in_visited or not next_scores:
                    continue  # לא בודקים מצבים לא שלמים
                expected = max(next_scores) if turn == 0 else min(next_scores)
                expected += 1
                if score != expected:
                    visited[state] = expected
                    fixed = True
            if not fixed:
                break
        print(f"consistency_loops={self.consistency_loops}")

    def get_last_visited(self):
        return getattr(self, 'last_visited', None)


