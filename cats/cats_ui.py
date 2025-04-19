import tkinter as tk
from tkinter import messagebox
from cats import Cats
import threading
import time

CELL_SIZE = 40
GRID_ROWS = 6
GRID_COLS = 6

class BoardEditor(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()
        self.reset_board()

    def create_widgets(self):
        self.canvas = tk.Canvas(self, width=GRID_COLS*CELL_SIZE, height=GRID_ROWS*CELL_SIZE, bg='white')
        self.canvas.grid(row=0, column=0, columnspan=4)
        self.canvas.bind('<Button-1>', self.on_canvas_click)

        # Move list on the right
        self.move_listbox = tk.Listbox(self, width=32, height=GRID_ROWS+2)
        self.move_listbox.grid(row=0, column=4, rowspan=GRID_ROWS+2, sticky='ns')
        self.move_listbox.bind('<<ListboxSelect>>', self.on_move_list_select)

        self.mode = tk.StringVar(value='M')
        tk.Radiobutton(self, text='Mouse', variable=self.mode, value='M').grid(row=1, column=0)
        tk.Radiobutton(self, text='Cat', variable=self.mode, value='C').grid(row=1, column=1)
        tk.Radiobutton(self, text='Block', variable=self.mode, value='X').grid(row=1, column=2)
        tk.Radiobutton(self, text='Erase', variable=self.mode, value='.').grid(row=1, column=3)

        self.solve_btn = tk.Button(self, text='Solve', command=self.solve)
        self.solve_btn.grid(row=2, column=0, columnspan=2, sticky='ew')
        self.reset_btn = tk.Button(self, text='Reset', command=self.reset_board)
        self.reset_btn.grid(row=2, column=2, columnspan=1, sticky='ew')
        self.back_btn = tk.Button(self, text='Back', command=self.back_to_original)
        self.back_btn.grid(row=2, column=3, columnspan=1, sticky='ew')

        self.result_label = tk.Label(self, text='Result: ')
        self.result_label.grid(row=3, column=0, columnspan=4)
        self.progress_label = tk.Label(self, text='')
        self.progress_label.grid(row=5, column=0, columnspan=4)

        # Turn selection
        self.turn = tk.IntVar(value=0)
        tk.Label(self, text='First turn:').grid(row=4, column=0)
        tk.Radiobutton(self, text='Mouse', variable=self.turn, value=0).grid(row=4, column=1)
        tk.Radiobutton(self, text='Cat', variable=self.turn, value=1).grid(row=4, column=2)

    def reset_board(self):
        self.board = [['.' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.draw_board()
        self.result_label.config(text='Result: ')

    def draw_board(self):
        self.canvas.delete('all')
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                x1, y1 = x*CELL_SIZE, y*CELL_SIZE
                x2, y2 = x1+CELL_SIZE, y1+CELL_SIZE
                fill = 'white'
                if self.board[y][x] == 'M':
                    fill = 'lightgreen'
                elif self.board[y][x] == 'C':
                    fill = 'orange'
                elif self.board[y][x] == 'X':
                    fill = 'gray'
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline='black')
                if self.board[y][x] in 'MCX':
                    self.canvas.create_text(x1+CELL_SIZE//2, y1+CELL_SIZE//2, text=self.board[y][x], font=('Arial', 18, 'bold'))
        # Draw scores last, so they are on top
        if hasattr(self, 'last_cats_solver') and self.last_cats_solver is not None:
            self.draw_move_scores(self.last_cats_solver)
        self.update_move_list()

    def on_canvas_click(self, event):
        x, y = event.x // CELL_SIZE, event.y // CELL_SIZE
        if 0 <= x < GRID_COLS and 0 <= y < GRID_ROWS:
            # If we have a solved board, try to make a move for the current player
            if hasattr(self, 'last_cats_solver') and self.last_cats_solver is not None:
                # Get current state
                mice, cats, blocks, m, n = self.last_cats_solver.parse_state()
                turn = self.turn.get()
                next_states = self.last_cats_solver.get_next_states(mice, cats, turn, blocks, m, n)
                found = False
                for next_state in next_states:
                    nmice, ncats, nturn = next_state
                    # Figure out which cell(s) changed
                    if turn == 0:
                        old = set(mice)
                        new = set(nmice)
                        moved = list(new - old)
                        # staying in place
                        if not moved:
                            for pos in old:
                                if pos == (y, x):
                                    found = True
                                    break
                            if found:
                                break
                        else:
                            if (y, x) == moved[0]:
                                found = True
                                break
                    else:
                        old = set(cats)
                        new = set(ncats)
                        moved = list(new - old)
                        if not moved:
                            for pos in old:
                                if pos == (y, x):
                                    found = True
                                    break
                            if found:
                                break
                        else:
                            if (y, x) == moved[0]:
                                found = True
                                break
                if found:
                    # Update board and turn to new state
                    # Build new board from next_state
                    new_board = [['.' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
                    for by in range(GRID_ROWS):
                        for bx in range(GRID_COLS):
                            if (by, bx) in blocks:
                                new_board[by][bx] = 'X'
                    for my, mx in nmice:
                        new_board[my][mx] = 'M'
                    for cy, cx in ncats:
                        new_board[cy][cx] = 'C'
                    self.board = new_board
                    self.turn.set(nturn)
                    # Create new Cats object for the new state
                    new_state_str = '\n'.join(' '.join(row) for row in new_board)
                    new_cats_solver = Cats(new_state_str)
                    # Copy visited from previous solver
                    if hasattr(self.last_cats_solver, 'last_visited'):
                        new_cats_solver.last_visited = self.last_cats_solver.last_visited
                    self.last_cats_solver = new_cats_solver
                    self.draw_board()
                    return
            # Otherwise, default: edit mode
            self.board[y][x] = self.mode.get()
            self.draw_board()

    def board_to_str(self):
        return '\n'.join(' '.join(row) for row in self.board)

    def solve(self):
        state_str = self.board_to_str()
        def run_solver():
            try:
                original_board = [row[:] for row in self.board]
                original_turn = self.turn.get()
                cats_solver = Cats(state_str)
                self._solver_running = True
                self._solve_start_time = time.time()
                def update_progress():
                    if hasattr(cats_solver, 'last_visited') and cats_solver.last_visited is not None:
                        values = list(cats_solver.last_visited.values())
                        n_not_inf = sum(1 for v in values if v != float('inf'))
                        elapsed = int(time.time() - self._solve_start_time)
                        self.progress_label.config(text=f'States explored: {len(cats_solver.last_visited)} ({n_not_inf} not inf) | Time: {elapsed}s')
                    else:
                        elapsed = int(time.time() - self._solve_start_time)
                        self.progress_label.config(text=f'States explored: 0 | Time: {elapsed}s')
                    if getattr(self, '_solver_running', False):
                        self.after(500, update_progress)
                self.after(0, update_progress)
                result = cats_solver.solve(turn=self.turn.get())
                def update_ui():
                    self.original_board = original_board
                    self.original_turn = original_turn
                    if result is None:
                        self.result_label.config(text='Result: No solution')
                    else:
                        self.result_label.config(text=f'Result: {result:.1f} moves')
                    self.last_cats_solver = cats_solver
                    self.draw_board()
                    self._solver_running = False
                    self.progress_label.config(text='')
                self.after(0, update_ui)
            except Exception as e:
                self._solver_running = False
                self.after(0, lambda: self.progress_label.config(text=''))
                self.after(0, lambda: messagebox.showerror('Error', f'Failed to solve: {e}'))
        threading.Thread(target=run_solver, daemon=True).start()

    def back_to_original(self):
        if hasattr(self, 'original_board') and hasattr(self, 'original_turn'):
            self.board = [row[:] for row in self.original_board]
            self.turn.set(self.original_turn)
            self.draw_board()

    def draw_move_scores(self, cats_solver):
        # Get visited dict from solver
        visited = cats_solver.get_last_visited()
        if not visited:
            return
        # Parse current state
        mice, cats, blocks, m, n = cats_solver.parse_state()
        turn = self.turn.get()
        # Get all possible next states
        next_states = cats_solver.get_next_states(mice, cats, turn, blocks, m, n)
        # Collect all scores
        scores = []
        for next_state in next_states:
            nmice, ncats, nturn = next_state
            score = visited.get((nmice, ncats, nturn), None)
            if score is not None and score != float('inf'):
                scores.append(score)
        if not scores:
            best_score = None
        else:
            if turn == 0:
                best_score = max(scores)
            else:
                best_score = min(scores)
        for next_state in next_states:
            nmice, ncats, nturn = next_state
            if turn == 0:
                old = set(mice)
                new = set(nmice)
                moved = list(new - old)
                if not moved:
                    for pos in old:
                        y, x = pos
                        score = visited.get((nmice, ncats, nturn), None)
                        if score is None or score == float('inf'):
                            text = '∞'
                            color = 'red'
                        else:
                            text = f'{(score-1)/2:.1f}'
                            color = 'green' if best_score is not None and score == best_score else 'red'
                        x1, y1 = x*CELL_SIZE, y*CELL_SIZE
                        # Draw circle background
                        self.canvas.create_oval(x1+CELL_SIZE-22, y1+CELL_SIZE-22, x1+CELL_SIZE-2, y1+CELL_SIZE-2, fill=color, outline='black')
                        self.canvas.create_text(x1+CELL_SIZE-12, y1+CELL_SIZE-12, text=text, anchor='center', font=('Arial', 8), fill='white')
                    continue
            else:
                old = set(cats)
                new = set(ncats)
                moved = list(new - old)
                if not moved:
                    for pos in old:
                        y, x = pos
                        score = visited.get((nmice, ncats, nturn), None)
                        if score is None or score == float('inf'):
                            text = '∞'
                            color = 'red'
                        else:
                            text = f'{(score-1)/2:.1f}'
                            color = 'green' if best_score is not None and score == best_score else 'red'
                        x1, y1 = x*CELL_SIZE, y*CELL_SIZE
                        self.canvas.create_oval(x1+CELL_SIZE-22, y1+CELL_SIZE-22, x1+CELL_SIZE-2, y1+CELL_SIZE-2, fill=color, outline='black')
                        self.canvas.create_text(x1+CELL_SIZE-12, y1+CELL_SIZE-12, text=text, anchor='center', font=('Arial', 8), fill='white')
                    continue
            y, x = moved[0]
            score = visited.get((nmice, ncats, nturn), None)
            if score is None or score == float('inf'):
                text = '∞'
                color = 'red'
            else:
                text = f'{(score-1)/2:.1f}'
                color = 'green' if best_score is not None and score == best_score else 'red'
            x1, y1 = x*CELL_SIZE, y*CELL_SIZE
            self.canvas.create_oval(x1+CELL_SIZE-22, y1+CELL_SIZE-22, x1+CELL_SIZE-2, y1+CELL_SIZE-2, fill=color, outline='black')
            self.canvas.create_text(x1+CELL_SIZE-12, y1+CELL_SIZE-12, text=text, anchor='center', font=('Arial', 8), fill='white')

    def update_move_list(self):
        self.move_listbox.delete(0, tk.END)
        if not hasattr(self, 'last_cats_solver') or self.last_cats_solver is None:
            return
        visited = self.last_cats_solver.get_last_visited()
        if not visited:
            return
        mice, cats, blocks, m, n = self.last_cats_solver.parse_state()
        turn = self.turn.get()
        next_states = self.last_cats_solver.get_next_states(mice, cats, turn, blocks, m, n)
        moves = []
        scores = []
        for next_state in next_states:
            nmice, ncats, nturn = next_state
            if turn == 0:
                old = set(mice)
                new = set(nmice)
                moved = list(new - old)
                if not moved:
                    for pos in old:
                        move_desc = f"M: {pos} → {pos} (stay)"
                        score = visited.get((nmice, ncats, nturn), None)
                        scores.append(score)
                        moves.append((move_desc, score, next_state))
                else:
                    move_desc = f"M: {list(old - new)[0]} → {moved[0]}"
                    score = visited.get((nmice, ncats, nturn), None)
                    scores.append(score)
                    moves.append((move_desc, score, next_state))
            else:
                old = set(cats)
                new = set(ncats)
                moved = list(new - old)
                if not moved:
                    for pos in old:
                        move_desc = f"C: {pos} → {pos} (stay)"
                        score = visited.get((nmice, ncats, nturn), None)
                        scores.append(score)
                        moves.append((move_desc, score, next_state))
                else:
                    move_desc = f"C: {list(old - new)[0]} → {moved[0]}"
                    score = visited.get((nmice, ncats, nturn), None)
                    scores.append(score)
                    moves.append((move_desc, score, next_state))
        # Sort moves by score (best for current player first)
        if turn == 0:
            moves.sort(key=lambda x: (float('-inf') if x[1] is None else x[1]))
            moves = moves[::-1]  # Mouse wants max
        else:
            moves.sort(key=lambda x: (float('inf') if x[1] is None else x[1]))
            # Cat wants min
        # Find best score
        best_score = None
        filtered_scores = [s for s in scores if s is not None and s != float('inf')]
        if filtered_scores:
            if turn == 0:
                best_score = max(filtered_scores)
            else:
                best_score = min(filtered_scores)
        self._move_state_map = []
        for i, (move_desc, score, state) in enumerate(moves):
            score_str = '∞' if score is None or score == float('inf') else f'{(score-1)/2:.1f}'
            self.move_listbox.insert(tk.END, f"{move_desc} | {score_str}")
            # Color the item
            color = 'green' if best_score is not None and score == best_score else 'red'
            self.move_listbox.itemconfig(i, {'fg': color})
            self._move_state_map.append(state)

    def on_move_list_select(self, event):
        if not hasattr(self, '_move_state_map'):
            return
        selection = self.move_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        next_state = self._move_state_map[idx]
        nmice, ncats, nturn, blocks, m, n = next_state[0], next_state[1], next_state[2], self.last_cats_solver.parse_state()[2], GRID_ROWS, GRID_COLS
        # Build new board from next_state
        new_board = [['.' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        for by in range(GRID_ROWS):
            for bx in range(GRID_COLS):
                if (by, bx) in blocks:
                    new_board[by][bx] = 'X'
        for my, mx in nmice:
            new_board[my][mx] = 'M'
        for cy, cx in ncats:
            new_board[cy][cx] = 'C'
        self.board = new_board
        self.turn.set(nturn)
        # Create new Cats object for the new state
        new_state_str = '\n'.join(' '.join(row) for row in new_board)
        new_cats_solver = Cats(new_state_str)
        if hasattr(self.last_cats_solver, 'last_visited'):
            new_cats_solver.last_visited = self.last_cats_solver.last_visited
        self.last_cats_solver = new_cats_solver
        self.draw_board()


def main():
    root = tk.Tk()
    root.title('Cats & Mice Board Editor')
    app = BoardEditor(master=root)
    app.mainloop()

if __name__ == '__main__':
    main() 