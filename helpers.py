from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from game_elements import Cell


class SimpleSprite(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()


def invert_coordinate(coordinate: tuple[int, int]) -> tuple[int, int]:
    """
    Inverts the given coordinate.
    Example:
            (x: 2, y: 6) -> (x: -3, y: -7) |
            (x: -2, y: -6) -> (x: -1, y: -5)

    Args:
            coordinate (tuple[int, int]): The coordinate to invert.

    Returns:
            tuple[int, int]: The inverted coordinate.
    """
    x = -coordinate[0] - 1
    y = -coordinate[1] - 1

    return (x, y)


def move_piece(source: "Cell", dest: "Cell"):
    """moves a piece from a source cell to destination cell
    if there is no piece in source or the dest cell is already occopied raise ValueError

    Args:
        source (Cell): the cell you want to move the piece from
        dest (Cell): the cell you want to move the piece to

    Raises:
        ValueError: if there is no piece in source or the dest cell is already occopied
    """
    if source.piece is None or dest.piece is not None:
        raise ValueError(
            "Invalid move, source cell is empty or destination cell is not empty"
        )

    piece = source.piece
    dest.set_piece(piece)
    source.rem_piece()
