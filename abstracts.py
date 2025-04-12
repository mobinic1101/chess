from abc import ABC, abstractmethod
import random
import pygame
import pygame.sprite


class AbstractDrawable(pygame.sprite.Sprite, ABC):
    def __init__(self, image: pygame.Surface):
        super().__init__()
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
    def __init__(self, image):
        super().__init__(image)

    @abstractmethod
    def find_available_spots(self, board):
        """a piece like a rook can only move to only x or only y directions right?
        so its available positions on the board will be those directions (coordinates)

        Args:
            board (Board): instance of Board class
        """
        pass
    
    def __str__(self):
        return f"Piece(id={self.id})"
