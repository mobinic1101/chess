import pygame
from abstracts import AbstractPlayer
from game_elements import Board


class Human(AbstractPlayer):
    def __init__(self, name: str, color):
        super().__init__()
        self.name = name
        self.color = color
        self.inputs = []
        self.__board = Board()
    
    def get_input(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.inputs.append(mouse_pos)
                if len(self.inputs) == 2:
                    inputs = self.inputs.copy()
                    self.inputs.clear()
                    return (
                        self.__board.get_cell_by_coordinates(inputs[0]),
                        self.__board.get_cell_by_coordinates(inputs[1])
                        )
        return None

class Bot(AbstractPlayer):
    def get_input(self, board: Board) -> tuple[tuple[int, int], tuple[int, int]]:
        """
        Returns:
            tuple: example-> (source: tuple, dest: tuple)
        """
