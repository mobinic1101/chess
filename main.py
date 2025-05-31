import logging
import pygame
from motion import Motion
from game_logic import GameLogic
from texture_loader import TexturePackLoader
import settings
import game_elements
import player
import input_sources
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from renderer import AbstractDrawable

pygame.init()


class Game:
    def __init__(self, game_logic: GameLogic):
        self.game_logic = game_logic
        self.motion = game_logic.motion
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HIGHT))
        from renderer import Renderer

        self.renderer = Renderer(self.screen)
        self.clock = pygame.time.Clock()
        self.moves = []
        self.is_game_running = False

    def _handle_closing_event(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.QUIT:
                self.is_game_running = False

    def add_move(self, move: "player.PlayerInput"):
        self.moves.append((move))

    def main_loop(self):
        self.is_game_running = True
        logging.info("entering main loop...")
        while self.is_game_running:
            self.clock.tick(settings.FPS)

            events = pygame.event.get()
            self._handle_closing_event(events)
            # handling simple clicks
            self.game_logic.handle_simple_clicks(events)

            # handling players input
            self.game_logic.process_input(events)

            # applying animations
            self.motion.apply_motion()

            # drawing stuff
            drawables: list["AbstractDrawable"] = [self.game_logic.board]
            if self.game_logic.previous_move_source_cell:
                drawables.append(self.game_logic.previous_move_source_cell)
            drawables.extend(self.game_logic.available_cells_to_draw)
            drawables.extend(
                [cell.piece for cell in self.game_logic.board.get_filled_cells()]
            )
            self.renderer.bulk_add_items(drawables)
            self.renderer.draw_items(self.screen, update_display=True)


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
    game_logic = GameLogic(board, player1, player2, Motion(settings.MOVEMENT_SPEED))
    game = Game(game_logic)
    game.main_loop()
