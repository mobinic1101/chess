from typing import SupportsIndex, TYPE_CHECKING
from abc import abstractmethod
import logging
import pygame
from renderer import AbstractDrawable
from texture_loader import TexturePack
from datatypes import AvailableSpot
import settings

if TYPE_CHECKING:
    from player import AbstractPlayer


class AbstractPiece(AbstractDrawable):
    def __init__(self, image, player: "AbstractPlayer", coordinate: tuple[int, int]):
        """
        Args:
            player: player who owns the piece
            color: the color of the piece
            coordinate (tuple[int, int]): The row and column index of the cell on the board.
        """
        super().__init__(image)
        self.player = player
        self.color = player.color
        self.set_coordinate(coordinate)
        # self.available_spots_cache: dict[list] = {}

    def copy(self):
        piece_copy = self.__class__(self.image.copy(), self.player, self.coordinate)
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

    def set_coordinate(self, coordinate: tuple[int, int]):
        self.rect.x = coordinate[1] * self.image.get_width()
        self.rect.y = coordinate[0] * self.image.get_height()
        self.coordinate = coordinate
        return self

    # def get_from_cache(
    #     self, coordinate: tuple[int, int]
    # ) -> list[tuple[int, int]] | None:
    #     """
    #     Get available spots from cache.

    #     Args:
    #         coordinate (tuple[int, int]): The coordinates of the piece to find available spots for.

    #     Returns:
    #         list[tuple[int, int]] | None: A list of coordinates of available spots or None of not found.
    #     """
    #     available_spots = self.available_spots_cache.get(coordinate)
    #     if available_spots is None:
    #         return None
    #     # check if the coordinate is still valid
    #     if self.coordinate != coordinate:
    #         # remove the coordinate from the cache
    #         del self.available_spots_cache[coordinate]
    #         return None
    #     return available_spots

    def filter_out_of_bound_spots(self, available_spots: list[AvailableSpot]) -> list[AvailableSpot]:
        """
        filters out-of-bound spots from the available spots.
        """
        return [
            spot
            for spot in available_spots
            if 0 <= spot.coordinate[0] < 8 and 0 <= spot.coordinate[1] < 8
        ]

    @abstractmethod
    def calculate_moves(
        self, board, color: str, coordinate: tuple[int, int], **kwargs
    ) -> list[AvailableSpot]:
        pass

    def find_available_spots(
        self, board, color: str, coordinate: tuple[int, int] | None = None, **kwargs
    ) -> list[AvailableSpot]:
        """
        Finds available spots a Piece can move to.

        Args:
            board (Board): The board to search for available spots.
            color (str): need to check if the piece is your piece or not (for catching moves).
            coordinate (tuple[int, int]): The coordinates of the piece to find available spots for.
            if not passed, the piece's current coordinate will be used.

        Returns:
            list[tuple[int, int]]: A list of coordinates of available spots.
        """
        coordinate = coordinate if coordinate else self.coordinate

        # # try hitting cache
        # if available_spots := self.get_from_cache(coordinate):
        #     return available_spots

        available_spots = self.calculate_moves(board, color, coordinate, **kwargs)
        available_spots = self.filter_out_of_bound_spots(available_spots)
        # # cache the result
        # self.available_spots_cache[coordinate] = available_spots
        return available_spots

    def __str__(self):
        return f"Piece(id={self.id}, color={self.color})"


class SpecialPiece(AbstractPiece):
    def __init__(self, image, player: "AbstractPlayer", coordinate: tuple[int, int]):
        super().__init__(image, player, coordinate)
        self.moves_count = 0

    @property
    def has_moved(self):
        return self.moves_count > 0


