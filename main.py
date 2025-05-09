import logging
import pygame
import abstracts
import game_elements
import settings
import player
import input_sources
from motion import Motion
from texture_loader import TexturePackLoader
from helpers import SimpleSprite
from datatypes import Move

pygame.init()


class Game:
    def __init__(
        self,
        board: game_elements.Board,
        player1: abstracts.AbstractPlayer,
        player2: abstracts.AbstractPlayer,
    ):
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1 if player1.color == "white" else player2
        self.board = board
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HIGHT))
        self.clock = pygame.time.Clock()
        self.motion = Motion(settings.MOVEMENT_SPEED)
        self.is_running = False

    def _handle_closing_event(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.QUIT:
                self.is_running = False

    def switch_players(self):
        if self.current_player.color == self.player1.color:
            self.current_player = self.player2
        else:
            self.current_player = self.player1

    def get_other_player(self) -> abstracts.AbstractPlayer:
        if self.current_player.color == self.player1.color:
            return self.player2
        else:
            return self.player1

    def get_clicked_pos(self, events: list[pygame.event.Event]):
        """
        Returns the position of the mouse when the user clicks,
        or None if no click event is found in the given events.

        Args:
            events (list[pygame.event.Event]): list of events to check

        Returns:
            tuple[int, int] | None: the position of the mouse click, or None if no click event is found
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                return mouse_pos
        return None

    def draw_items(self, surface: pygame.Surface, *items: abstracts.AbstractDrawable):
        """iterates through items and draw the on passed surface,
        order of passing items effects layering of drawing.
        """
        if not items:
            return

        for item in items:
            surface.blit(item.image, item.rect)

        pygame.display.update()

    def main_loop(self):
        self.is_running = True
        available_cells = []
        logging.info("entering main loop...")
        while self.is_running:
            self.clock.tick(settings.FPS)
            # handling events
            events = pygame.event.get()
            self._handle_closing_event(events)
            # handling simple clicks
            if clicked_pos := self.get_clicked_pos(events):
                if available_cells:
                    available_cells.clear()
                elif coordinate := self.board.get_cell_by_coordinates(clicked_pos):
                    if (
                        cell := self.board.get_cell(*coordinate)
                    ) in self.board.get_filled_cells():
                        available_spots = cell.piece.find_available_spots(
                            self.board, color=self.player1.color
                        )
                        for spot in available_spots:
                            cell = self.board.get_cell(*spot)
                            surface = pygame.surface.Surface((cell.width, cell.hight))
                            surface.fill(settings.AVAILABLE_SPOTS_COLOR)
                            sprite = SimpleSprite(surface)
                            sprite.rect = cell.rect.copy()
                            available_cells.append(sprite)

            # handling players input
            if player_input := self.current_player.get_input(
                self.board, events
            ):
                source_cell: game_elements.Cell = self.board.get_cell(
                    *player_input.source
                )
                dest_cell: game_elements.Cell = self.board.get_cell(
                    *player_input.dest
                )

                # handle eating pieces
                if dest_cell.piece:
                    self.current_player.eated_pieces.append(dest_cell.piece)

                # moving pieces
                dest_cell.set_piece(source_cell.piece)
                source_cell.rem_piece()

                self.motion.add_operation(dest_cell.piece, (dest_cell.rect.x, dest_cell.rect.y))

                # adding to player's move
                self.current_player.add_move(
                    Move(source=player_input.source, dest=player_input.dest)
                )

                # switching player
                self.switch_players()

            # applying animations
            self.motion.apply_motion()

            # drawing stuff
            pieces: list[abstracts.AbstractPiece] = [
                cell.piece for cell in self.board.get_filled_cells()
            ]
            self.screen.fill("white")
            self.draw_items(self.screen, self.board, *available_cells, *pieces)
                


if __name__ == "__main__":
    texture_pack = TexturePackLoader(settings.TEXTURE_DIR).get_pack(
        settings.DEFAULT_TEXTURE_PACK
    )

    human = input_sources.Human()
    bot = input_sources.Bot()
    player1 = player.Player(
        name="Player 1",
        color="white",
        input_source=human,
    )
    player2 = player.Player(
        name="Player 2",
        color="black",
        input_source=bot,
    )

    board = game_elements.get_board(texture_pack, player1, player2)
    game = Game(board, player1, player2)
    game.main_loop()
