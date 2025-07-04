import math

BOARD_SIZE = 15
WIN_COUNT = 5
DEPTH_LIMIT = 2
RANGE = 1

def start_game():
    Human = input("Do you want to be 'B' (black) or 'W' (white)? (black goes first):\n").strip().upper()
    while Human not in ['B', 'W']:
        Human = input("Invalid choice. Please enter 'B' for black or 'W' for white:\n").strip().upper()
    Human = 'black' if Human == 'B' else 'white'
    StartState = ['-'] * (BOARD_SIZE * BOARD_SIZE)
    starting_player = 'black'
    play([starting_player, StartState], Human, False)

def other_player(player):
    return 'white' if player == 'black' else 'black'

def play(state, human, already_printed):
    player, current_state = state
    if is_terminal(current_state, already_printed):
        return

    print()
    draw(current_state)
    print()

    if player == human:
        while True:
            try:
                move_idx = int(input(f"Enter your move index (0-{BOARD_SIZE * BOARD_SIZE - 1}): "))
                if move_idx < 0 or move_idx >= BOARD_SIZE * BOARD_SIZE:
                    print("Invalid index.")
                    continue
                if current_state[move_idx] == '-':
                    next_state = current_state[:]
                    next_state[move_idx] = human
                    if is_terminal(next_state, False):
                        print()
                        draw(next_state)
                        return
                    computer = other_player(human)
                    play([computer, next_state], human, False)
                    break
                else:
                    print("Cell already taken.")
            except ValueError:
                print("Invalid input.")
    else:
        computer = player
        _, next_state = minimax(current_state, DEPTH_LIMIT, computer, computer)
        if is_terminal(next_state, False):
            print()
            draw(next_state)
            return
        play([other_player(computer), next_state], human, False)

def draw(state):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            cell = state[i * BOARD_SIZE + j]
            if cell == 'black':
                print('B', end=' ')
            elif cell == 'white':
                print('W', end=' ')
            else:
                print('-', end=' ')
        print()

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

def get_winner(state):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if state[i * BOARD_SIZE + j] != '-':
                color = state[i * BOARD_SIZE + j]
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
    for idx in range(len(state)):
        if state[idx] != '-':
            row = idx // BOARD_SIZE
            col = idx % BOARD_SIZE
            for dr in range(-RANGE, RANGE + 1):
                for dc in range(-RANGE, RANGE + 1):
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

# --- Minimax بدون Alpha-Beta ---
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

# Run game
start_game()