class Cell(AbstractDrawable):
    def __init__(
        self,
        image: pygame.Surface,
        coordinate: tuple[int, int],
        piece: AbstractPiece | SpecialPiece | None = None,
    ):
        """
        Initializes a Cell object with a given image, coordinate, and optional piece.

        Args:
            image (pygame.Surface): The image to be used for the cell.
            coordinate (tuple[int, int]): The row and column index of the cell on the board.
            piece (AbstractPiece | None): The piece to be placed on the cell, defaults to None
            **the cell object can modify its piece attribute** like
            changing its piece.coordinate or piece.rect
        """

        super().__init__(image)
        self.piece = piece
        self.coordinate = coordinate

    def is_empty(self):
        """returns True of cell contains a piece False otherwise.
        ```return self.piece is None```
        """
        return self.piece is None

    def set_coordinate(self, coordinate: tuple[int, int]):
        """
        set the coordinate of the cell
        if self.piece is not None **its gonna change the piece's coordinate and rect too**.

        Args:
            coordinate (tuple[int, int]): The new coordinate to set.
        """
        self.coordinate = coordinate
        self.rect.x = coordinate[0] * self.width
        self.rect.y = coordinate[1] * self.hight
        if self.piece is not None:
            self.piece.coordinate = coordinate
            self.piece.rect.x = self.rect.x
            self.piece.rect.y = self.rect.y

    def set_piece(self, piece: AbstractPiece | SpecialPiece):
        """set the piece of the cell and set the piece's coordinate to the cell's coordinate
        Args:
            piece (AbstractPiece): The piece to be placed on the cell.
        """
        piece.coordinate = self.coordinate
        self.piece = piece

    def rem_piece(self):
        """remove the piece from the cell and set the cell's piece to None"""
        self.piece = None

    @property
    def width(self):
        return self.image.get_width()

    @property
    def hight(self):
        return self.image.get_height()

    def __str__(self):
        return f"Cell(id={self.id}, coordinate={self.coordinate}, piece={self.piece})"


class Board(AbstractDrawable):
    CELL_COUNT = 8  # each chess board has 8 cells vertically and horizontally

    def __init__(self, image):
        super().__init__(image)
        logging.info("initializing board...")
        self.board: list[list[Cell]] = self._init_board()

    def _init_board(self) -> list[list[Cell]]:
        """creates and initializes Cell objects, sets their width, hight, x and y
        based on self.image, and fill self.board with them.
        """
        cell_width = cell_hight = self.image.get_width() // self.CELL_COUNT
        board = []
        for i in range(self.CELL_COUNT):
            row = []
            for j in range(self.CELL_COUNT):
                cell = Cell(
                    pygame.Surface(size=(cell_width, cell_hight)), coordinate=(i, j)
                )
                cell.rect.x = j * cell_width
                cell.rect.y = i * cell_width

                # aligning cells with board texture
                cell.rect.x += self.rect.x
                cell.rect.y += self.rect.y

                row.append(cell)
            board.append(row)
        # print(board)
        return board

    def copy(self):
        """
        return a copy of the board's current state;
        **not an exact copy** because the player attribute of pieces inside cells is
        a reference the the current objects player, meaning if you change anything in player,
        its gonna change in the copied object too.

        but if you wanna get an exact copy you can modify the abstracts.AbstractPiece.copy() method
        to set a copy of current objects player to the copied piece.

        Returns:
            board (Board): __description__
        """
        board = Board(self.image.copy())
        filled_cells = self.get_filled_cells()
        for cell in filled_cells:
            piece = cell.piece
            piece_copy = piece.copy()
            cell_copy = board.get_cell(*cell.coordinate)
            cell_copy.set_piece(piece_copy)
            piece_copy.rect.x = cell_copy.rect.x
            piece_copy.rect.y = cell_copy.rect.y
        return board

    # def rotate_180(self) -> "Board":
    #     """return a new board rotated 180 degrees."""
    #     filled_cells = self.get_filled_cells().copy()
    #     board = Board(self.image)
    #     for source_cell in filled_cells:
    #         new_coordinate = invert_coordinate(source_cell.coordinate, board)
    #         dest_cell = board.get_cell(*new_coordinate)
    #         dest_cell.set_piece(source_cell.piece)
    #         piece = dest_cell.piece
    #         piece.rect.x = piece.coordinate[0] * piece.image.get_width()
    #         piece.rect.y = piece.coordinate[1] * piece.image.get_height()
    #     return board

    def get_cell(self, i, j) -> Cell:
        """return a cell based on it's row and col index (i and j) on the self.board

        Args:
            i: int
            j: int
        Returns:
            Cell
        """
        cell = self.board[i][j]
        return cell

    def get_cell_by_coordinates(self, coordinates: tuple) -> Cell | None:
        """return index of a cell in self.board using provided coordinates
        so that cell can be accessed like board[r][c] -> Cell

        Returns:
            Cell
        """
        for i in range(self.CELL_COUNT):
            for j in range(self.CELL_COUNT):
                cell = self.board[i][j]
                if (cell.rect.x + cell.width >= coordinates[0] >= cell.rect.x) and (
                    cell.rect.y + cell.hight >= coordinates[1] >= cell.rect.y
                ):
                    return self.get_cell(i, j)
        return None

    def get_filled_cells(self) -> list[Cell]:
        """get cells that have a piece attached to them
        Returns:
            list[Cell]
        """
        cells = []
        for row in self.board:
            for cell in row:
                if not cell.is_empty():
                    cells.append(cell)
        return cells

    def __getitem__(self, i: SupportsIndex):
        return self.board[i]

    def __iter__(self):
        return iter(self.board)


