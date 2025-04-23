import pygame
import settings
import abstracts
import texture_loader
import game_elements
import player as game_players
import datatypes
from motion import Motion


def main():
    pygame.init()
    screen = pygame.display.set_mode((settings.WIDTH, settings.HIGHT))
    pygame.display.set_caption(settings.CAPTION)
    clock = pygame.time.Clock()

    texture_pack = texture_loader.TexturePackLoader(settings.TEXTURE_DIR).get_pack()

    player = game_players.Human(name="human", color="white")
    board = game_elements.Board(
        texture_pack.get_texture(settings.TEXTURE_NAMES["board"], (settings.HIGHT, settings.HIGHT))
        )
    pawn_texture = texture_pack.get_texture(
        settings.TEXTURE_NAMES["w_pawn"],
        (board.image.get_width() // 8, board.image.get_height() // 8)
        )
    pawn = game_elements.Pawn(image=pawn_texture, player=player, coordinate=(1, 7))
    board.get_cell(*pawn.coordinate).set_piece(pawn)

    available_cells: list[game_elements.Cell] = []
    run = True
    while run:
        clock.tick(settings.FPS)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                available_cells.clear()
        
        if user_input := player.get_input(events):
            print("USERINPUT =", user_input)
            source, dest = user_input
            source_cell = board.get_cell(*user_input[0])
            dest_cell = board.get_cell(*user_input[1])
            if not source_cell.is_empty():
                piece = source_cell.piece
                available_spots = piece.find_available_spots(board=board, color=player.color)
                for spot in available_spots:
                    available_cells.append(board.get_cell(*spot))

        # drawings
        
        screen.blit(board.image, board.rect)
        if available_cells:
            for cell in available_cells:
                # rect = pygame.Rect(cell.rect.x, cell.rect.y, cell.image.get_width(), cell.image.get_height())
                square = pygame.Surface((cell.image.get_width(), cell.image.get_height()))
                screen.blit(square, cell.rect)
        for cell in board.get_filled_cells():
            screen.blit(cell.piece.image, cell.rect)
        pygame.display.update()

if __name__ == "__main__":
    main()

# class Game:
#     def __init__(
#             self,
#             player1: abstracts.AbstractPlayer,
#             player2: abstracts.AbstractPlayer,
#             time
#             ):
#         self.player1 = player1
#         self.player2 = player2
#         self.moves: list[datatypes.Move] = []

#     def add_move(self, move: datatypes.Move):
#         self.moves.append(move)
    

    