import os
from pathlib import Path
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from abstracts import AbstractPlayer

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(message)s")

FPS = 60
MOVEMENT_SPEED = 15
BASE_DIR = Path(os.getcwd())
WIDTH, HIGHT = (1024, 600)
CAPTION = "MasterChess"
TEXTURE_DIR = BASE_DIR / "textures/"
DEFAULT_TEXTURE_PACK = "pack1"
AVAILABLE_SPOTS_COLOR = "yellow"
LAST_MOVE_CELL_COLOR = "darkgreen"

BOARD_WIDTH_HIGHT = (HIGHT, HIGHT)
# divide BOARD_WIDTH_HIGHT by 8 because a board in a chess game has 8 cells
# and the board texture we are gonna use is 8x8, so get get piece with the
# size that is equal to a cell in the board.
PIECE_WIDTH_HIGHT = (BOARD_WIDTH_HIGHT[0] // 8, BOARD_WIDTH_HIGHT[0] // 8)

TEXTURE_NAMES = {
    "board": "board.jpg",
    "b_pawn": "b-pawn.png",
    "b_knight": "b-knight.png",
    "b_bishop": "b-bishop.png",
    "b_rook": "b-rook.png",
    "b_queen": "b-queen.png",
    "b_king": "b-king.png",
    "w_pawn": "w-pawn.png",
    "w_knight": "w-knight.png",
    "w_bishop": "w-bishop.png",
    "w_rook": "w-rook.png",
    "w_queen": "w-queen.png",
    "w_king": "w-king.png",
}


def get_piece_positions(player: "AbstractPlayer") -> dict[str, list[tuple[int, int]]]:
    """Get piece positions based on the player, meaning
    if the player is white, it will return WHITE piece positions on the bottom side of the board,
    or if the player is black, it will return BLACK piece positions on the bottom side of the board.

    Args:
        player (AbstractPlayer): The player object.

    Returns:
        dict[str, list[tuple[int, int]]]: A dictionary mapping piece names to their initial positions.
    """
    if player.color == "black":
        return {
            "b_pawn": [(6, i) for i in range(8)],
            "b_knight": [(7, 1), (7, 6)],
            "b_bishop": [(7, 2), (7, 5)],
            "b_rook": [(7, 0), (7, 7)],
            "b_queen": [(7, 3)],
            "b_king": [(7, 4)],
            "w_pawn": [(1, i) for i in range(8)],
            "w_knight": [(0, 1), (0, 6)],
            "w_bishop": [(0, 2), (0, 5)],
            "w_rook": [(0, 0), (0, 7)],
            "w_queen": [(0, 3)],
            "w_king": [(0, 4)],
        }
    else:
        return {
            "b_pawn": [(1, i) for i in range(8)],
            "b_knight": [(0, 1), (0, 6)],
            "b_bishop": [(0, 2), (0, 5)],
            "b_rook": [(0, 0), (0, 7)],
            "b_queen": [(0, 3)],
            "b_king": [(0, 4)],
            "w_pawn": [(6, i) for i in range(8)],
            "w_knight": [(7, 1), (7, 6)],
            "w_bishop": [(7, 2), (7, 5)],
            "w_rook": [(7, 0), (7, 7)],
            "w_queen": [(7, 3)],
            "w_king": [(7, 4)],
        }
