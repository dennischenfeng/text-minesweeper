"""
Text-based minesweeper game
"""
import numpy as np
from typing import List, Tuple

ADJACENT_SPACE_DELTAS = [(-1, 0), (0, 1), (1, 0), (0, -1)]
SURROUNDING_SPACE_DELTAS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


class Game:
    def __init__(self, board_size: int, num_mines: int):
        """

        :param board_size: the board will be a square of length `board_size`
        :param num_mines: number of mines in the game, randomly dispersed
        """
        self.board = Board(board_size, num_mines)

    def play(self) -> None:
        """
        The main loop to play the game
        """
        game_status = 0
        self.board.display_visible()
        while game_status == 0:
            user_input = input("Enter your move (e.g. '1,3,0'): ")
            s = user_input.split(',')
            row = int(s[0])
            col = int(s[1])
            flag = bool(int(s[2]))

            game_status = self.board.step(row, col, flag)
            self.board.display_visible()

        if game_status == -1:
            print("You lose! Try again.")
        else:
            print("You win! Congratulations!")


class Board:
    def __init__(self, board_size: int, num_mines: int):
        """
        Initialize the board. The internal board state is represented with a number in each element,
        with the following meanings:
        -1: mine
        0: no mines in adjacent spaces (i.e. displayed as blank space)
        1 through 8: indicates number of mines in adjacent space

        :param board_size: the board will be a square of length `board_size`
        :param num_mines: number of mines in the game, randomly dispersed
        """
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.board_size = board_size
        self.num_mines = num_mines

        # Add mines randomly
        mine_flattened_locs = np.random.choice(board_size ** 2, num_mines, replace=False)
        for flat_loc in mine_flattened_locs:
            loc = (flat_loc // board_size, flat_loc % board_size)
            self.board[loc] = -1
        for row in range(board_size):
            for col in range(board_size):
                if self.board[row, col] != -1:
                    self.board[row, col] = self._num_mines_surrounding(row, col)

        self.visibility = np.zeros((board_size, board_size), dtype=bool)
        self.flags = np.zeros((board_size, board_size), dtype=bool)

    def _num_mines_surrounding(self, row: int, col: int) -> int:
        """
        Number of mines surrounding this particular position

        :param row: row of position
        :param col: col of position
        :return: number of mines surrounding
        """
        mines = 0
        # TODO: refactor to use SURROUNDING_SPACE_DELTAS
        for row_delta in [-1, 0, 1]:
            current_row = row + row_delta
            if 0 <= current_row < self.board_size:
                for col_delta in [-1, 0, 1]:
                    current_col = col + col_delta
                    if 0 <= current_col < self.board_size:
                        if row_delta == 0 and col_delta == 0:
                            pass
                        else:
                            mines += 1 if self.board[current_row, current_col] == -1 else 0
        return mines

    def _connected_blank_spaces(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Identifies a list of all blank spaces within an adjacent-connected region to the identified position. Uses a
        BFS to search for these

        :param row:
        :param col:
        :return: list of positions
        """
        spaces = [(row, col)]
        queue = [(row, col)]

        while len(queue) > 0:
            row, col = queue.pop(0)
            for row_delta, col_delta in ADJACENT_SPACE_DELTAS:
                current_row = row + row_delta
                current_col = col + col_delta

                within_board = 0 <= current_row < self.board_size and 0 <= current_col < self.board_size
                if within_board and self.board[current_row, current_col] == 0 and (current_row, current_col) not in spaces:
                    queue.append((current_row, current_col))
                    spaces.append((current_row, current_col))
        return spaces

    def step(self, row: int , col: int, flag: bool) -> int:
        """
        The move that the player plays.

        :param row: row of the move
        :param col: column of the move
        :param flag: whether the player's move was to toggle flag for the position, or to uncover the position
        :return: game status; 0 is ongoing, -1 is lost, 1 is won
        """
        if flag:
            self.flags[row, col] = not self.flags[row, col]
        elif self.board[row, col] > 0:
            self.visibility[row, col] = True
        elif self.board[row, col] == 0:
            blank_spaces = self._connected_blank_spaces(row, col)
            for space_row, space_col in blank_spaces:
                self.visibility[space_row, space_col] = True
                for delta_row, delta_col in SURROUNDING_SPACE_DELTAS:
                    current_row = space_row + delta_row
                    current_col = space_col + delta_col
                    within_board = 0 <= current_row < self.board_size and 0 <= current_col < self.board_size
                    if within_board and self.board[current_row, current_col] > 0:
                        self.visibility[current_row, current_col] = True
        else:
            self.visibility[row, col] = True
            return -1

        if np.sum(self.visibility) == self.board_size ** 2 - self.num_mines:
            return 1
        else:
            return 0

    def display_visible(self) -> None:
        """
        Prints out the visible board
        """
        d = self.board.astype(str)
        for row in range(self.board_size):
            for col in range(self.board_size):
                if not self.visibility[row, col]:
                    d[row, col] = "?"
                if self.flags[row, col]:
                    d[row, col] = "F"
        print(d)


def test_text_minesweeper():
    np.random.seed(1)
    b = Board(10, 10)

    print(b.board)
    b.step(0, 9, False)
    print(b.display_visible())
    b.step(5, 5, False)
    print(b.display_visible())
    b.step(5, 6, True)
    print(b.display_visible())
    b.step(5, 6, False)
    print(b.display_visible())
    b.step(5, 6, True)
    print(b.display_visible())
    b.step(0, 0, False)
    print(b.display_visible())

# test_text_minesweeper()

g = Game(10, 10)
g.play()