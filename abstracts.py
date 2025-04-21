from abc import ABC, abstractmethod
import random
import pygame
import pygame.sprite


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


class AbstractPiece(AbstractDrawable):
    def __init__(self, image, player: int, coordinate: tuple[int, int]):
        """
        Args:
            player: player 1 or 2 (player 1 is You and player 2 os your Opponent)
            coordinate (tuple[int, int]): The row and column index of the cell on the board.
        """
        super().__init__(image)
        self.player = player
        self.coordinate = coordinate
        self.available_spots_cache = {}

    def is_my_piece(self):
        return self.player == 1

    @abstractmethod
    def find_available_spots(self, board, coordinte: tuple[int, int] = None):
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


class AbstractPlayer(ABC):
    @abstractmethod
    def get_input(self):
        pass
