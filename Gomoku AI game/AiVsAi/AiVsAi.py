import tkinter as tk
from tkinter import messagebox
import time
import math
import random

BOARD_SIZE = 15
CELL_SIZE = 30
WIN_COUNT = 5
DEPTH_LIMIT = 2
ALPHABETA_DEPTH = 2


class GomokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gomoku AI vs AI (Minimax vs Alpha-Beta)")
        self.state = ['-'] * (BOARD_SIZE * BOARD_SIZE)
        self.current_player = 'black'
        self.first_move_done = False
        self.game_over = False

        # Setup UI
        self.setup_ui()

        # Start the game
        self.root.after(500, self.play_turn)

    def setup_ui(self):
        # Create a frame for controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # Status label
        self.status_label = tk.Label(control_frame, text="Starting game...", font=('Arial', 12))
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Reset button
        self.reset_button = tk.Button(control_frame, text="Reset Game", command=self.reset_game)
        self.reset_button.pack(side=tk.LEFT, padx=10)

        # Create canvas for the board
        self.canvas = tk.Canvas(self.root,
                                width=BOARD_SIZE * CELL_SIZE,
                                height=BOARD_SIZE * CELL_SIZE,
                                bg='bisque')
        self.canvas.pack(pady=10)

        # Draw the board
        self.draw_board()

    def draw_board(self):
        """Draw the Gomoku board with grid lines"""
        self.canvas.delete("all")

        # Draw grid lines
        for i in range(BOARD_SIZE):
            # Horizontal lines
            self.canvas.create_line(0, i * CELL_SIZE,
                                    BOARD_SIZE * CELL_SIZE, i * CELL_SIZE)
            # Vertical lines
            self.canvas.create_line(i * CELL_SIZE, 0,
                                    i * CELL_SIZE, BOARD_SIZE * CELL_SIZE)

        # Draw stones
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                idx = i * BOARD_SIZE + j
                if self.state[idx] != '-':
                    x1 = j * CELL_SIZE + 5
                    y1 = i * CELL_SIZE + 5
                    x2 = (j + 1) * CELL_SIZE - 5
                    y2 = (i + 1) * CELL_SIZE - 5
                    fill_color = 'black' if self.state[idx] == 'black' else 'white'
                    self.canvas.create_oval(x1, y1, x2, y2, fill=fill_color, outline='black')

    def play_turn(self):
        if self.game_over:
            return

        if is_terminal(self.state, True):
            winner = get_winner(self.state)
            if winner != '-':
                message = f"{winner.capitalize()} wins!"
                self.status_label.config(text=message)
                self.game_over = True
            else:
                message = "It's a draw!"
                self.status_label.config(text=message)
                self.game_over = True
            return

        start_time = time.time()

        if not self.first_move_done:
            # Random first move
            empty_indices = [i for i, v in enumerate(self.state) if v == '-']
            if empty_indices:
                idx = random.choice(empty_indices)
                self.state[idx] = self.current_player
                self.first_move_done = True
                self.draw_board()
                self.status_label.config(text=f"Random first move by {self.current_player}")
                print(f"{self.current_player} (random) moved in {time.time() - start_time:.2f}s")
                self.current_player = other_player(self.current_player)
                self.root.after(500, self.play_turn)
            else:
                print("Error: No valid moves left for random selection.")
            return
        else:
            # AI turn
            if self.current_player == 'black':
                self.status_label.config(text="Alpha-Beta (Black) thinking...")
                new_state = alphabeta(self.state, -float('inf'), float('inf'), 'black', ALPHABETA_DEPTH)
            else:
                self.status_label.config(text="Minimax (White) thinking...")
                _, new_state = minimax(self.state, DEPTH_LIMIT, 'white', 'white')

            if new_state:
                self.state = new_state
            else:
                print("Error: AI returned an invalid state!")

            self.draw_board()
            print(f"{self.current_player} moved in {time.time() - start_time:.2f}s")
            self.current_player = other_player(self.current_player)
            self.root.after(500, self.play_turn)

    def reset_game(self):
        """Reset the game to initial state"""
        self.state = ['-'] * (BOARD_SIZE * BOARD_SIZE)
        self.current_player = 'black'
        self.first_move_done = False
        self.game_over = False
        self.status_label.config(text="Starting new game...")
        self.draw_board()
        self.root.after(500, self.play_turn)


# --- Game Logic Functions ---

def other_player(player):
    return 'white' if player == 'black' else 'black'


