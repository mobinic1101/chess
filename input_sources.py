import pygame
import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import helpers
import datatypes

if TYPE_CHECKING:
    from game_elements import Board


def get_clicked_pos(events: list[pygame.event.Event]) -> tuple[int, int] | None:
    if not events:
        return None
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            return mouse_pos
    return None


class AbstractInputSource(ABC):
    def __init__(self):
        self.board = None

    # def set_board(self, board: "game_elements.Board"):
    #     self.board = board

    @abstractmethod
    def get_input(
        self,
        color: str,
        board: "Board",
        events: list[pygame.event.Event] = None,
    ) -> "datatypes.Move | None":
        """
        Abstract method to get input for a move.

        Args:
            board (Board): The chess board instance.
            events (list[pygame.event.Event], optional): List of pygame events (used for Human input).
            color (str): the method will use piece.is_my_piece(self, color: str); so the
            color parameter is required.

        Returns:
            datatypes.Move | None: The move to be made, or None if no valid move is found.
        """
        pass


class Human(AbstractInputSource):
    def __init__(self):
        # stores the source and destination coordinates of a move
        self.inputs: list[tuple[int, int]] = []

    def get_input(
        self, color: str, events: list[pygame.event.Event], board: "Board" = None
    ) -> "datatypes.Move | None":
        mouse_pos = get_clicked_pos(events)
        if mouse_pos is None:
            return

        # validating clicked position
        cell = board.get_cell_by_coordinates(mouse_pos)
        if cell is None:
            return
        elif (len(self.inputs) == 0) and cell.piece is None:
            return

        self.inputs.append(cell.coordinate)
        if len(self.inputs) == 2:
            inputs = self.inputs.copy()
            self.inputs.clear()
            # validate destination pos
            dest_spot = None
            source_cell = board.get_cell(*inputs[0])
            for spot in source_cell.piece.find_available_spots(board, color=color):
                coordinate = spot.coordinate
                if inputs[1] == coordinate:
                    dest_spot = spot
            if dest_spot is None:
                return

            inputs = datatypes.Move(source=inputs[0], dest=dest_spot)
            return inputs
        return


class Bot(AbstractInputSource):
    def __init__(self):
        super().__init__()
        self.time_elapsed = None

    # def get_board_copy(self, board: Board) -> Board:
    #     """
    #     Creates a copy of the board and returns it.
    #     This is useful for the bot to simulate moves without affecting the actual game state.
    #     """
    #     return board.copy()

    def get_input(
        self, color: str, board: "Board", events: list[pygame.event.Event] = None
    ) -> "datatypes.Move | None":
        # we are not using `events` parameter here.
        if self.time_elapsed is None:
            self.time_elapsed = helpers.check_time_passed(1)
            return None
        if not next(self.time_elapsed):
            return None
        cells = [cell for cell in board.get_filled_cells() if cell.piece.color == color]
        possible_destinations = []
        while 1:
            source = random.choice(cells)
            available_spots = source.piece.find_available_spots(
                board, color=color, opponent=True
            )
            if available_spots:
                possible_destinations = available_spots
                break

        dest = random.choice(possible_destinations)

        # reset self.time_elapsed
        self.time_elapsed = None
        return datatypes.Move(source=source.coordinate, dest=dest)
