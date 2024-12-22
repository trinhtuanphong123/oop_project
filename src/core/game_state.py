# src/core/game_state.py

from enum import Enum
from typing import List, Optional, Dict, Set
from .board import Board 
from .game_rule import GameRules
from ..pieces.piece import Piece, PieceColor
from .move import Move
from .square import Square

class GamePhase(Enum):
    """Giai đoạn của ván cờ"""
    OPENING = "opening"       # Khai cuộc
    MIDDLEGAME = "middlegame" # Trung cuộc
    ENDGAME = "endgame"      # Tàn cuộc

class GameStatus(Enum):
    """Trạng thái của ván cờ"""
    ACTIVE = "active"        # Đang chơi
    CHECK = "check"          # Chiếu
    CHECKMATE = "checkmate"  # Chiếu hết  
    STALEMATE = "stalemate"  # Hết nước đi
    DRAW = "draw"            # Hòa

class GameState:
    """
    Class GameState - Quản lý trạng thái của ván cờ.
    
    Trách nhiệm:
    1. Quản lý trạng thái game:
       - Lượt chơi hiện tại
       - Giai đoạn ván đấu
       - Tình trạng chiếu/chiếu hết/hòa
    
    2. Theo dõi lịch sử:
       - Các nước đi đã thực hiện
       - Vị trí các quân đã bị bắt
       - Số nước đi không bắt quân/không di chuyển tốt
       
    3. Xử lý điều kiện hòa:
       - Luật 50 nước
       - Lặp lại vị trí 3 lần
       - Không đủ quân để chiếu hết
    """

    def __init__(self, board: Board, rules: GameRules):
        """
        Khởi tạo trạng thái game mới
        Args:
            board: Bàn cờ
            rules: Luật chơi
        """
        self._board = board
        self._rules = rules
        
        # Trạng thái cơ bản
        self._current_player = PieceColor.WHITE
        self._status = GameStatus.ACTIVE
        self._phase = GamePhase.OPENING
        
        # Lịch sử và theo dõi
        self._move_history: List[Move] = []
        self._captured_pieces: List[Piece] = []
        self._position_history: List[str] = []
        self._fifty_move_counter = 0
        self._moves_played = 0
        
        # Lưu nước đi cuối cùng (cho en passant)
        self._last_move: Optional[Move] = None

    @property
    def current_player(self) -> PieceColor:
        """Người chơi hiện tại"""
        return self._current_player

    @property
    def status(self) -> GameStatus:
        """Trạng thái hiện tại của game"""
        return self._status

    @property
    def phase(self) -> GamePhase:
        """Giai đoạn hiện tại của game"""
        return self._phase

    @property
    def is_game_over(self) -> bool:
        """Kiểm tra game đã kết thúc chưa"""
        return self._status in {
            GameStatus.CHECKMATE,
            GameStatus.STALEMATE,
            GameStatus.DRAW
        }

    def make_move(self, move: Move) -> bool:
        """
        Thực hiện một nước đi và cập nhật trạng thái
        Args:
            move: Nước đi cần thực hiện
        Returns:
            True nếu nước đi thành công
        """
        if self.is_game_over:
            return False

        if not self._rules.is_valid_move(move):
            return False

        # Lưu trạng thái hiện tại
        self._position_history.append(str(self._board))
        
        # Thực hiện nước đi
        captured_piece = self._board.make_move(move)
        if captured_piece:
            self._captured_pieces.append(captured_piece)
            self._fifty_move_counter = 0
        elif move.moving_piece.piece_type == "PAWN":
            self._fifty_move_counter = 0
        else:
            self._fifty_move_counter += 1

        # Cập nhật lịch sử
        self._moves_played += 1
        self._move_history.append(move)
        self._last_move = move
        
        # Cập nhật trạng thái
        self._update_game_status()
        self._update_game_phase()
        
        # Chuyển lượt
        self._current_player = self._current_player.opposite
        return True

    def undo_last_move(self) -> Optional[Move]:
        """
        Hoàn tác nước đi cuối cùng
        Returns:
            Nước đi đã hoàn tác hoặc None
        """
        if not self._move_history:
            return None

        last_move = self._move_history.pop()
        self._position_history.pop()
        
        # Hoàn tác trên bàn cờ
        self._board.undo_move(last_move)
        
        # Khôi phục quân bị bắt
        if last_move.captured_piece:
            self._captured_pieces.pop()
            
        # Cập nhật bộ đếm
        self._moves_played -= 1
        if last_move.captured_piece or last_move.moving_piece.piece_type == "PAWN":
            self._fifty_move_counter = 0
        else:
            self._fifty_move_counter -= 1
            
        # Cập nhật trạng thái
        self._last_move = self._move_history[-1] if self._move_history else None
        self._current_player = self._current_player.opposite
        self._update_game_status()
        self._update_game_phase()
        
        return last_move

    def _update_game_status(self) -> None:
        """Cập nhật trạng thái game"""
        if self._is_checkmate():
            self._status = GameStatus.CHECKMATE
        elif self._is_stalemate():
            self._status = GameStatus.STALEMATE
        elif self._is_draw():
            self._status = GameStatus.DRAW
        elif self._is_check():
            self._status = GameStatus.CHECK
        else:
            self._status = GameStatus.ACTIVE

    def _update_game_phase(self) -> None:
        """Cập nhật giai đoạn game"""
        if self._moves_played < 20:
            self._phase = GamePhase.OPENING
        elif len(self._captured_pieces) < 10:
            self._phase = GamePhase.MIDDLEGAME
        else:
            self._phase = GamePhase.ENDGAME

    def _is_checkmate(self) -> bool:
        """
        Kiểm tra chiếu hết
        Returns:
            True nếu bị chiếu hết
        """
        return (self._is_check() and 
                not self._has_legal_moves())

    def _is_stalemate(self) -> bool:
        """
        Kiểm tra hết nước đi
        Returns:
            True nếu hết nước đi
        """
        return (not self._is_check() and 
                not self._has_legal_moves())

    def _is_check(self) -> bool:
        """
        Kiểm tra chiếu
        Returns:
            True nếu đang bị chiếu
        """
        king = self._board.get_king(self._current_player)
        return king and self._rules.is_square_attacked(
            king.square,
            self._current_player.opposite
        )

    def _is_draw(self) -> bool:
        """
        Kiểm tra các điều kiện hòa
        Returns:
            True nếu ván cờ hòa
        """
        return (self._is_fifty_move_draw() or
                self._is_threefold_repetition() or
                self._is_insufficient_material())

    def _has_legal_moves(self) -> bool:
        """
        Kiểm tra còn nước đi hợp lệ không
        Returns:
            True nếu còn nước đi hợp lệ
        """
        pieces = self._board.get_pieces(self._current_player)
        return any(self._rules.get_legal_moves(piece) for piece in pieces)

    def _is_fifty_move_draw(self) -> bool:
        """
        Kiểm tra hòa do luật 50 nước
        Returns:
            True nếu đạt điều kiện hòa
        """
        return self._fifty_move_counter >= 50

    def _is_threefold_repetition(self) -> bool:
        """
        Kiểm tra hòa do lặp vị trí 3 lần
        Returns:
            True nếu có vị trí lặp 3 lần
        """
        current_position = str(self._board)
        return self._position_history.count(current_position) >= 3

    def _is_insufficient_material(self) -> bool:
        """
        Kiểm tra hòa do không đủ quân chiếu hết
        Returns:
            True nếu không đủ quân để chiếu hết
        """
        white_pieces = self._board.get_pieces(PieceColor.WHITE)
        black_pieces = self._board.get_pieces(PieceColor.BLACK)
        
        # Chỉ còn 2 vua
        if len(white_pieces) == 1 and len(black_pieces) == 1:
            return True
            
        # Vua + tượng/mã vs vua
        if (len(white_pieces) == 2 and len(black_pieces) == 1) or \
           (len(white_pieces) == 1 and len(black_pieces) == 2):
            for piece in white_pieces | black_pieces:
                if piece.piece_type in {"BISHOP", "KNIGHT"}:
                    return True
                    
        return False