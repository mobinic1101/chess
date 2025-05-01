import pygame
import datatypes
from abstracts import AbstractPlayer, AbstractInputSource
from game_elements import Board


class Player(AbstractPlayer):
    def __init__(self, name: str, color: str, input_source: AbstractInputSource):
        super().__init__(name, color)
        self.input_source = input_source

    def get_input(
        self, board: Board, events: list[pygame.event.Event] = None, **kwargs
    ) -> datatypes.Move | None:
        """
        Delegate the get_input method to the input_source instance.

        Args:
            board (Board): The chess board instance.
            events (list[pygame.event.Event], optional): List of pygame events.

        Returns:
            datatypes.Move | None: The move returned by the input_source.
        """
        return self.input_source.get_input(board=board, events=events, **kwargs)