class Pawn(SpecialPiece):
    def calculate_moves(
        self,
        board: Board,
        color: str,
        coordinate: tuple[int, int],
        **kwargs,
    ):
        """
        Args:
            board (Board, optional):
            coordinate (tuple[int, int], optional):
            **kwargs (optional):
        """
        opponent = kwargs.get("opponent", False)
        piece_i = coordinate[0]
        piece_j = coordinate[1]
        available_spots = []
        UP = -1
        DOWN = +1

        # the direction can also be used for horizontal movements
        if not opponent:
            vertical_direction = UP if self.is_my_piece(color) else DOWN
        else:
            vertical_direction = DOWN if self.is_my_piece(color) else UP

        # normal moves (either up or down)
        if board.CELL_COUNT > piece_i + vertical_direction >= 0:
            if board.get_cell(piece_i + vertical_direction, piece_j).piece is None:
                available_spots.append(
                    AvailableSpot((piece_i + vertical_direction, piece_j))
                )
                # Double move
                if (
                    (not opponent and vertical_direction == UP)
                    or (opponent and vertical_direction == UP)
                ) and (piece_i == 6):
                    available_spots.append(
                        AvailableSpot((piece_i + 2 * vertical_direction, piece_j))
                    )
                elif (
                    (not opponent and vertical_direction == DOWN)
                    or (opponent and vertical_direction == DOWN)
                ) and (piece_i == 1):
                    available_spots.append(
                        AvailableSpot((piece_i + 2 * vertical_direction, piece_j))
                    )

            horizontal_directions = [+1, -1]
            for horizontal_direction in horizontal_directions:
                # diagonal moves (either downside or upside)
                if not board.CELL_COUNT > piece_j + horizontal_direction >= 0:
                    continue
                cell = board.get_cell(
                    piece_i + vertical_direction, piece_j + horizontal_direction
                )
                if cell.piece is not None and cell.piece.color != color:
                    available_spots.append(
                        AvailableSpot(
                            (
                                piece_i + vertical_direction,
                                piece_j + horizontal_direction,
                            )
                        )
                    )

                # en passant
                print("while handling en-passant...")
                print(f"piece_i: {piece_i}, piece_j: {piece_j}")
                if piece_i == 3 or piece_i == 4:
                    side_cell = board.get_cell(piece_i, piece_j + horizontal_direction)
                    dest_coordinate = (
                        piece_i + vertical_direction,
                        piece_j + horizontal_direction,
                    )
                    dest_cell = board.get_cell(*dest_coordinate)
                    if side_cell.is_empty():
                        continue
                    if not dest_cell.is_empty():
                        continue
                    if not isinstance(side_cell.piece, Pawn):
                        continue
                    print(f"side_cell.piece: {side_cell.piece}")
                    print(
                        f"can piece has_done_1_move?: {side_cell.piece.moves_count == 1}"
                    )
                    if not side_cell.piece.moves_count == 1:
                        continue
                    if side_cell.piece.color == color:
                        continue
                    available_spots.append(
                        AvailableSpot(
                            dest_coordinate,
                            is_en_passant=True,
                            target_cell=side_cell,
                        )
                    )

        return available_spots


