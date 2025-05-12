from typing import TYPE_CHECKING
from datetime import datetime, timedelta
import pygame

if TYPE_CHECKING:
    from game_elements import Board


class SimpleSprite(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()


def invert_coordinate(coordinate: tuple[int, int], board: "Board") -> tuple[int, int]:
    """
    Inverts the given coordinate.
    Example:
            (x: 2, y: 6) -> (x: 5, y: 1) |
            (x: -2, y: -6) -> (x: 1, y: 5)

    Args:
            coordinate (tuple[int, int]): The coordinate to invert.

    Returns:
            tuple[int, int]: The inverted coordinate.
    """
    # inverting the coordinates (output might be a negative
    # value for either x or y depending on their values for example if the coordinates[0] is
    # given a positive value the output will be a negative x value or if the coordinates is
    # a negative value the output will be a positive value)
    x = -coordinate[0] - 1
    y = -coordinate[1] - 1

    # overriding x and y to positive values/indexes
    x = x if x >= 0 else board.CELL_COUNT - abs(x)
    y = y if y >= 0 else board.CELL_COUNT - abs(y)

    return (x, y)


def check_time_passed(seconds: int):
    """a generator that takes an integer n as input and yield True if
    n seconds passed since we first initialized it, each time we call next() on it. otherwise false
    **it doesn't raise any StopIteration so you need to close the generator manually using .close() method**

    Args:
        seconds (int): seconds to pass for the generator to yield True.
    Returns:
        True: if the specified time passed since the first time generator initialized
        False: otherwise.
    """
    seconds_to_pass = timedelta(seconds=seconds)
    time_before = datetime.now()
    while True:
        current_time = datetime.now()
        if (current_time - time_before) > seconds_to_pass:
            yield True
        yield False


if __name__ == "__main__":
    # from game_elements import Board

    # print(invert_coordinate((3, -1), Board))
    secs = 10
    time_elapsed = check_time_passed(secs)

    while True:
        if next(time_elapsed):
            print(f"{secs} secs elapsed")
            time_elapsed.close()
            break
