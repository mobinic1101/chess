from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import game_elements
    from renderer import AbstractDrawable


class Operation:
    def __init__(self, object: "AbstractDrawable", coordinate: tuple) -> None:
        self.object = object
        self.coordinate = coordinate

    def __str__(self):
        return f"({self.object}, {self.coordinate})"

    def __eq__(self, other):
        return self.object.id == other.object.id


class AvailableSpot:
    def __init__(
        self,
        coordinate: tuple[int, int],
        is_en_passant=False,
        is_castling=False,
        is_promotion=False,
        target_cell: "game_elements.Cell" = None,
    ):
        """
        Args:
            coordinate (tuple[int, int]): coordinate for the available spot on the board
            is_en_passant (bool, optional): if moving to this spot is en-passant. Defaults to False.
            target_cell (game_elements.Cell, optional): the piece that the special move is gonna be made on. Defaults to None.
            is_castling (bool, optional): if moving to this spot is castling. Defaults to False.
            is_promotion (bool, optional): if moving to this spot is promotion. Defaults to False.

        Raises:
            ValueError: You must pass the target_cell parameter if you pass is_en_passant or is_castling as True
        """
        self.coordinate = coordinate
        self.is_en_passant = is_en_passant
        self.is_castling = is_castling
        self.is_promotion = is_promotion
        self.target_cell = target_cell
        self.castling_details: dict[str, tuple[int, int]] = {}
        if self.is_en_passant or self.is_castling:
            if self.target_cell is None:
                raise ValueError(
                    "You must pass the target_cell parameter if you pass is_en_passant or is_castling as True"
                )

    def set_castling_details(
        self,
        rook_new_pos: tuple[int, int],
        king_new_pos: tuple[int, int],
    ):
        """sets the details for castling move"""
        details = {
            "rook_new_pos": rook_new_pos,
            "king_new_pos": king_new_pos,
        }
        self.is_castling = True
        self.castling_details = details


class Move:
    """represents a single move a player does;
    example: Move(source=(2, 4), dest=(2, 5))
    """
    def __init__(self, source: tuple[int, int], dest: AvailableSpot):
        self.source = source
        self.dest: AvailableSpot = dest
        
    def __str__(self):
        return f"Move(source={self.source}, dest={self.dest.coordinate})"