class Rook(SpecialPiece):
    def calculate_moves(
        self,
        board: Board,
        color: str,
        coordinate: tuple[int, int],
        **kwargs,
    ):
        piece_i = coordinate[0]
        piece_j = coordinate[1]
        available_spots = []

        for j in range(piece_j + 1, board.CELL_COUNT):  # right
            # print(f"going right: {piece_i, j}")
            cell = board.get_cell(piece_i, j)
            if cell.piece is not None:
                if cell.piece.color != color:
                    available_spots.append(AvailableSpot((piece_i, j)))
                    break
                # handle castling move
                elif not isinstance(cell.piece, King):
                    break
                elif cell.piece.has_moved or self.has_moved:
                    break
                spot = AvailableSpot((piece_i, j), is_castling=True, target_cell=cell)
                spot.castling_set_details(rook_new_pos=(piece_i, j - 2), king_new_pos=(piece_i, j + 1))
                available_spots.append(spot)
                break
            available_spots.append(AvailableSpot((piece_i, j)))

        for j in range(piece_j - 1, -1, -1):  # left
            # print(f"going left: {piece_i, j}")
            cell = board.get_cell(piece_i, j)
            if cell.piece is not None:
                if cell.piece.color != color:
                    available_spots.append(AvailableSpot((piece_i, j)))
                    break
                # handle castling move
                elif not isinstance(cell.piece, King):
                    break
                elif cell.piece.has_moved or self.has_moved:
                    break
                spot = AvailableSpot((piece_i, j), is_castling=True, target_cell=cell)
                spot.set_castling_details(
                    rook_new_pos=(piece_i, j + 2), king_new_pos=(piece_i, j - 1)
                )
                available_spots.append(spot)
                break
            available_spots.append(AvailableSpot((piece_i, j)))

        for i in range(piece_i + 1, board.CELL_COUNT):  # down
            # print(f"going downwards: {i, piece_j}")
            cell = board.get_cell(i, piece_j)
            if cell.piece is not None:
                if cell.piece.color != color:
                    available_spots.append(AvailableSpot((i, piece_j)))
                break
            available_spots.append(AvailableSpot((i, piece_j)))

        for i in range(piece_i - 1, -1, -1):  # up
            # print(f"going upwards: {i, piece_j}")
            cell = board.get_cell(i, piece_j)
            if cell.piece is not None:
                if cell.piece.color != color:
                    available_spots.append(AvailableSpot((i, piece_j)))
                break
            available_spots.append(AvailableSpot((i, piece_j)))

        return available_spots


class Knight(AbstractPiece):
    def calculate_moves(
        self,
        board: Board,
        color: str,
        coordinate: tuple[int, int],
        **kwargs,
    ):
        piece_i = coordinate[0]
        piece_j = coordinate[1]

        available_spots = []
        for i in [-2, 2]:
            for j in [-1, 1]:
                # prevent IndexOutOfRange
                if (
                    (piece_i + i < 0 or piece_i + i >= board.CELL_COUNT)
                    or (piece_j + j < 0 or piece_j + j >= board.CELL_COUNT)
                    or (piece_j - j < 0 or piece_j - j >= board.CELL_COUNT)
                ):
                    continue
                cell = board.get_cell(piece_i + i, piece_j + j)
                cell2 = board.get_cell(piece_i + i, piece_j - j)
                if (cell.piece is None) or cell.piece.color != color:
                    available_spots.append(AvailableSpot((piece_i + i, piece_j + j)))
                if (cell2.piece is None) or cell2.piece.color != color:
                    available_spots.append(AvailableSpot((piece_i + i, piece_j - j)))
        for i in [-1, 1]:
            for j in [-2, 2]:
                # prevent IndexOutOfRange
                if (
                    (piece_i + i < 0 or piece_i + i >= board.CELL_COUNT)
                    or (piece_j + j < 0 or piece_j + j >= board.CELL_COUNT)
                    or (piece_i - i < 0 or piece_i - i >= board.CELL_COUNT)
                ):
                    continue
                cell = board.get_cell(piece_i + i, piece_j + j)
                cell2 = board.get_cell(piece_i - i, piece_j + j)
                if (cell.piece is None) or cell.piece.color != color:
                    available_spots.append(AvailableSpot((piece_i + i, piece_j + j)))
                if (cell2.piece is None) or cell2.piece.color != color:
                    available_spots.append(AvailableSpot((piece_i - i, piece_j + j)))

        return available_spots


