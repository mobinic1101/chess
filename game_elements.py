import pygame
from typing import SupportsIndex
import logging
from abstracts import AbstractDrawable, AbstractPiece


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
            piece (AbstractPiece | None): The piece to be placed on the cell, defaults to None.
        """

        super().__init__(image)
        self.piece = piece
        self.coordinate = coordinate

    def is_empty(self):
        """returns True of cell contains a piece False otherwise.
        ```return self.piece is None```
        """
        return self.piece is None

    def set_piece(self, piece: AbstractPiece):
        self.piece = piece

    def rem_piece(self):
        self.piece = None

    @property
    def width(self):
        return self.image.get_width()

    @property
    def hight(self):
        return self.image.get_height()

    def __str__(self):
        return f"Cell(id={self.id}, piece={self.piece})"


class Board(AbstractDrawable):
    CELL_COUNT = 8  # each chess board has 8 cells vertically and horizantally

    def __init__(self, image):
        super().__init__(image)
        logging.info("initializing board...")
        self.board = self._init_board()

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

    def __getitem__(self, i: SupportsIndex):
        return self.board[i]

    def __iter__(self):
        return iter(self.board)


class Pawn(AbstractPiece):
    def find_available_spots(
        self, board: Board = None, coordinate: tuple[int, int] = None
    ):
        coordinate = self.coordinate if not coordinate else coordinate

        # try using the cache
        available_spots = self.available_spots_cache.get(coordinate)
        if available_spots:
            return available_spots

        piece_i = coordinate[0]
        piece_j = coordinate[1]
        available_spots = []
        if self.is_my_piece():
            if piece_j == 6:
                available_spots.append((piece_i, piece_j - 1))
                available_spots.append((piece_i, piece_j - 2))
            else:
                available_spots.append((piece_i, piece_j - 1))

            if not board[piece_i - 1][piece_j - 1].is_empty():
                available_spots.append((piece_i - 1, piece_j - 1))
            if not board[piece_i + 1][piece_j - 1].is_empty():
                available_spots.append((piece_i + 1, piece_j - 1))
        else:
            if piece_j == 1:
                available_spots.append((piece_i, piece_j + 1))
                available_spots.append((piece_i, piece_j + 2))
            else:
                available_spots.append((piece_i, piece_j + 1))

            if not board[piece_i - 1][piece_j + 1].is_empty():
                available_spots.append((piece_i - 1, piece_j + 1))
            if not board[piece_i + 1][piece_j + 1].is_empty():
                available_spots.append((piece_i + 1, piece_j + 1))

        # filtering available_spots that are out of bounds
        available_spots = [
            spot
            for spot in available_spots
            if 0 <= spot[0] < self.CELL_COUNT and 0 <= spot[1] < self.CELL_COUNT
        ]
        self.available_spots_cache[coordinate] = available_spots
        return available_spots


class Rook(AbstractPiece):
    def find_available_spots(self, board: Board, coordinate: tuple[int, int] = None):
        coordinate = coordinate if coordinate else self.coordinate

        # try using the cache
        available_spots = self.available_spots_cache.get(coordinate)
        if available_spots:
            return available_spots

        piece_i = coordinate[0]
        piece_j = coordinate[1]
        available_spots = []
        for i in range(piece_i):
            available_spots.append((i, piece_j))
        for i in range(piece_i + 1, self.CELL_COUNT):
            available_spots.append((i, piece_j))
        for j in range(piece_j):
            available_spots.append((piece_i, j))
        for j in range(piece_j + 1, self.CELL_COUNT):
            available_spots.append((piece_i, j))

        self.available_spots_cache[coordinate] = available_spots
        return available_spots


class Knight(AbstractPiece):
    def find_available_spots(self, board: Board, coordiante: tuple[int, int] = None):
        coordinate = coordinate if coordinate else self.coordinate

        # try using the cache
        available_spots = self.available_spots_cache.get(coordinate)
        if available_spots:
            return available_spots

        piece_i = coordinate[0]
        piece_j = coordinate[1]

        available_spots = []
        for i in [-2, 2]:
            for j in [-1, 1]:
                # prevent IndexOutOfRange
                if (piece_i + i < 0 or piece_i + i >= self.CELL_COUNT) or (
                    piece_j + j < 0 or piece_j + j >= self.CELL_COUNT):
                    continue

                available_spots.append((piece_i + i, piece_j + j))
                available_spots.append((piece_i + i, piece_j - j))
        for i in [-1, 1]:
            for j in [-2, 2]:
                # prevent IndexOutOfRange
                if (piece_i + i < 0 or piece_i + i >= self.CELL_COUNT) or (
                    piece_j + j < 0 or piece_j + j >= self.CELL_COUNT):
                    continue
                
                available_spots.append((piece_i + i, piece_j + j))
                available_spots.append((piece_i - i, piece_j + j))

        self.available_spots_cache[coordinate] = available_spots
        return available_spots


class Bishop(AbstractPiece):
    def find_available_spots(self, board: Board, coordinate: tuple[int, int] = None):
        coordinate = coordinate if coordinate else self.coordinate

        available_spots = self.available_spots_cache.get(coordinate)
        if available_spots:
            return available_spots
            
        piece_i = coordinate[0]
        piece_j = coordinate[1]
        for i in range(1, board.CELL_COUNT):

            # optimize the loop
            if (piece_i - i < 0 or piece_i - i >= self.CELL_COUNT) or (
                piece_j - i < 0 or piece_j - i >= self.CELL_COUNT):
                continue

            available_spots.append((piece_i - i, piece_j - i)) # diagonal up left
            available_spots.append((piece_i + i, piece_j - i)) # diagonal up right
            available_spots.append((piece_i - i, piece_j + i)) # diagonal down left
            available_spots.append((piece_i + i, piece_j + i)) # diagonal down left

        self.available_spots_cache[coordinate] = available_spots
        return available_spots


class Queen(AbstractPiece):
    def find_available_spots(self, board: Board, coordinate: tuple[int, int] = None):
        coordinate = coordinate if coordinate else self.coordinate

        available_spots = self.available_spots_cache.get(coordinate)
        if available_spots:
            return available_spots
        piece_i = coordinate[0]
        piece_j = coordinate[1]

        for i in range(1, board.CELL_COUNT): # DIAGONAL

            # optimize the loop
            if (piece_i - i < 0 or piece_i - i >= self.CELL_COUNT) or (
                piece_j - i < 0 or piece_j - i >= self.CELL_COUNT):
                continue

            available_spots.append((piece_i - i, piece_j - i)) # up left
            available_spots.append((piece_i + i, piece_j - i)) # up right
            available_spots.append((piece_i - i, piece_j + i)) # down left
            available_spots.append((piece_i + i, piece_j + i)) # down left
        
        # HORIZENTAL
        for i in range(piece_i): # left
            available_spots.append((i, piece_j))
        for i in range(piece_i + 1, self.CELL_COUNT): # right
            available_spots.append((i, piece_j))
        for j in range(piece_j): # up
            available_spots.append((piece_i, j))
        for j in range(piece_j + 1, self.CELL_COUNT): # down
            available_spots.append((piece_i, j))
        self.available_spots_cache[coordinate] = available_spots
        return available_spots
        


class King(AbstractPiece):
    def find_available_spots(self, board: Board, coordinate: tuple[int, int] = None):
        coordinate = coordinate if coordinate else self.coordinate

        available_spots = self.available_spots_cache.get(coordinate)
        if available_spots:
            return available_spots
        piece_i = coordinate[0]
        piece_j = coordinate[1]

        for i in [-1, 1]:
            for j in [-1, 1]:
                # prevent IndexOutOfRange
                if (piece_i + i < 0 or piece_i + i >= self.CELL_COUNT) or (
                    piece_j + j < 0 or piece_j + j >= self.CELL_COUNT):
                    continue

                available_spots.append((piece_i + i, piece_j + j))

        self.available_spots_cache[coordinate] = available_spots
        return available_spots


# testing
if __name__ == "__main__":
    import pygame
    import settings
    from texture_loader import TexturePackLoader

    texturepackloader = TexturePackLoader(settings.TEXTURE_DIR)
    pack = texturepackloader.get_pack(settings.DEFAULT_TEXTURE_PACK)

    screen = pygame.display.set_mode((settings.WIDTH, settings.HIGHT))

    image = pack.get_texture(settings.TEXTURE_NAMES["board"])
    image = pygame.transform.scale(image, (settings.HIGHT, settings.HIGHT))
    board = Board(image)
    run = True
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

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
