from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
CELL_SIZE = 8

columns = 0
rows = 0
board: list[list[int]] = []


def create_2d_array(cols: int, row_count: int) -> list[list[int]]:
    return [[0 for _ in range(row_count)] for _ in range(cols)]


def setup() -> None:
    global columns, rows, board
    py5.size(640, 240)
    columns = py5.width // CELL_SIZE
    rows = py5.height // CELL_SIZE
    board = create_2d_array(columns, rows)

    for i in range(1, columns - 1):
        for j in range(1, rows - 1):
            board[i][j] = py5.floor(py5.random(2))

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global board
    next_board = create_2d_array(columns, rows)

    for i in range(1, columns - 1):
        for j in range(1, rows - 1):
            neighbor_sum = 0
            for k in range(-1, 2):
                for l in range(-1, 2):
                    neighbor_sum += board[i + k][j + l]
            neighbor_sum -= board[i][j]

            if board[i][j] == 1 and neighbor_sum < 2:
                next_board[i][j] = 0
            elif board[i][j] == 1 and neighbor_sum > 3:
                next_board[i][j] = 0
            elif board[i][j] == 0 and neighbor_sum == 3:
                next_board[i][j] = 1
            else:
                next_board[i][j] = board[i][j]

    for i in range(columns):
        for j in range(rows):
            py5.fill(255 - board[i][j] * 255)
            py5.stroke(0)
            py5.square(i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE)

    board = next_board


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "game_of_life_####.png"))


py5.run_sketch()
