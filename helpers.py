from typing import TYPE_CHECKING
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


if __name__ == "__main__":
        from game_elements import Board
        print(invert_coordinate((3, -1), Board))
