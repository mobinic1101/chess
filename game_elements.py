import pygame
from typing import SupportsIndex
import logging
from abstracts import AbstractDrawable, AbstractPiece


class Cell(AbstractDrawable):
    def __init__(self, _id, image: pygame.Surface, piece: AbstractPiece | None = None):
        super().__init__(image)
        self.piece = piece
        self.id = _id

    def is_empty(self):
        return self.piece is None

    def set_piece(self, piece: AbstractPiece):
        self.piece = piece
    
    def rem_piece(self):
        self.piece = None


class Board(AbstractDrawable):
    CELL_COUNT = 8 # each chess board has 8 cells vertically and horizantally
    
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
                cell = Cell(cell_id, pygame.Surface(size=(cell_width, cell_hight)))
                cell.rect.x = i * cell_width
                cell.rect.y = j * cell_width

                # aligning cells with board texture
                cell.rect.x += self.rect.x
                cell.rect.y += self.rect.y

                cell_id += 1
                row.append(cell)
            board.append(row)
        return board
        

    def get_cell_by_coordinates(self, coordinates: tuple) -> Cell | None:
        pass

    def __getitem__(self, i: SupportsIndex):
        return self.board[i]
    
    def __iter__(self):
        return iter(self.board)
    

class Pawn(AbstractPiece):
    def find_available_spots(self, board: Board):
        pass


class Rook(AbstractPiece):
    def find_available_spots(self, board: Board):
        pass


class Knight(AbstractPiece):
    def find_available_spots(self, board: Board):
        pass


class Bishop(AbstractPiece):
    def find_available_spots(self, board: Board):
        pass


class Queen(AbstractPiece):
    def find_available_spots(self, board: Board):
        pass


class King(AbstractPiece):
    def find_available_spots(self, board: Board):
        pass


# testing
if __name__ == "__main__":
    import pygame
    import settings
    from texture_loader import TexturePackLoader

    texture_loader = TexturePackLoader(settings.TEXTURE_DIR)
    pack = texture_loader.get_pack()
    image = pack.get_texture(settings.TEXTURE_NAMES["board"])
    piece = pack.get_texture(settings.TEXTURE_NAMES["b_pawn"])
    image = pygame.transform.scale(image, (settings.HIGHT, settings.HIGHT))
    board = Board(image)
    board.rect.x = (settings.WIDTH // 2) - (board.image.get_width() // 2)
    board.rect.y = (settings.HIGHT // 2) - (board.image.get_height() // 2)
    screen = pygame.display.set_mode((settings.WIDTH, settings.HIGHT))

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for row in board.board:
            for cell in row:
                cell.image.fill('red')
                # board.image.blit(cell.image, cell.rect)
        board.image.blit(piece, piece.get_rect())
        screen.blit(board.image, board.rect)
        pygame.display.update()