class Bishop(AbstractPiece):
    def calculate_moves(
        self,
        board: Board,
        color: str,
        coordinate: tuple[int, int],
        **kwargs,
    ):
        piece_i = coordinate[0]
        piece_j = coordinate[1]
        available_spots = []
        # example usage for `completed_directions` variable:
        # in the loop below when we iterate through directions and encounter a filled cell
        # we can add the cell to available_spots and add that direction to this set this helps us to
        # prevent going through the same direction again
        completed_directions = set()
        for i in range(1, board.CELL_COUNT):
            up_left = piece_i - i, piece_j - i
            up_right = piece_i - i, piece_j + i
            down_left = piece_i + i, piece_j - i
            down_right = piece_i + i, piece_j + i
            directions = (up_left, up_right, down_left, down_right)
            for i in range(len(directions)):
                direction = directions[i]
                if i in completed_directions:
                    continue
                if direction[0] < 0 or direction[0] >= board.CELL_COUNT:
                    continue
                if direction[1] < 0 or direction[1] >= board.CELL_COUNT:
                    continue
                cell = board.get_cell(*direction)
                if cell.piece is not None:
                    if cell.piece.color != color:
                        available_spots.append(AvailableSpot(direction))
                    completed_directions.add(i)
                    continue
                available_spots.append(AvailableSpot(direction))

        return available_spots


class Queen(AbstractPiece):
    def calculate_moves(
        self,
        board: Board,
        color: str,
        coordinate: tuple[int, int],
        **kwargs,
    ):
        piece_i = coordinate[0]
        piece_j = coordinate[1]
        available_spots = []

        for j in range(piece_j + 1, board.CELL_COUNT):  # right
            # print(f"going right: {piece_i, j}")
            cell = board.get_cell(piece_i, j)
            if cell.piece is not None:
                if cell.piece.color != color:
                    available_spots.append(AvailableSpot((piece_i, j)))
                break
            available_spots.append(AvailableSpot((piece_i, j)))

        for j in range(piece_j - 1, -1, -1):  # left
            # print(f"going left: {piece_i, j}")
            cell = board.get_cell(piece_i, j)
            if cell.piece is not None:
                if cell.piece.color != color:
                    available_spots.append(AvailableSpot((piece_i, j)))
                break
            available_spots.append(AvailableSpot((piece_i, j)))

        for i in range(piece_i + 1, board.CELL_COUNT):  # down
            # print(f"going downwards: {i, piece_j}")
            cell = board.get_cell(i, piece_j)
            if cell.piece is not None:
                if cell.piece.color != color:
                    available_spots.append(AvailableSpot((i, piece_j)))
                break
            available_spots.append(AvailableSpot((i, piece_j)))

        for i in range(piece_i - 1, -1, -1):  # up
            # print(f"going upwards: {i, piece_j}")
            cell = board.get_cell(i, piece_j)
            if cell.piece is not None:
                if cell.piece.color != color:
                    available_spots.append(AvailableSpot((i, piece_j)))
                break
            available_spots.append(AvailableSpot((i, piece_j)))

        # diagonal moves
        completed_directions = set()
        for i in range(1, board.CELL_COUNT):
            up_left = piece_i - i, piece_j - i
            up_right = piece_i - i, piece_j + i
            down_left = piece_i + i, piece_j - i
            down_right = piece_i + i, piece_j + i
            directions = (up_left, up_right, down_left, down_right)
            for i in range(len(directions)):
                direction = directions[i]
                if i in completed_directions:
                    continue
                if direction[0] < 0 or direction[0] >= board.CELL_COUNT:
                    continue
                if direction[1] < 0 or direction[1] >= board.CELL_COUNT:
                    continue
                cell = board.get_cell(*direction)
                if cell.piece is not None:
                    if cell.piece.color != color:
                        available_spots.append(AvailableSpot(direction))
                    completed_directions.add(i)
                    continue
                available_spots.append(AvailableSpot(direction))
        return available_spots


class King(SpecialPiece):
    def calculate_moves(
        self,
        board: Board,
        color: str,
        coordinate: tuple[int, int],
        **kwargs,
    ):
        piece_i = coordinate[0]
        piece_j = coordinate[1]
        available_spots = []

        UP = (piece_i - 1, piece_j)
        DOWN = (piece_i + 1, piece_j)
        LEFT = (piece_i, piece_j - 1)
        RIGHT = (piece_i, piece_j + 1)
        UP_LEFT = (piece_i - 1, piece_j - 1)
        UP_RIGHT = (piece_i - 1, piece_j + 1)
        DOWN_LEFT = (piece_i + 1, piece_j - 1)
        DOWN_RIGHT = (piece_i + 1, piece_j + 1)
        directions = [UP, DOWN, LEFT, RIGHT, UP_LEFT, UP_RIGHT, DOWN_LEFT, DOWN_RIGHT]
        for direction in directions:
            if direction[0] < 0 or direction[0] >= board.CELL_COUNT:
                continue
            if direction[1] < 0 or direction[1] >= board.CELL_COUNT:
                continue
            cell = board.get_cell(*direction)
            if cell.piece is not None:
                if cell.piece.color != color:
                    available_spots.append(AvailableSpot(direction))
                continue
            available_spots.append(AvailableSpot(direction))

        return available_spots


