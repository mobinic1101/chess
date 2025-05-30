import inspect
from abc import ABC
import pygame
from input_sources import AbstractInputSource
import game_elements
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import datatypes


class PlayerInput:
    def __init__(self, move: "datatypes.Move"):
        self.move = move

    @property
    def is_en_passant(self) -> bool:
        return self.move.dest.is_en_passant

    @property
    def is_castling(self) -> bool:
        return self.move.dest.is_castling

    @property
    def is_promotion(self) -> bool:
        return self.move.dest.is_promotion

    def get_cells(
        self, board: "game_elements.Board"
    ) -> tuple["game_elements.Cell", "game_elements.Cell"]:
        """Returns the source and destination cells for the move.

        Args:
            board (game_elements.Board): the current game board

        Returns:
            tuple[game_elements.Cell, game_elements.Cell]: source cell and dest cell

        Example:
            ```source_cell, dest_cell = player_input.get_cells(board)
        """
        source_cell = board.get_cell(*self.move.source)
        dest_cell = board.get_cell(*self.move.dest.coordinate)
        return source_cell, dest_cell


class AbstractPlayer(ABC):
    def __init__(self, name, color: str, input_source: AbstractInputSource):
        """
        Initializes an AbstractPlayer with a given name and color.

        Args:
            name (str): The name of the player.
            color (str): The color of the player, should be either 'white' or 'black'.
            input_source (AbstractInputSource): The input source for the player (e.g., Human or Bot).

        Raises:
            ValueError: If the color is not 'white' or 'black'.
        """

        color = color.lower()
        if not (color == "white" or color == "black"):
            raise ValueError(
                f"{inspect.getfullargspec(AbstractPlayer.__init__).args[2]} parameter should be either 'white' or 'black'. no other values allowed!"
            )
        self.color = color
        self.name = name
        self.input_source = input_source
        self.eaten_pieces: list["datatypes.Piece"] = []

    def validate_player_input(
        self, player_input: PlayerInput, board: "game_elements.Board"
    ):
        # check if the piece that the player is trying to move is actually his piece or
        # the dest cell is empty or the dest cell has a piece that is not his
        # otherwise return None meaning invalid move
        source_cell, dest_cell = player_input.get_cells(board)
        invalid_conditions = [
            not source_cell.piece.is_my_piece(self.color),
            dest_cell.piece and dest_cell.piece.is_my_piece(self.color),
            (dest_cell.piece and not dest_cell.piece.is_my_piece(self.color))
            and isinstance(dest_cell.piece, game_elements.King),
        ]
        if any(invalid_conditions):
            return False
        return True

    def get_input(
        self, board: "game_elements.Board", events: list[pygame.event.Event]
    ) -> "PlayerInput | None":
        """
        Delegate the get_input method to the input_source instance.

        Args:
            board (Board): The chess board instance.
            events (list[pygame.event.Event], optional): List of pygame events.

        Returns:
            PlayerInput | None: The move returned by the input_source.
        """
        result = self.input_source.get_input(self.color, board=board, events=events)
        if result is None:
            return None
        player_input = PlayerInput(move=result)

        is_valid = self.validate_player_input(player_input, board)
        if not is_valid:
            return None

        return player_input

    def __eq__(self, other: "AbstractPlayer") -> bool:
        """
        Checks if two players are equal based on their name and color.

        Args:
            other (AbstractPlayer): The other player to compare with.

        Returns:
            bool: True if both players have the same name and color, False otherwise.
        """
        return self.name == other.name and self.color == other.color


class Player(AbstractPlayer):
    def __init__(self, name: str, color: str, input_source: AbstractInputSource):
        super().__init__(name, color, input_source)
