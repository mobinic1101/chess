from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import inspect
import random
import pygame
import pygame.sprite

if TYPE_CHECKING:
    from datatypes import Move


class AbstractDrawable(pygame.sprite.Sprite, ABC):
    def __init__(self, image: pygame.Surface):
        self.id = random.random()
        self.image = image
        self.rect = self.image.get_rect()

    def move_x(self, value):
        self.rect.x += value

    def move_y(self, value):
        self.rect.y += value

    def __eq__(self, other):
        return self.id == other.id


class AbstractPlayer(ABC):
    def __init__(self, name, color: str):
        """
        Initializes an AbstractPlayer with a given name and color.

        Args:
            name (str): The name of the player.
            color (str): The color of the player, should be either 'white' or 'black'.

        Raises:
            ValueError: If the color is not 'white' or 'black'.
        """

        if not (color == "white" or color == "black"):
            raise ValueError(
                f"{inspect.getfullargspec(AbstractPlayer.__init__).args[2]} parameter should be either 'white' or 'black'. no other values allowed!"
            )
        self.color = color
        self.name = name
        self.moves = []

    def add_move(self, move: "Move"):
        self.moves.append(move)

    @abstractmethod
    def get_input(self):
        pass


class AbstractPiece(AbstractDrawable):
    def __init__(self, image, player: AbstractPlayer, coordinate: tuple[int, int]):
        """
        Args:
            player: player who owns the piece
            color: the color of the piece
            coordinate (tuple[int, int]): The row and column index of the cell on the board.
        """
        super().__init__(image)
        self.player = player
        self.color = player.color
        self.coordinate = coordinate
        self.available_spots_cache = {}

    def is_my_piece(self, color: str):
        """provide your color, its gonna tell you whether it is your piece or not.

        Args:
            color (str): your color

        Returns:
            Boolean: True if it is your piece
        """
        return color == self.color

    @abstractmethod
    def find_available_spots(
        self, board, coordinate: tuple[int, int] | None = None, **kwargs
    ) -> list[tuple[int, int]]:
        """
        Finds available spots a Piece can move to.

        Args:
            board (Board): The board to search for available spots.
            coordinate (tuple[int, int]): The coordinates of the piece to find available spots for.
              if not provided use self.coordinate (current piece coordiante)

        Returns:
            list[tuple[int, int]]: A list of coordinates of available spots.
        """
        pass

    def __str__(self):
        return f"Piece(id={self.id})"


class AbstractInputSource(ABC):
    @abstractmethod
    def get_input(self):
        pass
