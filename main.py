import logging
import pygame
import abstracts
import game_elements
import settings
import player
import input_sources
from motion import Motion
from texture_loader import TexturePackLoader
from helpers import create_simple_square_sprite
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
        self.moves = []
        self.is_game_running = False

    def _handle_closing_event(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.QUIT:
                self.is_game_running = False

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

    def add_move(self, move: Move):
        self.moves.append(move)

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
        self.is_game_running = True
        available_cells_to_draw = []
        previous_move_source_cell = None  # the last cell a piece moved from.
        logging.info("entering main loop...")
        while self.is_game_running:
            self.clock.tick(settings.FPS)

            events = pygame.event.get()
            self._handle_closing_event(events)
            # handling simple clicks
            if clicked_pos := self.get_clicked_pos(events):
                if available_cells_to_draw:
                    available_cells_to_draw.clear()
                elif coordinate := self.board.get_cell_by_coordinates(clicked_pos):
                    if (
                        cell := self.board.get_cell(*coordinate)
                    ) in self.board.get_filled_cells():
                        available_spots = cell.piece.find_available_spots(
                            self.board, color=self.player1.color
                        )
                        for spot in available_spots:
                            spot_coordinate = spot.coordinate
                            cell = self.board.get_cell(*spot_coordinate)
                            sprite = create_simple_square_sprite(
                                cell.width,
                                cell.hight,
                                settings.AVAILABLE_SPOTS_COLOR,
                                cell.rect.copy(),
                            )
                            available_cells_to_draw.append(sprite)

            # handling players input
            if player_input := self.current_player.get_input(self.board, events):
                source_cell: game_elements.Cell = self.board.get_cell(
                    *player_input.source
                )
                available_spot = player_input.dest
                dest_cell: game_elements.Cell = self.board.get_cell(
                    *available_spot.coordinate
                )

                previous_move_source_cell = create_simple_square_sprite(
                    source_cell.width,
                    source_cell.hight,
                    settings.LAST_MOVE_CELL_COLOR,
                    source_cell.rect.copy(),
                )
                available_cells_to_draw.clear()

                if isinstance(
                    source_cell.piece, game_elements.Pawn
                ):  # helpful for detecting en-passant
                    source_cell.piece.moves_count += 1

                # handle en-passant
                if available_spot.is_en_passant:
                    target_cell = available_spot.en_passant_target_cell
                    self.current_player.eaten_pieces.append(target_cell.piece)
                    target_cell.rem_piece()

                if dest_cell.piece:
                    self.current_player.eaten_pieces.append(source_cell.piece)

                # moving pieces
                dest_cell.set_piece(source_cell.piece)
                source_cell.rem_piece()

                self.motion.add_operation(
                    dest_cell.piece, (dest_cell.rect.x, dest_cell.rect.y)
                )

                self.add_move(Move(source=player_input.source, dest=player_input.dest))
                self.switch_players()

            # applying animations
            self.motion.apply_motion()

            # drawing stuff
            pieces: list[abstracts.AbstractPiece] = [
                cell.piece for cell in self.board.get_filled_cells()
            ]

            items_to_draw = [self.board, *available_cells_to_draw, *pieces]
            if previous_move_source_cell is not None:
                items_to_draw.append(previous_move_source_cell)

            self.screen.fill("white")
            self.draw_items(self.screen, *items_to_draw)


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
