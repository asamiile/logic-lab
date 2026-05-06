from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
CELL_SIZE = 8


class Cell:
    def __init__(self, state: int, x: int, y: int, size: int) -> None:
        self.state = state
        self.previous = state
        self.x = x
        self.y = y
        self.size = size

    def show(self) -> None:
        py5.stroke(0)
        if self.previous == 0 and self.state == 1:
            py5.fill(0, 0, 255)
        elif self.state == 1:
            py5.fill(0)
        elif self.previous == 1 and self.state == 0:
            py5.fill(255, 0, 0)
        else:
            py5.fill(255)
        py5.square(self.x, self.y, self.size)


columns = 0
rows = 0
board: list[list[Cell]] = []


def create_2d_array(cols: int, row_count: int) -> list[list[Cell]]:
    arr: list[list[Cell]] = []
    for i in range(cols):
        col: list[Cell] = []
        for j in range(row_count):
            col.append(Cell(0, i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE))
        arr.append(col)
    return arr


def setup() -> None:
    global columns, rows, board
    py5.size(640, 240)
    columns = py5.width // CELL_SIZE
    rows = py5.height // CELL_SIZE
    board = create_2d_array(columns, rows)
    for i in range(1, columns - 1):
        for j in range(1, rows - 1):
            board[i][j] = Cell(py5.floor(py5.random(2)), i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    for x in range(1, columns - 1):
        for y in range(1, rows - 1):
            neighbor_sum = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    neighbor_sum += board[x + i][y + j].previous
            neighbor_sum -= board[x][y].previous

            if board[x][y].state == 1 and neighbor_sum < 2:
                board[x][y].state = 0
            elif board[x][y].state == 1 and neighbor_sum > 3:
                board[x][y].state = 0
            elif board[x][y].state == 0 and neighbor_sum == 3:
                board[x][y].state = 1

    for i in range(columns):
        for j in range(rows):
            board[i][j].show()
            board[i][j].previous = board[i][j].state


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "game_of_life_oop_####.png"))


py5.run_sketch()
