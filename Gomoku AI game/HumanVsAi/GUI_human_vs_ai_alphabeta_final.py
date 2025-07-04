import tkinter as tk
import random
import math

BOARD_SIZE = 15
CELL_SIZE = 30
PLAYER_BLACK = '●'  # Black pieces
PLAYER_WHITE = '○'  # White pieces

class GomokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gomoku 15x15")

        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        # Default player colors (user plays Black, AI White)
        self.user_color = 'black'  # can be 'black' or 'white'
        self.ai_color = 'white'

        # Current player on board (black always starts first in Gomoku)
        self.current_player = 'black'

        self.mode = tk.StringVar(value="human_minimax")
        self.player_color_var = tk.StringVar(value="black")  # New variable for color choice

        self.setup_ui()

        # Trace changes in mode or color
        self.mode.trace_add("write", self.on_mode_change)
        self.player_color_var.trace_add("write", self.on_color_change)

    def setup_ui(self):
        # Mode selection
        options = [
            #("Human vs AI (Minimax)", "human_minimax"),
            ("Human vs AI (Alpha-Beta)", "human_alphabeta"),
            #("AI vs AI (Minimax vs Alpha-Beta)", "ai_vs_ai")
        ]

        option_frame = tk.Frame(self.root)
        option_frame.pack(pady=10)

        for text, value in options:
            tk.Radiobutton(option_frame, text=text, variable=self.mode, value=value).pack(anchor="w")

        # New: Player color selection (Black or White)
        color_frame = tk.Frame(self.root)
        color_frame.pack(pady=10)

        tk.Label(color_frame, text="Choose your color:").pack(anchor="w")

        tk.Radiobutton(color_frame, text="Black (You start first)", variable=self.player_color_var, value="black").pack(anchor="w")
        tk.Radiobutton(color_frame, text="White (AI starts first)", variable=self.player_color_var, value="white").pack(anchor="w")

        self.canvas = tk.Canvas(self.root, width=BOARD_SIZE * CELL_SIZE, height=BOARD_SIZE * CELL_SIZE, bg="bisque")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)

        self.status_label = tk.Label(self.root, text="Your turn", font=("Arial", 14))
        self.status_label.pack(pady=5)

        self.reset_button = tk.Button(self.root, text="Reset Game", command=self.reset_game)
        self.reset_button.pack(pady=10)

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                x1 = j * CELL_SIZE
                y1 = i * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")
                if self.board[i][j] == 'black':
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="black")
                elif self.board[i][j] == 'white':
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="white")

    def handle_click(self, event):
        # Ignore clicks if mode is AI vs AI or not user's turn
        if self.mode.get().startswith("ai") or self.current_player != self.user_color:
            return

        row = event.y // CELL_SIZE
        col = event.x // CELL_SIZE

        if self.board[row][col] is not None:
            return

        # User places piece
        self.board[row][col] = self.user_color
        self.draw_board()

        if self.check_winner(self.user_color):
            self.status_label.config(text="You win!")
            self.canvas.unbind("<Button-1>")
            return

        # Switch turn to AI
        self.current_player = self.ai_color
        self.status_label.config(text="AI's turn")

        # Let AI move after short delay
        self.root.after(500, self.ai_move)

    def ai_move(self):
        if self.current_player != self.ai_color:
            return

        move = self.get_ai_move()
        if move:
            row, col = move
            self.board[row][col] = self.ai_color
            self.draw_board()
            if self.check_winner(self.ai_color):
                self.status_label.config(text="AI wins!")
                self.canvas.unbind("<Button-1>")
                return

            # Switch back to user
            self.current_player = self.user_color
            self.status_label.config(text="Your turn")

    def ai_vs_ai(self):
        if self.check_winner('black') or self.check_winner('white'):
            return

        move = self.get_ai_move()
        if move:
            row, col = move
            self.board[row][col] = self.current_player
            self.draw_board()

            if self.check_winner(self.current_player):
                self.status_label.config(text=f"{self.current_player.capitalize()} wins!")
                return

            # Switch player
            self.current_player = 'white' if self.current_player == 'black' else 'black'
            self.root.after(300, self.ai_vs_ai)

    def get_ai_move(self):
        # Flatten board for AI algorithms
        flat_board = []
        for row in self.board:
            for cell in row:
                if cell == 'black':
                    flat_board.append('black')
                elif cell == 'white':
                    flat_board.append('white')
                else:
                    flat_board.append('-')

        # Decide AI move depending on mode and current player
        if self.mode.get() == "human_minimax" or (self.mode.get() == "ai_vs_ai" and self.current_player == 'black'):
            _, next_state = minimax(flat_board, 2, 'black', 'black')
        else:
            next_state = alphabeta(flat_board, -float('inf'), float('inf'), 'white', depth=2)

        for i in range(BOARD_SIZE * BOARD_SIZE):
            if flat_board[i] != next_state[i]:
                return i // BOARD_SIZE, i % BOARD_SIZE
        return None

    def reset_game(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.canvas.delete("all")
        self.draw_board()
        self.canvas.bind("<Button-1>", self.handle_click)

        # Set players based on selected color
        self.user_color = self.player_color_var.get()
        self.ai_color = 'white' if self.user_color == 'black' else 'black'

        # Black always starts first
        self.current_player = 'black'

        # Update status label accordingly
        if self.user_color == 'black':
            self.status_label.config(text="Your turn")
        else:
            self.status_label.config(text="AI's turn")

        # If AI starts (user is white), let AI play first
        if self.user_color == 'white' and self.mode.get().startswith("human"):
            self.root.after(500, self.ai_move)
        elif self.mode.get() == "ai_vs_ai":
            self.status_label.config(text="AI vs AI mode")
            self.root.after(500, self.ai_vs_ai)

    def on_mode_change(self, *args):
        self.reset_game()

    def on_color_change(self, *args):
        self.reset_game()

    def check_winner(self, player):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.check_line(player, row, col, 1, 0) or \
                   self.check_line(player, row, col, 0, 1) or \
                   self.check_line(player, row, col, 1, 1) or \
                   self.check_line(player, row, col, 1, -1):
                    return True
        return False

    def check_line(self, player, row, col, dr, dc):
        count = 0
        for i in range(5):
            r = row + i * dr
            c = col + i * dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                count += 1
            else:
                break
        return count == 5

# (Minimax and Alpha-Beta functions unchanged)

# -- rest of your minimax and alphabeta code here --
def move(state, player):
    return [state[:i] + [player] + state[i+1:] for i in range(len(state)) if state[i] == '-']

def get_winner(state):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if state[i * BOARD_SIZE + j] != '-':
                if j + 5 <= BOARD_SIZE and all(state[i * BOARD_SIZE + (j + k)] == state[i * BOARD_SIZE + j] for k in range(5)):
                    return state[i * BOARD_SIZE + j]
                if i + 5 <= BOARD_SIZE and all(state[(i + k) * BOARD_SIZE + j] == state[i * BOARD_SIZE + j] for k in range(5)):
                    return state[i * BOARD_SIZE + j]
                if i + 5 <= BOARD_SIZE and j + 5 <= BOARD_SIZE and all(state[(i + k) * BOARD_SIZE + (j + k)] == state[i * BOARD_SIZE + j] for k in range(5)):
                    return state[i * BOARD_SIZE + j]
                if i + 5 <= BOARD_SIZE and j - 5 >= -1 and all(state[(i + k) * BOARD_SIZE + (j - k)] == state[i * BOARD_SIZE + j] for k in range(5)):
                    return state[i * BOARD_SIZE + j]
    return '-'

def utility(state):
    winner = get_winner(state)
    if winner == 'black':
        return 1
    elif winner == 'white':
        return -1
    return 0

def minimax(state, depth, player, maximizing_player):
    if get_winner(state) != '-' or depth == 0:
        return utility(state), state
    if player == maximizing_player:
        max_eval = -math.inf
        best_state = None
        for next_state in move(state, player):
            eval_score, _ = minimax(next_state, depth - 1, 'white' if player == 'black' else 'black', maximizing_player)
            if eval_score > max_eval:
                max_eval = eval_score
                best_state = next_state
        return max_eval, best_state
    else:
        min_eval = math.inf
        best_state = None
        for next_state in move(state, player):
            eval_score, _ = minimax(next_state, depth - 1, 'white' if player == 'black' else 'black', maximizing_player)
            if eval_score < min_eval:
                min_eval = eval_score
                best_state = next_state
        return min_eval, best_state

# Alpha-Beta Pruning

def heuristic(state):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    score = 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if state[i * BOARD_SIZE + j] == '-':
                continue
            player = state[i * BOARD_SIZE + j]
            modifier = 1 if player == 'black' else -1
            for dx, dy in directions:
                count = 0
                open_ends = 0
                x, y = i, j
                while 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and state[x * BOARD_SIZE + y] == player:
                    count += 1
                    x += dx
                    y += dy
                if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and state[x * BOARD_SIZE + y] == '-':
                    open_ends += 1
                x, y = i - dx, j - dy
                while 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and state[x * BOARD_SIZE + y] == player:
                    count += 1
                    x -= dx
                    y -= dy
                if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and state[x * BOARD_SIZE + y] == '-':
                    open_ends += 1
                if count >= 5:
                    score += modifier * 100000
                elif count == 4 and open_ends == 2:
                    score += modifier * 10000
                elif count == 4:
                    score += modifier * 1000
                elif count == 3 and open_ends == 2:
                    score += modifier * 500
                elif count == 3:
                    score += modifier * 100
                elif count == 2 and open_ends == 2:
                    score += modifier * 50
                elif count == 2:
                    score += modifier * 10
    return score

def alphabeta(state, alpha, beta, player, depth):
    best_move = None
    def max_value(state, alpha, beta, depth):
        if depth == 0 or utility(state) != 0:
            return heuristic(state)
        v = -float('inf')
        for s in move(state, 'black'):
            v2 = min_value(s, alpha, beta, depth - 1)
            nonlocal best_move
            if v2 > v:
                v = v2
                if depth == max_depth:
                    best_move = s
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta, depth):
        if depth == 0 or utility(state) != 0:
            return heuristic(state)
        v = float('inf')
        for s in move(state, 'white'):
            v2 = max_value(s, alpha, beta, depth - 1)
            nonlocal best_move
            if v2 < v:
                v = v2
                if depth == max_depth:
                    best_move = s
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    max_depth = depth
    if player == 'black':
        max_value(state, alpha, beta, depth)
    else:
        min_value(state, alpha, beta, depth)
    return best_move

if __name__ == '__main__':
    root = tk.Tk()
    gui = GomokuGUI(root)
    root.mainloop()
