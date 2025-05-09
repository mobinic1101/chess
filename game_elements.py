from typing import SupportsIndex
import logging
import pygame
from abstracts import AbstractDrawable, AbstractPiece, AbstractPlayer
from texture_loader import TexturePack
import settings
# from helpers import invert_coordinate


class Cell(AbstractDrawable):
    def __init__(
        self,
        image: pygame.Surface,
        coordinate: tuple[int, int],
        piece: AbstractPiece | None = None,
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
        # modifying self.piece
        if self.piece is not None:
            self.piece.coordinate = coordinate
            self.piece.rect.x = self.rect.x
            self.piece.rect.y = self.rect.y

    def set_piece(self, piece: AbstractPiece):
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
    CELL_COUNT = 8  # each chess board has 8 cells vertically and horizantally

    def __init__(self, image):
        super().__init__(image)
        logging.info("initializing board...")
        # board is a 2D list
        self.board: list[list[Cell]] = self._init_board()

    def _init_board(self) -> list[list[Cell]]:
        """creates and initializes Cell objects, sets their width, hight, x and y
        based on self.image, and fill self.board with them.
        """
        # divide board width and hight to 8 equal cells,
        # set the cell width and hight based on the result of division.
        cell_width = cell_hight = self.image.get_width() // self.CELL_COUNT
        board = []
        cell_id = 1
        for i in range(self.CELL_COUNT):
            row = []
            for j in range(self.CELL_COUNT):
                cell = Cell(
                    pygame.Surface(size=(cell_width, cell_hight)), coordinate=(i, j)
                )
                cell.rect.x = i * cell_width
                cell.rect.y = j * cell_width

                # aligning cells with board texture
                cell.rect.x += self.rect.x
                cell.rect.y += self.rect.y

                cell_id += 1
                row.append(cell)
            board.append(row)
        # print(board)
        return board

    def copy(self):
        """
        return a copy of the board's current state;
        **not an exact copy** because the player attribute of pieces inside cells is
        a reference the the current objects player, meanning if you change anything in player,
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

    def get_cell_by_coordinates(self, coordinates: tuple) -> tuple[int, int] | None:
        """return index of a cell in self.board using provided coordinates
        so that cell can be accessed like board[r][c] -> Cell

        Returns:
            tuple[int, int]
        """
        for i in range(self.CELL_COUNT):
            for j in range(self.CELL_COUNT):
                cell = self.board[i][j]
                if (cell.rect.x + cell.width >= coordinates[0] >= cell.rect.x) and (
                    cell.rect.y + cell.hight >= coordinates[1] >= cell.rect.y
                ):
                    return i, j
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


class Pawn(AbstractPiece):
    def calculate_moves(
        self, board: Board, coordinate: tuple[int, int] | None = None, **kwargs
    ):
        """
        Args:
            board (Board, optional):
            coordinate (tuple[int, int], optional):
            **kwargs: a color should be passed here to determine if the piece is white or black
        """
        if kwargs.get("color") is None:
            raise ValueError(
                "color should be passed to determine if the piece is white or black, HINT: pass the player1 (your player) color."
            )

        piece_i = coordinate[0]
        piece_j = coordinate[1]
        available_spots = []

        if self.is_my_piece(kwargs["color"]):
            # Normal moves (moving forward)
            if piece_j > 0 and board[piece_i][piece_j - 1].is_empty():
                available_spots.append((piece_i, piece_j - 1))
                # Double move if on starting position
                if piece_j == 6 and board[piece_i][piece_j - 2].is_empty():
                    available_spots.append((piece_i, piece_j - 2))

            # Capturing moves (diagonal moves)
            if piece_j > 0:
                if piece_i - 1 >= 0:  # Left diagonal
                    if not board[piece_i - 1][piece_j - 1].is_empty() and not board[
                        piece_i - 1
                    ][piece_j - 1].piece.is_my_piece(kwargs["color"]):
                        available_spots.append((piece_i - 1, piece_j - 1))
                if piece_i + 1 < board.CELL_COUNT:  # Right diagonal
                    if not board[piece_i + 1][piece_j - 1].is_empty() and not board[
                        piece_i + 1
                    ][piece_j - 1].piece.is_my_piece(kwargs["color"]):
                        available_spots.append((piece_i + 1, piece_j - 1))
        else:
            # Normal moves (moving forward)
            if (
                piece_j < board.CELL_COUNT - 1
                and board[piece_i][piece_j + 1].is_empty()
            ):
                available_spots.append((piece_i, piece_j + 1))
                # Double move if on starting position
                if piece_j == 1 and board[piece_i][piece_j + 2].is_empty():
                    available_spots.append((piece_i, piece_j + 2))

            # Capturing moves (diagonal moves)
            if piece_j < board.CELL_COUNT - 1:
                if piece_i - 1 >= 0:  # Left diagonal
                    if not board[piece_i - 1][piece_j + 1].is_empty() and board[
                        piece_i - 1
                    ][piece_j + 1].piece.is_my_piece(kwargs["color"]):
                        available_spots.append((piece_i - 1, piece_j + 1))
                if piece_i + 1 < board.CELL_COUNT:  # Right diagonal
                    if not board[piece_i + 1][piece_j + 1].is_empty() and board[
                        piece_i + 1
                    ][piece_j + 1].piece.is_my_piece(kwargs["color"]):
                        available_spots.append((piece_i + 1, piece_j + 1))

        return available_spots


class Rook(AbstractPiece):
    def calculate_moves(
        self,
        board: Board,
        coordinate: tuple[int, int] | None = None,
        _all=False,
        **kwargs,
    ):
        piece_i = coordinate[0]
        piece_j = coordinate[1]
        available_spots = []
        for i in range(piece_i):
            available_spots.append((i, piece_j))
        for i in range(piece_i + 1, board.CELL_COUNT):
            available_spots.append((i, piece_j))
        for j in range(piece_j):
            available_spots.append((piece_i, j))
        for j in range(piece_j + 1, board.CELL_COUNT):
            available_spots.append((piece_i, j))

        self.available_spots_cache[coordinate] = available_spots
        return available_spots


class Knight(AbstractPiece):
    def calculate_moves(
        self,
        board: Board,
        coordinate: tuple[int, int] | None = None,
        _all=False,
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

                available_spots.append((piece_i + i, piece_j + j))
                available_spots.append((piece_i + i, piece_j - j))
        for i in [-1, 1]:
            for j in [-2, 2]:
                # prevent IndexOutOfRange
                if (
                    (piece_i + i < 0 or piece_i + i >= board.CELL_COUNT)
                    or (piece_j + j < 0 or piece_j + j >= board.CELL_COUNT)
                    or (piece_i - i < 0 or piece_i - i >= board.CELL_COUNT)
                ):
                    continue

                available_spots.append((piece_i + i, piece_j + j))
                available_spots.append((piece_i - i, piece_j + j))

        self.available_spots_cache[coordinate] = available_spots
        return available_spots


class Bishop(AbstractPiece):
    def calculate_moves(
        self,
        board: Board,
        coordinate: tuple[int, int] | None = None,
        _all=False,
        **kwargs,
    ):
        piece_i = coordinate[0]
        piece_j = coordinate[1]
        available_spots = []
        for i in range(1, board.CELL_COUNT):
            available_spots.append((piece_i - i, piece_j - i))  # diagonal up left
            available_spots.append((piece_i + i, piece_j - i))  # diagonal up right
            available_spots.append((piece_i - i, piece_j + i))  # diagonal down left
            available_spots.append((piece_i + i, piece_j + i))  # diagonal down left

        # finter out of bound spots:
        available_spots = [
            spot
            for spot in available_spots
            if (0 <= spot[0] < board.CELL_COUNT) and (0 <= spot[1] < board.CELL_COUNT)
        ]

        self.available_spots_cache[coordinate] = available_spots
        return available_spots


class Queen(AbstractPiece):
    def calculate_moves(
        self,
        board: Board,
        coordinate: tuple[int, int] | None = None,
        _all=False,
        **kwargs,
    ):
        piece_i = coordinate[0]
        piece_j = coordinate[1]
        available_spots = []
        for i in range(1, board.CELL_COUNT):  # DIAGONAL
            available_spots.append((piece_i - i, piece_j - i))  # up left
            available_spots.append((piece_i + i, piece_j - i))  # up right
            available_spots.append((piece_i - i, piece_j + i))  # down left
            available_spots.append((piece_i + i, piece_j + i))  # down left

        # finter out of bound spots:
        available_spots = [
            spot
            for spot in available_spots
            if (0 <= spot[0] < board.CELL_COUNT) and (0 <= spot[1] < board.CELL_COUNT)
        ]

        # HORIZENTAL
        for i in range(piece_i):  # left
            available_spots.append((i, piece_j))
        for i in range(piece_i + 1, board.CELL_COUNT):  # right
            available_spots.append((i, piece_j))
        for j in range(piece_j):  # up
            available_spots.append((piece_i, j))
        for j in range(piece_j + 1, board.CELL_COUNT):  # down
            available_spots.append((piece_i, j))
        self.available_spots_cache[coordinate] = available_spots
        return available_spots


class King(AbstractPiece):
    def calculate_moves(
        self,
        board: Board,
        coordinate: tuple[int, int] | None = None,
        _all=False,
        **kwargs,
    ):
        piece_i = coordinate[0]
        piece_j = coordinate[1]
        available_spots = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                # prevent IndexOutOfRange
                if (piece_i + i < 0 or piece_i + i >= board.CELL_COUNT) or (
                    piece_j + j < 0 or piece_j + j >= board.CELL_COUNT
                ):
                    continue

                available_spots.append((piece_i + i, piece_j + j))

        self.available_spots_cache[coordinate] = available_spots
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
    texture_pack: TexturePack, player1: AbstractPlayer, player2: AbstractPlayer
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

    texturepackloader = TexturePackLoader(settings.TEXTURE_DIR)
    pack = texturepackloader.get_pack(settings.DEFAULT_TEXTURE_PACK)

    screen = pygame.display.set_mode((settings.WIDTH, settings.HIGHT))

    image = pack.get_texture(settings.TEXTURE_NAMES["board"])
    image = pygame.transform.scale(image, (settings.HIGHT, settings.HIGHT))
    board = Board(image)
    RUN = True
    while RUN:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                rowcol = board.get_cell_by_coordinates(mouse_pos)
                if rowcol:
                    i, j = rowcol
                    cell = board[i][j]
                    cell.image.fill("black")
                    board.image.blit(cell.image, cell.rect)

        screen.blit(board.image, board.rect)
        pygame.display.update()
