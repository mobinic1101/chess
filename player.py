import pygame
import random
from abstracts import AbstractPlayer
from game_elements import Board, basic_board_instance


class Human(AbstractPlayer):
    def __init__(self, name: str, color: str):
        super().__init__(name, color)
        self.inputs = []
        self.__board = basic_board_instance
    
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
    def get_input(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # check clicked pos is in the area of the board because if it's not
                # the get_cell_by_coordinates will return None
                cell_coordinates = self.__board.get_cell_by_coordinates(mouse_pos)
                if not cell_coordinates:
                    break
                self.inputs.append(cell_coordinates)
                if len(self.inputs) == 2:
                    inputs = self.inputs.copy()
                    self.inputs.clear()
                    return tuple(inputs)
        return None

class Bot(AbstractPlayer):
    def __init__(self, name, color: str):
        super().__init__(name, color)

    def get_input(self, board: Board) -> tuple[tuple[int, int], tuple[int, int]]:
        """
        Returns:
            tuple: example-> (source: tuple, dest: tuple)
        """
        cells = board.get_filled_cells()
        source = random.choice(cells)
        dest = random.choice(source.piece.find_available_spots(board, color=self.color))

        return (source.coordinate, dest)

