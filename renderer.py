from abc import ABC
import random
import logging
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


class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.items: list[AbstractDrawable] = []

    def add_item(self, item: AbstractDrawable):
        """Adds an item to the renderer's list of items."""
        if item not in self.items:
            self.items.append(item)
    
    def bulk_add_items(self, items: list[AbstractDrawable]):
        """Adds multiple items to the renderer's list of items."""
        self.items.extend(items)

    def clear_items(self):
        """Clears the list of items."""
        self.items.clear()

    def draw_items(self, surface: pygame.Surface | None=None, update_display=False):
        """Iterates through items and draws them on the passed surface, clear the list of items at the end.
        The order of passing items affects the layering of drawing.

        Args:
            surface: Defaults to None, which uses the renderer's screen.
            update_display (bool, optional): Whether to update the display after drawing. Defaults to False.
        """
        if surface is None:
            surface = self.screen
        surface.fill((255, 255, 255))
        if not self.items:
            logging.warning("Renderer.draw_items called while self.items is empty.")
            return

        for item in self.items:
            surface.blit(item.image, item.rect)
        self.clear_items()
        if update_display:
            pygame.display.update()
