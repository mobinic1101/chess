from typing import TYPE_CHECKING
import abstracts

if TYPE_CHECKING:
    import game_elements


class Operation:
    def __init__(self, object: abstracts.AbstractDrawable, coordinate: tuple) -> None:
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
        en_passant_target_cell: "game_elements.Cell" = None,
        is_castling=False,
        is_promotion=False,
    ):
        self.coordinate = coordinate
        self.is_en_passant = is_en_passant
        self.en_passant_target_cell = en_passant_target_cell
        if self.is_en_passant:
            if self.en_passant_target_cell is None:
                raise ValueError(
                    "if you pass is_en_passant parameter as True you must pass the en_passant_target_cell too"
                )
        self.is_castling = is_castling
        self.is_promotion = is_promotion


class Move:
    """represents a single move a player does;
    example: Move(source=(2, 4), dest=(2, 5))
    """

    source: tuple[int, int]
    dest: tuple[int, int]

    def __init__(self, source: tuple[int, int], dest: AvailableSpot):
        self.source = source
        self.dest: AvailableSpot = dest
