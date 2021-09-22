"""
Test the text-based minesweeper game.
"""
import numpy as np
from text_minesweeper.game import Board


def test_lose():
    np.random.seed(1)
    b = Board(5, 5)
    print(b.board)

    assert b.step(0, 0, False) == 0
    assert b.step(2, 1, False) == 0
    assert b.step(1, 3, False) == 0
    assert b.step(2, 3, False) == -1
    b.display_visible()


def test_win():
    np.random.seed(1)
    b = Board(5, 5)
    print(b.board)

    assert b.step(0, 0, False) == 0
    assert b.step(4, 4, False) == 0
    assert b.step(4, 2, False) == 0
    assert b.step(4, 0, False) == 0
    assert b.step(0, 4, False) == 0
    assert b.step(1, 4, False) == 0
    assert b.step(1, 3, False) == 1
    b.display_visible()


# TODO: implement test cases for flag and Game
