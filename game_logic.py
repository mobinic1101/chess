import pygame
import helpers
import settings
from game_elements import Board, Cell, SpecialPiece
from motion import Motion
from input_sources import get_clicked_pos
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import AbstractPlayer, PlayerInput


class GameLogic:
    def __init__(
        self,
        board: Board,
        player1: "AbstractPlayer",
        player2: "AbstractPlayer",
        motion: Motion,
    ):
        self.board = board
        self.player1 = player1
        self.player2 = player2
        self.motion = motion
        self.current_player = player1 if player1.color == "white" else player2
        # available cells for a single piece to draw for example for pawn its one cell in front of it
        self.available_cells_to_draw = []
        # this is used to draw the last move cell
        self.previous_move_source_cell = None

    def switch_players(self):
        """Switches the current player to the other player."""
        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1

    def add_previous_move_source_cell(self, source_cell: Cell):
        """Adds a sprite to the previous_move_source_cell attribute to draw it on the board."""
        self.previous_move_source_cell = helpers.create_simple_square_sprite(
            source_cell.width,
            source_cell.hight,
            settings.LAST_MOVE_CELL_COLOR,
            source_cell.rect.copy(),
        )

    def handle_simple_clicks(self, events: list[pygame.event.Event]):
        mouse_pos = get_clicked_pos(events)
        if mouse_pos is None:
            return
        # based on the condition above we only clear the available_cells_to_draw
        # if the user clicks somewhere. so
        if self.available_cells_to_draw:
            self.available_cells_to_draw.clear()
            return

        # validation
        cell = self.board.get_cell_by_coordinates(mouse_pos)
        if cell is None:
            return
        if cell.is_empty():
            return
        for spot in cell.piece.find_available_spots(
            self.board, color=self.player1.color
        ):
            cell = self.board.get_cell(*spot.coordinate)
            sprite = helpers.create_simple_square_sprite(
                cell.width,
                cell.hight,
                settings.AVAILABLE_SPOTS_COLOR,
                cell.rect.copy(),
            )
            self.available_cells_to_draw.append(sprite)

    def execute_move(self, source_cell: Cell, dest_cell: Cell):
        """Executes a move from source_cell to dest_cell.
        \n\+ adds the movement done to the list of operations in the self.motion object.
        """

        dest_cell.set_piece(source_cell.piece)
        source_cell.rem_piece()
        self.motion.add_operation(dest_cell.piece, (dest_cell.rect.x, dest_cell.rect.y))

    def handle_en_passant(
        self, player_input: "PlayerInput", source_cell: Cell, dest_cell: Cell
    ):
        target_cell = player_input.move.dest.target_cell
        self.current_player.eaten_pieces.append(target_cell.piece)
        target_cell.rem_piece()
        self.execute_move(source_cell, dest_cell)

    def handle_castling(
        self, player_input: "PlayerInput", rook_cell: Cell, king_cell: Cell
    ):
        rook_new_cell = self.board.get_cell(
            *player_input.move.dest.castling_details["rook_new_pos"]
        )
        king_new_cell = self.board.get_cell(
            *player_input.move.dest.castling_details["king_new_pos"]
        )

        self.execute_move(rook_cell, rook_new_cell)
        self.execute_move(king_cell, king_new_cell)

    def handle_promotion(self, player_input: "PlayerInput"): ...

    def handle_special_moves(self, player_input: "PlayerInput") -> bool:
        """Handles special moves like castling, en-passant, promotion, etc.
        if a special move detected and executed it will return True otherwise False

        Returns:
            bool (True|False): if a special move detected and executed it will return True otherwise False
        """
        source_cell, dest_cell = player_input.get_cells(self.board)

        if player_input.is_en_passant:
            self.handle_en_passant(player_input, source_cell, dest_cell)
            return True
        elif player_input.is_castling:
            self.handle_castling(
                player_input, rook_cell=source_cell, king_cell=dest_cell
            )
            return True
        elif player_input.is_promotion:
            self.handle_promotion(player_input)
            return True
        else:
            return False

    def handle_normal_moves(self, player_input: "PlayerInput"):
        source_cell, dest_cell = player_input.get_cells(self.board)
        if not dest_cell.is_empty():
            self.current_player.eaten_pieces.append(dest_cell.piece)
        self.execute_move(source_cell, dest_cell)

    def process_input(self, events: list[pygame.event.Event]) -> "PlayerInput | None":
        """Processes the input from the current player and updates the board accordingly.
        + handles special moves like castling, en-passant, promotion, etc.

        Args:
            events (list[pygame.event.Event]): List of pygame events to process.
        Returns:
            player_input ("PlayerInput"): The input from the current player.
        """
        player_input: "PlayerInput" = self.current_player.get_input(self.board, events)
        if player_input is None:
            return False
        source_cell, dest_cell = player_input.get_cells(self.board)

        self.add_previous_move_source_cell(source_cell)

        # handle special moves like castling, en-passant, promotion, etc...
        special_move_made = False
        if isinstance(source_cell.piece, SpecialPiece):
            if source_cell.piece.moves_count == 0:
                source_cell.piece.moves_count += 1
            if dest_cell.piece and isinstance(dest_cell.piece, SpecialPiece):
                dest_cell.piece.moves_count += 1
            special_move_made = self.handle_special_moves(player_input)

        if not special_move_made:
            self.handle_normal_moves(player_input)

        # add this line because if other player (possibly the bot) does a move
        # while the player have already clicked on a piece the available cells for that piece
        # should not no longer be displayed so we should clear the available_cells_to_draw
        # when bot does a move
        self.available_cells_to_draw.clear()

        # switch players after the move is done
        self.switch_players()
        return player_input
