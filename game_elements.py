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
        self, board: Board, color: str, coordinate: tuple[int, int] | None = None, **kwargs
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
            direction = UP if self.is_my_piece(color) else DOWN
        else:
            direction = DOWN if self.is_my_piece(color) else UP

        # normal moves (either up or down)
        if (board.CELL_COUNT > piece_i + direction >= 0):
            if board.get_cell(piece_i + direction, piece_j).piece is None:
                available_spots.append((piece_i + direction, piece_j))
                # Double move
                if (
                    (not opponent and direction == UP) or (opponent and direction == UP)
                ) and (piece_i == 6):
                    available_spots.append((piece_i + 2 * direction, piece_j))
                elif (
                    (not opponent and direction == DOWN) or (opponent and direction == DOWN)
                ) and (piece_i == 1):
                    available_spots.append((piece_i + 2 * direction, piece_j))
            
            # diagonal moves (either downside or upside)
            if board.CELL_COUNT > piece_j + 1 >= 0:
                cell = board.get_cell(piece_i + direction, piece_j + 1)
                if cell.piece is not None and cell.piece.color != color:
                    available_spots.append((piece_i + direction, piece_j + 1))
            if board.CELL_COUNT > piece_j - 1 >= 0:
                cell = board.get_cell(piece_i + direction, piece_j - 1)
                if cell.piece is not None and cell.piece.color != color:
                    available_spots.append((piece_i + direction, piece_j - 1))

        # filter out-of-bound/invalid spots:
        available_spots = [
            spot
            for spot in available_spots
            if (0 <= spot[0] < board.CELL_COUNT) and (0 <= spot[1] < board.CELL_COUNT)
        ]
        return available_spots


class Rook(AbstractPiece):
    def calculate_moves(
        self, board: Board, color: str, coordinate: tuple[int, int] | None = None, **kwargs
    ):
        piece_i = coordinate[0]
        piece_j = coordinate[1]
        available_spots = []

        for j in range(piece_j + 1, board.CELL_COUNT): # right
            print(f"going right: {piece_i, j}")
            cell = board.get_cell(piece_i , j)
            if cell.piece is not None:
                if cell.piece.color != color:
                    available_spots.append((piece_i, j))
                break
            available_spots.append((piece_i, j))

        for j in range(piece_j - 1, -1, -1): # left
            print(f"going left: {piece_i, j}")
            cell = board.get_cell(piece_i, j)
            if cell.piece is not None:
                if cell.piece.color != color:
                    available_spots.append((piece_i, j))
                break
            available_spots.append((piece_i, j))
            
        for i in range(piece_i + 1, board.CELL_COUNT): # down
            print(f"going downwards: {i, piece_j}")
            cell = board.get_cell(i, piece_j)
            if cell.piece is not None:
                if cell.piece.color != color:
                    available_spots.append((i, piece_j))
                break
            available_spots.append((i, piece_j))

        for i in range(piece_i - 1, -1, -1): # up
            print(f"going upwards: {i, piece_j}")
            cell = board.get_cell(i, piece_j)
            if cell.piece is not None:
                if cell.piece.color != color:
                    available_spots.append((i, piece_j))
                break
            available_spots.append((i, piece_j))

        return available_spots


class Knight(AbstractPiece):
    def calculate_moves(
        self,
        board: Board,
        color: str,
        coordinate: tuple[int, int] | None = None,
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
                    available_spots.append((piece_i + i, piece_j + j))
                if (cell2.piece is None) or cell2.piece.color!=color:
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
                cell = board.get_cell(piece_i + i, piece_j + j)
                cell2 = board.get_cell(piece_i - i, piece_j + j)
                if (cell.piece is None) or cell.piece.color != color:
                    available_spots.append((piece_i + i, piece_j + j))
                if (cell2.piece is None) or cell2.piece.color != color:
                    available_spots.append((piece_i - i, piece_j + j))

        return available_spots


class Bishop(AbstractPiece):
    def calculate_moves(
        self,
        board: Board,
        color: str,
        coordinate: tuple[int, int] | None = None,
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

        # filter out of bound spots:
        available_spots = [
            spot
            for spot in available_spots
            if (0 <= spot[0] < board.CELL_COUNT) and (0 <= spot[1] < board.CELL_COUNT)
        ]

        return available_spots


class Queen(AbstractPiece):
    def calculate_moves(
        self,
        board: Board,
        color:str,
        coordinate: tuple[int, int] | None = None,
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

        # filter out of bound spots:
        available_spots = [
            spot
            for spot in available_spots
            if (0 <= spot[0] < board.CELL_COUNT) and (0 <= spot[1] < board.CELL_COUNT)
        ]

        # HORIZONTAL AND VERTICAL MOVES
        for i in range(piece_i):  # left
            available_spots.append((i, piece_j))
        for i in range(piece_i + 1, board.CELL_COUNT):  # right
            available_spots.append((i, piece_j))
        for j in range(piece_j):  # up
            available_spots.append((piece_i, j))
        for j in range(piece_j + 1, board.CELL_COUNT):  # down
            available_spots.append((piece_i, j))
        return available_spots


class King(AbstractPiece):
    def calculate_moves(
        self,
        board: Board,
        color: str,
        coordinate: tuple[int, int] | None = None,
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
    from player import Player
    from input_sources import Human

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
    board[7][7].set_piece(
        Rook(
            pack.get_texture(settings.TEXTURE_NAMES["b_rook"], size=settings.PIECE_WIDTH_HIGHT),
            player2,
            (7, 7),
        ).set_coordinate((7, 7))
    )
    board[0][0].set_piece(
        Rook(
            pack.get_texture(settings.TEXTURE_NAMES["w_rook"], size=settings.PIECE_WIDTH_HIGHT),
            player1,
            (0, 0),
        ).set_coordinate((0, 0))
    )
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
                    if cell.piece:
                        print(cell.piece)
                    else:
                        print("empty cell")
                    available_spots = cell.piece.find_available_spots(
                        board, color=cell.piece.color
                    )
                    print(f"Available spots for {cell.piece}: {available_spots}")

        screen.blit(board.image, board.rect)
        for cell in board.get_filled_cells():
            screen.blit(cell.piece.image, cell.piece.rect)
        pygame.display.update()