string_to_piece_class = {
    "pawn": Pawn,
    "rook": Rook,
    "knight": Knight,
    "bishop": Bishop,
    "queen": Queen,
    "king": King,
}


def get_board(
    texture_pack: TexturePack, player1: "AbstractPlayer", player2: "AbstractPlayer"
) -> Board:
    """
    Create a board with pieces for two players.

    Args:
        texture_pack: texture pack to get textures from
        player1: first player (you)
        player2: second player (your opponent)

    Returns:
        Board: a board with pieces for player1 and player2
    """

    board_texture = texture_pack.get_texture(
        settings.TEXTURE_NAMES["board"], settings.BOARD_WIDTH_HIGHT
    )
    board = Board(image=board_texture)

    # attaching pieces
    piece_positions = settings.get_piece_positions(player1)
    for piece_name in piece_positions.keys():
        piece_texture = texture_pack.get_texture(
            settings.TEXTURE_NAMES[piece_name], settings.PIECE_WIDTH_HIGHT
        )
        Piece = string_to_piece_class[piece_name[2:]]
        player = player1 if player1.color[0] == piece_name[0] else player2

        for pos in piece_positions[piece_name]:
            cell = board.get_cell(*pos)
            piece = Piece(piece_texture, player, pos)
            piece.rect.x = cell.rect.x
            piece.rect.y = cell.rect.y
            cell.set_piece(piece)
    return board


basic_board_instance = Board(pygame.Surface((settings.HIGHT, settings.HIGHT)))

# testing
if __name__ == "__main__":
    import pygame
    from texture_loader import TexturePackLoader
    from player import Player
    from input_sources import Human
    from helpers import create_simple_square_sprite

    texturepackloader = TexturePackLoader(settings.TEXTURE_DIR)
    pack = texturepackloader.get_pack(settings.DEFAULT_TEXTURE_PACK)

    screen = pygame.display.set_mode((settings.WIDTH, settings.HIGHT))

    image = pack.get_texture(settings.TEXTURE_NAMES["board"])
    image = pygame.transform.scale(image, (settings.HIGHT, settings.HIGHT))
    player1 = Player(
        name="Player 1",
        color="white",
        input_source=Human(),
    )
    player2 = Player(
        name="Player 2",
        color="black",
        input_source=Human(),
    )
    board = Board(image)
    board[3][1].set_piece(
        Pawn(
            pack.get_texture(
                settings.TEXTURE_NAMES["b_pawn"], size=settings.PIECE_WIDTH_HIGHT
            ),
            player2,
            (3, 1),
        )
    )
    pawn = Pawn(
        pack.get_texture(
            settings.TEXTURE_NAMES["w_pawn"], size=settings.PIECE_WIDTH_HIGHT
        ),
        player1,
        (3, 0),
    )
    board[3][0].set_piece(pawn)
    RUN = True
    available_cells_to_draw = []
    while RUN:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if available_cells_to_draw:
                    available_cells_to_draw.clear()
                    break
                mouse_pos = pygame.mouse.get_pos()
                cell = board.get_cell_by_coordinates(mouse_pos)
                if cell:
                    if cell.piece:
                        print(cell.piece)
                        available_spots = cell.piece.find_available_spots(
                            board, color=cell.piece.color
                        )
                        print(f"Available spots for {cell.piece}: {available_spots}")
                        for spot in available_spots:
                            cell = board.get_cell(*spot.coordinate)
                            surface = create_simple_square_sprite(
                                cell.width, cell.hight, "black", cell.rect
                            )
                            available_cells_to_draw.append(surface)
                    else:
                        print("empty cell")

        screen.blit(board.image, board.rect)
        for cell in board.get_filled_cells():
            screen.blit(cell.piece.image, cell.piece.rect)
        for cell in available_cells_to_draw:
            screen.blit(cell.image, cell.rect)
        pygame.display.update()
