import logging
import pygame
from pygame.sprite import Sprite
import abstracts
import game_elements
import settings
import player
from motion import Motion
from texture_loader import TexturePackLoader
from datatypes import Move, Operation
from helpers import SimpleSprite

pygame.init()


class Game:
    def __init__(
            self,
            board: game_elements.Board,
            player1: abstracts.AbstractPlayer,
            player2: abstracts.AbstractPlayer,
            ):
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HIGHT))
        self.board = board
        self.player1 = player1
        self.player2 = player2
        self.motion = Motion(settings.MOVEMENT_SPEED)
        self.run = False

    def _handle_closing_event(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.QUIT:
                self.run = False

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
        self.run = True
        available_cells = []
        logging.info("entering main loop...")
        while self.run:
            events = pygame.event.get()
            self._handle_closing_event(events)
            # handling simple clicks
            if clicked_pos := self.get_clicked_pos(events):
                if available_cells:
                    available_cells.clear()
                elif coordinate := self.board.get_cell_by_coordinates(clicked_pos):
                    if (cell := self.board.get_cell(*coordinate)) in self.board.get_filled_cells():
                        available_spots = cell.piece.find_available_spots(
                            self.board, color=self.player1.color)
                        for spot in available_spots:
                            cell = self.board.get_cell(*spot)
                            surface = pygame.surface.Surface((cell.width, cell.hight))
                            surface.fill(settings.AVAILABLE_SPOTS_COLOR)
                            sprite = SimpleSprite(surface)
                            sprite.rect = cell.rect.copy()
                            available_cells.append(sprite)
                            
            # drawing stuff
            pieces: list[abstracts.AbstractPiece] = [cell.piece for cell in self.board.get_filled_cells()]
            self.screen.fill("white")
            self.draw_items(
                self.screen,
                self.board,
                *available_cells,
                *pieces
                )

if __name__ == '__main__':
    texture_pack = TexturePackLoader(settings.TEXTURE_DIR).get_pack(settings.DEFAULT_TEXTURE_PACK)

    player1 = player.Human("MObin", "black")
    player2 = player.Human("Haammma", "white")
    board = game_elements.get_board(texture_pack, player1, player2)

    game = Game(board, player1, player2)
    game.main_loop()