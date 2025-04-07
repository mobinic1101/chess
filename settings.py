import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(message)s")

BASE_DIR = Path(os.getcwd())
WIDTH, HIGHT = (1024, 600)
TEXTURE_DIR = BASE_DIR / "textures/"
DEFAULT_TEXTURE_PACK = "pack1"

# texture names
TEXTURE_NAMES = {
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
    "board": "board.jpg",
}

