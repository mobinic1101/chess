from abc import ABC, abstractmethod
import pygame
import pygame.sprite


class AbstractDrawable(pygame.sprite.Sprite, ABC):
    def __init__(self, sprite: pygame.Surface):
        super().__init__()
        self.image = sprite
        self.rect = self.sprite.get_rect()

    def move_x(self, value):
        self.rect.x += value

    def move_y(self, value):
        self.rect.y += value


class AbstractPiece(AbstractDrawable):
    def __init__(self, _id, sprite):
        super().__init__(sprite)
        self.id = _id

    @abstractmethod
    def find_available_spots(self, board):
        """a piece like a rook can only move to only x or only y directions right?
        so its available positions on the board will be those directions (coordinates)

        Args:
            board (Board): instance of Board class
        """
        pass
