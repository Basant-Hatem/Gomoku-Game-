# gomoku_alphabeta_combined.py

BOARD_SIZE = 15
WIN_COUNT = 5

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
        next_state = alphabeta(current_state, -float('inf'), float('inf'), computer, depth=2)
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
    # Loop through the grid, checking for a winning line in all directions
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            # If the current cell is occupied, check all directions
            if state[i * BOARD_SIZE + j] != '-':
                # Check horizontally (to the right)
                if j + WIN_COUNT <= BOARD_SIZE and all(state[i * BOARD_SIZE + (j + k)] == state[i * BOARD_SIZE + j] for k in range(WIN_COUNT)):
                    return state[i * BOARD_SIZE + j]
                # Check vertically (downwards)
                if i + WIN_COUNT <= BOARD_SIZE and all(state[(i + k) * BOARD_SIZE + j] == state[i * BOARD_SIZE + j] for k in range(WIN_COUNT)):
                    return state[i * BOARD_SIZE + j]
                # Check diagonally (down-right)
                if i + WIN_COUNT <= BOARD_SIZE and j + WIN_COUNT <= BOARD_SIZE and all(state[(i + k) * BOARD_SIZE + (j + k)] == state[i * BOARD_SIZE + j] for k in range(WIN_COUNT)):
                    return state[i * BOARD_SIZE + j]
                # Check diagonally (down-left)
                if i + WIN_COUNT <= BOARD_SIZE and j - WIN_COUNT >= -1 and all(state[(i + k) * BOARD_SIZE + (j - k)] == state[i * BOARD_SIZE + j] for k in range(WIN_COUNT)):
                    return state[i * BOARD_SIZE + j]

    return '-'

def move(state, player):
    return [state[:i] + [player] + state[i+1:] for i in range(len(state)) if state[i] == '-']

def utility(state):
    winner = get_winner(state)
    if winner == 'black':
        return 1
    elif winner == 'white':
        return -1
    return 0

# --- Alpha-Beta AI logic ---
def heuristic(state):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # → ↓ ↘ ↙
    score = 0

    def evaluate_line(x, y, dx, dy, player):
        count = 0
        open_ends = 0

        i, j = x, y
        while 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE and state[i * BOARD_SIZE + j] == player:
            count += 1
            i += dx
            j += dy

        # Check the next cell for openness
        if 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE and state[i * BOARD_SIZE + j] == '-':
            open_ends += 1

        # Check the opposite direction
        i, j = x - dx, y - dy
        while 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE and state[i * BOARD_SIZE + j] == player:
            count += 1
            i -= dx
            j -= dy

        if 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE and state[i * BOARD_SIZE + j] == '-':
            open_ends += 1

        if count >= WIN_COUNT:
            return 100000  # Immediate win

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


def alphabeta(state, alpha, beta, player, depth):
    best_move = None
    def max_value(state, alpha, beta, depth):
        if depth == 0 or utility(state) != 0:
            return heuristic(state)
        v = -float('inf')
        for s in move(state, 'black'):
            v2 = min_value(s, alpha, beta, depth - 1)
            if v2 > v:
                v = v2
                if depth == max_depth:
                    nonlocal best_move
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
            if v2 < v:
                v = v2
                if depth == max_depth:
                    nonlocal best_move
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

# Uncomment to play
start_game()
