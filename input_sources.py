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
        self, events: list[pygame.event.Event], board: Board = None, **kwargs
    ) -> datatypes.Move | None:
        if events is None:
            raise ValueError("passing events parameter is required for Human input")
        if not kwargs.get("color"):
            raise ValueError("color parameter is required for Human input; pass it as a keyword argument in **kwargs parameter.")

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
                    source_cell = board.get_cell(inputs.source)
                    available_spots = source_cell.piece.find_available_spots(
                        board, color=self.color
                    )
                    if inputs.dest not in available_spots:
                        break
                    return inputs
        return None


class Bot(AbstractInputSource):
    def get_input(self, board: Board, events: list[pygame.event.Event] = None, **kwargs) -> datatypes.Move | None:
        # the Bot does not use events and color, so we can safely ignore them
        cells = board.get_filled_cells()
        source = random.choice(cells)
        dest = random.choice(source.piece.find_available_spots(board, color=self.color))
        return datatypes.Move(source=source, dest=dest)