"""
Text-based minesweeper game. Only has basic functionality.
"""
import numpy as np
from typing import List, Tuple

ADJACENT_SPACE_DELTAS = [(-1, 0), (0, 1), (1, 0), (0, -1)]
SURROUNDING_SPACE_DELTAS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


class Game:
    """
    Game engine handle, to play the text-based minesweeper game.
    """

    def __init__(self, board_size: int, num_mines: int):
        """
        Instantiates a game handle.

        :param board_size: the board will be a square of length `board_size`
        :param num_mines: number of mines in the game, randomly dispersed
        """
        self.board_size = board_size
        self.num_mines = num_mines
        self.board = Board(self.board_size, self.num_mines)

    def play(self) -> None:
        """
        The main loop to play the game. User input move is (row, col, flag), which are all integers.
        """
        game_status = 0
        print("Initial visible board:")
        self.board.display_visible()
        print(
            "At each turn, type in a move in the form 'row, col, flag', where each value is an integer. E.g. '1,3,0'. "
            "`flag` of 1 means you want to flag the position; otherwise you'll uncover the position. "
            "After you submit your move, the resultant visible board will be shown. An error may be thrown if your "
            "input is invalid."
        )

        while game_status == 0:
            user_input = input("Enter your move (e.g. '1,3,0'): ")
            s = user_input.split(",")
            row = int(s[0])
            col = int(s[1])
            flag = bool(int(s[2]))

            game_status = self.board.step(row, col, flag)
            self.board.display_visible()

        if game_status == -1:
            print("You lose! Try again.")
        else:
            print("You win! Congratulations!")

    def reset(self) -> None:
        """
        Reset the game.
        """
        self.board = Board(self.board_size, self.num_mines)


class Board:
    """
    Game board, for text-minesweeper. Holds information about each space (e.g. whether mine, hidden, or flag). You
    can also play a move on the board.
    """

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
        self.board_size = board_size
        self.num_mines = num_mines
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)

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

    def _within_board(self, row: int, col: int) -> bool:
        """
        Whether or not the row / col is inside the board.

        :param row: row of position
        :param col: col of position
        :return:
        """
        return (0 <= row < self.board_size) and (0 <= col < self.board_size)

    def _num_mines_surrounding(self, row: int, col: int) -> int:
        """
        Number of mines surrounding this particular position

        :param row: row of position
        :param col: col of position
        :return: number of mines surrounding
        """
        mines = 0
        for row_delta, col_delta in SURROUNDING_SPACE_DELTAS:
            curr_row = row + row_delta
            curr_col = col + col_delta
            within_board = self._within_board(curr_row, curr_col)

            if within_board and self.board[curr_row, curr_col] == -1:
                mines += 1

        return mines

    def _connected_blank_spaces(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Identifies a list of all blank spaces within an adjacent-connected region to the identified position.
        Uses a BFS to search for this.

        :param row: row of position
        :param col: col of position
        :return: list of positions
        """
        spaces = [(row, col)]
        queue = [(row, col)]

        while len(queue) > 0:
            row, col = queue.pop(0)
            for row_delta, col_delta in ADJACENT_SPACE_DELTAS:
                curr_row = row + row_delta
                curr_col = col + col_delta
                within_board = self._within_board(curr_row, curr_col)

                if within_board and self.board[curr_row, curr_col] == 0 and (curr_row, curr_col) not in spaces:
                    queue.append((curr_row, curr_col))
                    spaces.append((curr_row, curr_col))

        return spaces

    def step(self, row: int, col: int, flag: bool) -> int:
        """
        Plays one move.

        :param row: row of the move
        :param col: column of the move
        :param flag: whether the player's move was to toggle flag for the position, or to uncover the position.
            True means it was to toggle flag
        :return: resultant game status; 0 is ongoing, -1 is lost, 1 is won
        """
        if flag:
            self.flags[row, col] = not self.flags[row, col]
        elif self.board[row, col] > 0:
            self.visibility[row, col] = True
        elif self.board[row, col] == 0:
            # uncover all connected blank spaces and surrounding non-mine spaces
            blank_spaces = self._connected_blank_spaces(row, col)
            for space_row, space_col in blank_spaces:
                self.visibility[space_row, space_col] = True
                for row_delta, col_delta in SURROUNDING_SPACE_DELTAS:
                    curr_row = space_row + row_delta
                    curr_col = space_col + col_delta
                    within_board = self._within_board(curr_row, curr_col)
                    if within_board and self.board[curr_row, curr_col] > 0:
                        self.visibility[curr_row, curr_col] = True
        else:
            # only lose if it you click a mine and it's not flagged. If flagged, do nothing.
            if not self.flags[row, col]:
                self.visibility[row, col] = True
                return -1

        if np.sum(self.visibility) == self.board_size ** 2 - self.num_mines:
            return 1
        else:
            return 0

    def display_visible(self) -> None:
        """
        Prints out the visible board. Each element will be converted to a str, and then hidden (?) or flagged (F)
        depending on the space.
        """
        d = self.board.astype(str)
        for row in range(self.board_size):
            for col in range(self.board_size):
                if not self.visibility[row, col]:
                    if self.flags[row, col]:
                        d[row, col] = "F"
                    else:
                        d[row, col] = "?"
        print(d)


if __name__ == "__main__":
    g = Game(5, 3)
    g.play()
