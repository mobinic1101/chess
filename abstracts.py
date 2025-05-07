from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import inspect
import random
import pygame
import pygame.sprite

if TYPE_CHECKING:
    import datatypes
    import game_elements


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


class AbstractInputSource(ABC):
    @abstractmethod
    def get_input(
        self,
        color: str,
        board: "game_elements.Board",
        events: list[pygame.event.Event] = None,
    ):
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


class AbstractPlayer(ABC):
    def __init__(
        self,
        name,
        color: str,
        input_source: AbstractInputSource,
    ):
        """
        Initializes an AbstractPlayer with a given name and color.

        Args:
            name (str): The name of the player.
            color (str): The color of the player, should be either 'white' or 'black'.
            input_source (AbstractInputSource): The input source for the player (e.g., Human or Bot).
            board (Board, optional): The chess board instance. Defaults to None.
            If not provided, the player should set it later using the set_board method.

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
        self.moves = []

    def add_move(self, move: "datatypes.Move"):
        self.moves.append(move)

    def get_input(self, board, events: list[pygame.event.Event]):
        """
        Delegate the get_input method to the input_source instance.

        Args:
            board (Board): The chess board instance.
            events (list[pygame.event.Event], optional): List of pygame events.

        Returns:
            datatypes.Move | None: The move returned by the input_source.
        """
        result = self.input_source.get_input(
            self.color, board=board, events=events
        )
        if result is None:
            return None

        # check if the piece that the player is trying to move is actually his piece or
        # the dest cell is empty or the dest cell has a piece that is not his
        # otherwise return None meanning invalid move
        source_cell = board.get_cell(*result.source)
        dest_cell = board.get_cell(*result.dest)
        if not source_cell.piece.is_my_piece(self.color):
            return None
        if dest_cell.piece:
            if dest_cell.piece.is_my_piece(self.color):
                return None

        return result


class AbstractPiece(AbstractDrawable):
    def __init__(self, image, player: AbstractPlayer, coordinate: tuple[int, int]):
        """
        Args:
            player: player who owns the piece
            color: the color of the piece
            coordinate (tuple[int, int]): The row and column index of the cell on the board.
        """
        super().__init__(image)
        self.player = player
        self.color = player.color
        self.coordinate = coordinate
        self.available_spots_cache: dict[list] = {}

    def copy(self):
        piece_copy =  self.__class__(
            self.image.copy(), self.player, self.coordinate)
        piece_copy.id = self.id
        piece_copy.rect = self.rect.copy()
        piece_copy.available_spots_cache = self.available_spots_cache.copy()
        return piece_copy

    def is_my_piece(self, color: str):
        """provide your color, its gonna tell you whether it is your piece or not.

        Args:
            color (str): your color

        Returns:
            Boolean: True if it is your piece
        """
        return color == self.color

    def get_from_cache(
        self, coordinate: tuple[int, int]
    ) -> list[tuple[int, int]] | None:
        """
        Get available spots from cache.

        Args:
            coordinate (tuple[int, int]): The coordinates of the piece to find available spots for.

        Returns:
            list[tuple[int, int]] | None: A list of coordinates of available spots or None of not found.
        """
        return self.available_spots_cache.get(coordinate)

    @abstractmethod
    def calculate_moves(
        self, board, coordinate: tuple[int, int] | None = None, **kwargs
    ) -> list[tuple[int, int]]:
        pass

    def find_available_spots(
        self, board, coordinate: tuple[int, int] | None = None, **kwargs
    ) -> list[tuple[int, int]]:
        """
        Finds available spots a Piece can move to.

        Args:
            board (Board): The board to search for available spots.
            coordinate (tuple[int, int]): The coordinates of the piece to find available spots for.
              if not provided use self.coordinate (current piece coordiante).
            all (bool): If True, find all available spots, otherwise find only valid moves.

        Returns:
            list[tuple[int, int]]: A list of coordinates of available spots.
        """
        coordinate = coordinate if coordinate else self.coordinate

        # try hitting cache
        if available_spots := self.get_from_cache(coordinate):
            return available_spots

        available_spots = self.calculate_moves(board, coordinate, **kwargs)
        # cache the result
        self.available_spots_cache[coordinate] = available_spots
        return available_spots

    def __str__(self):
        return f"Piece(id={self.id})"