def get_winner(state):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if state[i * BOARD_SIZE + j] != '-':
                if j + WIN_COUNT <= BOARD_SIZE and all(
                        state[i * BOARD_SIZE + (j + k)] == state[i * BOARD_SIZE + j] for k in range(WIN_COUNT)):
                    return state[i * BOARD_SIZE + j]
                if i + WIN_COUNT <= BOARD_SIZE and all(
                        state[(i + k) * BOARD_SIZE + j] == state[i * BOARD_SIZE + j] for k in range(WIN_COUNT)):
                    return state[i * BOARD_SIZE + j]
                if i + WIN_COUNT <= BOARD_SIZE and j + WIN_COUNT <= BOARD_SIZE and all(
                        state[(i + k) * BOARD_SIZE + (j + k)] == state[i * BOARD_SIZE + j] for k in range(WIN_COUNT)):
                    return state[i * BOARD_SIZE + j]
                if i + WIN_COUNT <= BOARD_SIZE and j - WIN_COUNT >= -1 and all(
                        state[(i + k) * BOARD_SIZE + (j - k)] == state[i * BOARD_SIZE + j] for k in range(WIN_COUNT)):
                    return state[i * BOARD_SIZE + j]
    return '-'


def is_terminal(state, suppress_output=False):
    winner = get_winner(state)
    if winner != '-':
        if not suppress_output:
            print(f"{winner} wins!")
        return True
    if '-' not in state:
        if not suppress_output:
            print("It's a draw!")
        return True
    return False


def heuristic(state):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    score = 0

    def evaluate_line(x, y, dx, dy, player):
        count = 0
        open_ends = 0
        i, j = x, y
        while 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE and state[i * BOARD_SIZE + j] == player:
            count += 1
            i += dx
            j += dy
        if 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE and state[i * BOARD_SIZE + j] == '-':
            open_ends += 1
        i, j = x - dx, y - dy
        while 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE and state[i * BOARD_SIZE + j] == player:
            count += 1
            i -= dx
            j -= dy
        if 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE and state[i * BOARD_SIZE + j] == '-':
            open_ends += 1
        if count >= WIN_COUNT:
            return 100000
        if count == 4 and open_ends == 2:
            return 10000
        if count == 4 and open_ends == 1:
            return 1000
        if count == 3 and open_ends == 2:
            return 500
        if count == 3 and open_ends == 1:
            return 100
        if count == 2 and open_ends == 2:
            return 50
        if count == 2 and open_ends == 1:
            return 10
        return 0

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if state[i * BOARD_SIZE + j] == '-':
                continue
            player = state[i * BOARD_SIZE + j]
            modifier = 1 if player == 'black' else -1
            for dx, dy in directions:
                score += modifier * evaluate_line(i, j, dx, dy, player)
    return score


def move(state, player):
    return [state[:i] + [player] + state[i + 1:] for i in range(len(state)) if state[i] == '-']


def alphabeta(state, alpha, beta, player, depth):
    best_move = None

    def max_value(state, alpha, beta, depth):
        if depth == 0 or is_terminal(state, True):
            return heuristic(state)
        v = -float('inf')
        for s in move(state, 'black'):
            v2 = min_value(s, alpha, beta, depth - 1)
            if v2 > v:
                v = v2
                if depth == ALPHABETA_DEPTH:
                    nonlocal best_move
                    best_move = s
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta, depth):
        if depth == 0 or is_terminal(state, True):
            return heuristic(state)
        v = float('inf')
        for s in move(state, 'white'):
            v2 = max_value(s, alpha, beta, depth - 1)
            if v2 < v:
                v = v2
                if depth == ALPHABETA_DEPTH:
                    nonlocal best_move
                    best_move = s
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    if player == 'black':
        max_value(state, alpha, beta, depth)
    else:
        min_value(state, alpha, beta, depth)
    return best_move


def get_neighbors(state):
    neighbors = set()
    for idx in range(len(state)):
        if state[idx] != '-':
            row = idx // BOARD_SIZE
            col = idx % BOARD_SIZE
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    r = row + dr
                    c = col + dc
                    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                        new_idx = r * BOARD_SIZE + c
                        if state[new_idx] == '-':
                            neighbors.add(new_idx)
    return list(neighbors) if neighbors else [i for i in range(len(state)) if state[i] == '-']


def evaluate_line(line, player):
    opp = other_player(player)
    if opp in line and player in line:
        return 0
    count = line.count(player)
    return [0, 10, 100, 1000, 10000, 100000][count] if count <= 5 else 0


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
    if is_terminal(state, True) or depth == 0:
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


if __name__ == '__main__':
    root = tk.Tk()
    app = GomokuGUI(root)
    root.mainloop()