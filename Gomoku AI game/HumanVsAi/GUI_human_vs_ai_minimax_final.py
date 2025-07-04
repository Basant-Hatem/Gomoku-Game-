import tkinter as tk
import math

BOARD_SIZE = 15
CELL_SIZE = 30
PLAYER_HUMAN = '●'
PLAYER_AI = '○'
DEPTH_LIMIT = 2
WIN_COUNT = 5
RANGE = 1

class GomokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gomoku 15x15")
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = PLAYER_HUMAN
        self.human_color = 'black'
        self.ai_color = 'white'

        self.mode = tk.StringVar(value="human_minimax")
        self.color_choice = tk.StringVar(value="black")

        self.setup_ui()
        self.mode.trace_add("write", self.on_mode_change)

    def setup_ui(self):
        option_frame = tk.Frame(self.root)
        option_frame.pack(pady=5)

        tk.Label(option_frame, text="Mode:").pack(anchor="w")
        tk.Radiobutton(option_frame, text="Human vs AI (Minimax)", variable=self.mode, value="human_minimax").pack(anchor="w")
        #tk.Radiobutton(option_frame, text="AI vs AI", variable=self.mode, value="ai_vs_ai").pack(anchor="w")

        color_frame = tk.Frame(self.root)
        color_frame.pack(pady=5)
        tk.Label(color_frame, text="Choose your color:").pack(anchor="w")
        tk.Radiobutton(color_frame, text="Black (You start)", variable=self.color_choice, value="black").pack(anchor="w")
        tk.Radiobutton(color_frame, text="White (AI starts)", variable=self.color_choice, value="white").pack(anchor="w")

        self.canvas = tk.Canvas(self.root, width=BOARD_SIZE * CELL_SIZE, height=BOARD_SIZE * CELL_SIZE, bg="bisque")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)

        self.status_label = tk.Label(self.root, text="Choose color and press Reset", font=("Arial", 14))
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
                if self.board[i][j] == PLAYER_HUMAN:
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=self.human_color)
                elif self.board[i][j] == PLAYER_AI:
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=self.ai_color)

    def handle_click(self, event):
        if self.mode.get() != "human_minimax":
            return

        row = event.y // CELL_SIZE
        col = event.x // CELL_SIZE
        if self.board[row][col] is not None:
            return

        self.board[row][col] = PLAYER_HUMAN
        self.draw_board()

        if self.check_winner(PLAYER_HUMAN):
            self.status_label.config(text="You win!")
            self.canvas.unbind("<Button-1>")
            return

        self.root.after(300, self.ai_move)

    def ai_move(self):
        move = self.get_ai_move()
        if move:
            row, col = move
            self.board[row][col] = PLAYER_AI
            self.draw_board()
            if self.check_winner(PLAYER_AI):
                self.status_label.config(text="AI wins!")
                self.canvas.unbind("<Button-1>")

    def ai_vs_ai(self):
        if self.check_winner(PLAYER_HUMAN) or self.check_winner(PLAYER_AI):
            return

        move = self.get_ai_move()
        if move:
            row, col = move
            self.board[row][col] = self.current_player
            self.draw_board()

            if self.check_winner(self.current_player):
                self.status_label.config(text=f"{self.current_player} wins!")
                return

            self.current_player = PLAYER_AI if self.current_player == PLAYER_HUMAN else PLAYER_HUMAN
            self.root.after(300, self.ai_vs_ai)

    def get_ai_move(self):
        state = self.convert_board_to_state()
        _, new_state = minimax(state, DEPTH_LIMIT, self.ai_color, self.ai_color)
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                idx = i * BOARD_SIZE + j
                if state[idx] != new_state[idx]:
                    return i, j
        return None

    def convert_board_to_state(self):
        state = []
        for row in self.board:
            for cell in row:
                if cell == PLAYER_HUMAN:
                    state.append(self.human_color)
                elif cell == PLAYER_AI:
                    state.append(self.ai_color)
                else:
                    state.append('-')
        return state

    def reset_game(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        if self.color_choice.get() == "black":
            self.human_color = 'black'
            self.ai_color = 'white'
            self.status_label.config(text="You play first")
        else:
            self.human_color = 'white'
            self.ai_color = 'black'
            self.status_label.config(text="AI starts...")
            self.root.after(300, self.ai_move)

        self.current_player = PLAYER_HUMAN
        self.draw_board()
        self.canvas.bind("<Button-1>", self.handle_click)

        if self.mode.get() == "ai_vs_ai":
            self.status_label.config(text="AI vs AI playing...")
            self.root.after(500, self.ai_vs_ai)

    def on_mode_change(self, *args):
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
        for i in range(WIN_COUNT):
            r = row + i * dr
            c = col + i * dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                count += 1
            else:
                break
        return count == WIN_COUNT


# --- Minimax AI below ---

def other_player(player):
    return 'white' if player == 'black' else 'black'

def is_terminal(state):
    return get_winner(state) != '-' or '-' not in state

def get_winner(state):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            idx = i * BOARD_SIZE + j
            if state[idx] != '-':
                color = state[idx]
                if j + WIN_COUNT <= BOARD_SIZE and all(state[i * BOARD_SIZE + (j + k)] == color for k in range(WIN_COUNT)):
                    return color
                if i + WIN_COUNT <= BOARD_SIZE and all(state[(i + k) * BOARD_SIZE + j] == color for k in range(WIN_COUNT)):
                    return color
                if i + WIN_COUNT <= BOARD_SIZE and j + WIN_COUNT <= BOARD_SIZE and all(state[(i + k) * BOARD_SIZE + (j + k)] == color for k in range(WIN_COUNT)):
                    return color
                if i + WIN_COUNT <= BOARD_SIZE and j - WIN_COUNT >= -1 and all(state[(i + k) * BOARD_SIZE + (j - k)] == color for k in range(WIN_COUNT)):
                    return color
    return '-'

def get_neighbors(state):
    neighbors = set()
    for idx, cell in enumerate(state):
        if cell != '-':
            row, col = divmod(idx, BOARD_SIZE)
            for dr in range(-RANGE, RANGE + 1):
                for dc in range(-RANGE, RANGE + 1):
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                        nidx = nr * BOARD_SIZE + nc
                        if state[nidx] == '-':
                            neighbors.add(nidx)
    return list(neighbors) if neighbors else [i for i in range(len(state)) if state[i] == '-']

def evaluate_line(line, player):
    opp = other_player(player)
    if opp in line and player in line:
        return 0
    count = line.count(player)
    if count == 5:
        return 100000
    elif count == 4:
        return 1000
    elif count == 3:
        return 100
    elif count == 2:
        return 10
    return 0

def evaluate_board(state, player):
    score = 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if j + 5 <= BOARD_SIZE:
                line = [state[i * BOARD_SIZE + j + k] for k in range(5)]
                score += evaluate_line(line, player)
                score -= evaluate_line(line, other_player(player))
            if i + 5 <= BOARD_SIZE:
                line = [state[(i + k) * BOARD_SIZE + j] for k in range(5)]
                score += evaluate_line(line, player)
                score -= evaluate_line(line, other_player(player))
            if i + 5 <= BOARD_SIZE and j + 5 <= BOARD_SIZE:
                line = [state[(i + k) * BOARD_SIZE + (j + k)] for k in range(5)]
                score += evaluate_line(line, player)
                score -= evaluate_line(line, other_player(player))
            if i + 5 <= BOARD_SIZE and j - 4 >= 0:
                line = [state[(i + k) * BOARD_SIZE + (j - k)] for k in range(5)]
                score += evaluate_line(line, player)
                score -= evaluate_line(line, other_player(player))
    return score

def minimax(state, depth, player, maximizing_player):
    if is_terminal(state) or depth == 0:
        return evaluate_board(state, maximizing_player), state

    best_state = None
    valid_moves = get_neighbors(state)

    if player == maximizing_player:
        max_eval = -math.inf
        for idx in valid_moves:
            new_state = state[:]
            new_state[idx] = player
            eval_score, _ = minimax(new_state, depth - 1, other_player(player), maximizing_player)
            if eval_score > max_eval:
                max_eval = eval_score
                best_state = new_state
        return max_eval, best_state
    else:
        min_eval = math.inf
        for idx in valid_moves:
            new_state = state[:]
            new_state[idx] = player
            eval_score, _ = minimax(new_state, depth - 1, other_player(player), maximizing_player)
            if eval_score < min_eval:
                min_eval = eval_score
                best_state = new_state
        return min_eval, best_state

# --- Run ---
if __name__ == "__main__":
    root = tk.Tk()
    app = GomokuGUI(root)
    root.mainloop()
