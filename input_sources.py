import pygame
import random
import datatypes
from abstracts import AbstractInputSource
from game_elements import Board


class Human(AbstractInputSource):
    def __init__(self):
        # Stores the source and destination coordinates of a move
        self.inputs: list[tuple[int, int]] = []

    def get_input(
        self, color: str, events: list[pygame.event.Event], board: Board = None
    ) -> datatypes.Move | None:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # check if the clicked pos is in the area of the board because if it's not
                # the get_cell_by_coordinates will return None
                cell_coordinates = board.get_cell_by_coordinates(mouse_pos)
                if not cell_coordinates:
                    break
                # Ensure the first click is on a piece; ignore if the cell is empty
                elif (len(self.inputs) == 0) and board.get_cell(
                    *cell_coordinates
                ).piece is None:
                    break

                self.inputs.append(cell_coordinates)
                if len(self.inputs) == 2:
                    inputs = self.inputs.copy()
                    self.inputs.clear()
                    inputs = datatypes.Move(source=inputs[0], dest=inputs[1])
                    # validate destination pos
                    source_cell = board.get_cell(*inputs.source)
                    available_spots = source_cell.piece.find_available_spots(
                        board, color=color
                    )
                    if inputs.dest not in available_spots:
                        break
                    return inputs
        return None


class Bot(AbstractInputSource):
    def get_input(
        self, color: str, board: Board, events: list[pygame.event.Event] = None
    ) -> datatypes.Move | None:
        # the Bot does not use events and color, so we can safely ignore them
        cells = [cell for cell in board.get_filled_cells() if cell.piece.color == color]
        possible_destinations = []
        while 1:
            source = random.choice(cells)
            available_spots = source.piece.find_available_spots(board, color=color)
            if available_spots:
                possible_destinations = available_spots
                break

        # choose a random destination
        dest = random.choice(possible_destinations)
        return datatypes.Move(source=source.coordinate, dest=dest)
