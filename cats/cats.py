import itertools
from collections import deque
import time

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
        
    def generic_solver(self, start_state, get_next_states, is_caught):
        queue = deque()
        self.last_visited = visited = dict()
        mice_pos, cats_pos, turn, blocks, m, n = start_state
        result_state = (mice_pos, cats_pos, turn)
        visited[result_state] = float('inf')

        # מדידת זמן עבור הפונקציה המהירה עם pop (LIFO)
        start_time_fast = time.time()
        visited_fast = self.check_visited_consistency_fast(visited.copy(), get_next_states, blocks, m, n, is_caught, use_popleft=False)
        end_time_fast = time.time()
        fast_duration = end_time_fast - start_time_fast
        
        # מדידת זמן עבור הפונקציה המהירה עם popleft (FIFO)
        start_time_fast_popleft = time.time()
        visited_fast_popleft = self.check_visited_consistency_fast(visited.copy(), get_next_states, blocks, m, n, is_caught, use_popleft=True)
        end_time_fast_popleft = time.time()
        fast_popleft_duration = end_time_fast_popleft - start_time_fast_popleft
        
        # מדידת זמן עבור הפונקציה האיטית
        start_time_slow = time.time()
        self.check_visited_consistency(visited, get_next_states, blocks, m, n, is_caught)
        end_time_slow = time.time()
        slow_duration = end_time_slow - start_time_slow
        
        # הדפסת משכי זמן הריצה
        print(f"Fast consistency check (pop/LIFO) duration: {fast_duration:.4f} seconds")
        print(f"Fast consistency check (popleft/FIFO) duration: {fast_popleft_duration:.4f} seconds")
        print(f"Slow consistency check duration: {slow_duration:.4f} seconds")
        
        # השוואה בין pop ל-popleft
        if fast_duration == 0 or fast_popleft_duration == 0:
            print("One or both algorithms ran too quickly to measure differences (0s)")
        elif fast_duration > fast_popleft_duration:
            print(f"LIFO is slower than FIFO by {(fast_duration/fast_popleft_duration - 1)*100:.2f}%")
        else:
            print(f"LIFO is faster than FIFO by {(fast_popleft_duration/fast_duration - 1)*100:.2f}%")
        
        # בדיקה שהפונקציה המהירה אכן מהירה יותר
        faster_fast_duration = min(fast_duration, fast_popleft_duration)
        if faster_fast_duration > slow_duration:
            print(f"WARNING: Even the faster algorithm ({faster_fast_duration:.4f}s) is slower than slow algorithm ({slow_duration:.4f}s)")
            # בדיקה אם היחס גדול משמעותית
            if faster_fast_duration > slow_duration * 1.2:  # אם הפונקציה המהירה איטית ב-20% או יותר
                print(f"PERFORMANCE WARNING: Fast algorithm ({faster_fast_duration:.4f}s) is significantly slower than slow algorithm ({slow_duration:.4f}s)")

        # בדיקת עקביות התוצאות
        result_score = visited.get(result_state)
        result_score_fast = visited_fast.get(result_state)
        result_score_fast_popleft = visited_fast_popleft.get(result_state)
        
        print(f"correct score (slow)={result_score}")
        print(f"correct score fast (LIFO)={result_score_fast}")
        print(f"correct score fast (FIFO)={result_score_fast_popleft}")

        if result_score != result_score_fast or result_score != result_score_fast_popleft:
            print(f"WARNING: Inconsistency detected: slow={result_score}, fast_LIFO={result_score_fast}, fast_FIFO={result_score_fast_popleft}")
            print("Using slow algorithm's result as the correct one.")

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
        fixed = True
        while fixed:
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
                        visited[nstate] = float('inf')  # הוסף מצבים חסרים
                        fixed = True
                        all_in_visited = False
                if not all_in_visited or not next_scores:
                    continue  # לא בודקים מצבים לא שלמים
                expected = max(next_scores) if turn == 0 else min(next_scores)
                expected += 1
                if score != expected:
                    visited[state] = expected
                    fixed = True
        print(f"consistency_loops={self.consistency_loops}")

    def get_last_visited(self):
        return getattr(self, 'last_visited', None)

    def check_visited_consistency_fast(self, visited, get_next_states, blocks, m, n, is_caught, use_popleft=False):
        """
        גרסה מהירה עם תור ומבנה אובייקט לכל מצב ב-visited.
        visited: מילון שבו המפתחות הם מצבים (tuple) והערכים הם מספרים (score)
        הפונקציה לא משנה את visited המקורי, אלא בונה visited חדש עם אובייקטים.
        
        Parameters:
        -----------
        use_popleft : bool
            אם True, ישתמש ב-popleft (FIFO) במקום ב-pop (LIFO) להוצאת איברים מהתור.
        """
        # Initialize debug print control
        self.need_print = False
        nodes = {}
        
        # מבנה האובייקט לכל מצב
        class Node:
            def __init__(self, key, turn):
                self.key = key
                self.score = float('inf')
                self.parents = []
                self.children = []
                self.is_updated = False
                self.did_call_get_next_states = False
                self.turn = turn
            
            def update(self):
                expected = max([child.score for child in self.children], default=0) if self.turn == 0 else min([child.score for child in self.children], default=0)
                expected += 1
                if expected != self.score:
                    self.is_updated = True
                self.score = expected
            
            def __repr__(self):
                return f"Node(key={self.key}, score={self.score}, is_updated={self.is_updated}, did_call_get_next_states={self.did_call_get_next_states})"
            
        # יצירת visited חדש
        nodes = {}
        for state in visited.keys():
            # נניח ש-state = (mice, cats, turn)
            turn = state[2]
            node = Node(state, turn)
            nodes[state] = node
        # תור ראשוני
        queue = deque(nodes.values())
        while queue:
            # בוחר אם להשתמש ב-popleft (FIFO) או ב-pop (LIFO)                   
            x = queue.popleft() if use_popleft else queue.pop()
            if not x.did_call_get_next_states:
                x.did_call_get_next_states = True
                mice, cats, turn = x.key
                if is_caught(mice, cats):
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

            # עדכון הורים אם X התעדכן
            if x.is_updated:
                x.is_updated = False
                for parent in x.parents:
                    parent.update()
                    queue.append(parent)

        # הפקת מילון תוצאה
        result = {k: node.score for k, node in nodes.items()}
        return result




