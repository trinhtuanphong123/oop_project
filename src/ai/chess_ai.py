# src/ai/chess_ai.py

from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Tuple, TYPE_CHECKING
from datetime import datetime
from enum import Enum

# Import từ core package
from ..pieces.piece import PieceColor
from ..core.move import Move
from ..pieces.king import King

if TYPE_CHECKING:
    from ..core.game_state import GameState
    from ..core.board import Board
    from ..core.game_rule import GameRules

class AIStrategy(Enum):
    """Các loại chiến thuật AI"""
    RANDOM = "random"
    NEGAMAX = "negamax"
    MCTS = "mcts"

class AIStats:
    """
    Lưu trữ thống kê của quá trình tìm kiếm
    """
    def __init__(self):
        self.nodes_evaluated: int = 0      # Số nodes đã đánh giá
        self.max_depth: int = 0            # Độ sâu tối đa đạt được
        self.avg_depth: float = 0          # Độ sâu trung bình
        self.time_spent: int = 0           # Thời gian đã dùng (ms)
        self.best_moves: List[Move] = []   # Các nước đi tốt nhất tìm được
        self.best_score: float = 0.0       # Điểm số tốt nhất
        self.branches_pruned: int = 0      # Số nhánh đã cắt tỉa

class ChessAI(ABC):
    """
    Lớp cơ sở cho các chiến thuật AI.
    
    Trách nhiệm:
    - Định nghĩa interface chung cho các chiến thuật AI
    - Cung cấp các công cụ đánh giá bàn cờ
    - Theo dõi và ghi nhận thống kê
    """

    def __init__(self, strategy: AIStrategy):
        """
        Khởi tạo AI engine
        
        Args:
            strategy: Loại chiến thuật sử dụng
        """
        self._strategy = strategy
        self._color: Optional[PieceColor] = None
        
        # Cấu hình
        self._thinking_time: int = 1000    # Thời gian suy nghĩ tối đa (ms)
        self._search_depth: int = 3        # Độ sâu tìm kiếm tối đa
        self._max_simulations: int = 1000  # Số lần mô phỏng tối đa (cho MCTS)
        self._use_opening_book: bool = True
        
        # Thống kê
        self._stats = AIStats()
        self._start_time: float = 0
        
        # Cache để tối ưu
        self._transposition_table: Dict = {}
        self._move_ordering_scores: Dict = {}

    @property
    def strategy(self) -> AIStrategy:
        """Chiến thuật đang sử dụng"""
        return self._strategy

    @property
    def stats(self) -> AIStats:
        """Thống kê hiện tại"""
        return self._stats

    def configure(self, **kwargs) -> None:
        """
        Cấu hình các tham số cho AI
        
        Args:
            **kwargs: Các tham số cấu hình
                - thinking_time: Thời gian suy nghĩ (ms)
                - search_depth: Độ sâu tìm kiếm
                - max_simulations: Số lần mô phỏng tối đa
                - use_opening_book: Có sử dụng opening book
                - player_color: Màu quân của AI
        """
        self._thinking_time = kwargs.get('thinking_time', self._thinking_time)
        self._search_depth = kwargs.get('search_depth', self._search_depth)
        self._max_simulations = kwargs.get('max_simulations', self._max_simulations)
        self._use_opening_book = kwargs.get('use_opening_book', self._use_opening_book)
        self._color = kwargs.get('player_color', self._color)

    @abstractmethod
    def get_best_move(self, game_state: 'GameState') -> Optional[Move]:
        """
        Tìm nước đi tốt nhất từ trạng thái hiện tại
        
        Args:
            game_state: Trạng thái game hiện tại
            
        Returns:
            Nước đi tốt nhất hoặc None nếu không tìm thấy
        """
        pass

    def evaluate_position(self, game_state: 'GameState') -> float:
        """
        Đánh giá vị trí hiện tại
        
        Args:
            game_state: Trạng thái game cần đánh giá
            
        Returns:
            Điểm số đánh giá (dương là có lợi cho AI)
        """
        if not self._color:
            raise ValueError("Player color not set")

        score = 0.0
        board = game_state.board

        # Material score (điểm vật chất)
        material_score = self._calculate_material_score(board)
        
        # Position score (điểm vị trí)
        position_score = self._calculate_position_score(board)
        
        # Mobility score (điểm khả năng di chuyển)
        mobility_score = self._calculate_mobility_score(game_state)
        
        # King safety (độ an toàn của vua)
        king_safety_score = self._calculate_king_safety(game_state)

        # Tổng hợp điểm
        score = (
            material_score * 1.0 +    # Trọng số vật chất
            position_score * 0.1 +    # Trọng số vị trí
            mobility_score * 0.1 +    # Trọng số khả năng di chuyển
            king_safety_score * 0.2   # Trọng số an toàn của vua
        )

        # Đảo dấu nếu là quân đen
        return score if self._color == PieceColor.WHITE else -score

    def _calculate_material_score(self, board: 'Board') -> float:
        """Tính điểm dựa trên giá trị quân cờ"""
        piece_values = {
            'PAWN': 1.0,
            'KNIGHT': 3.0,
            'BISHOP': 3.0,
            'ROOK': 5.0,
            'QUEEN': 9.0,
            'KING': 0.0  # Không tính điểm cho vua
        }
        
        score = 0.0
        for piece in board.get_pieces(self._color):
            score += piece_values.get(piece.piece_type.name, 0.0)
        for piece in board.get_pieces(self._color.opposite):
            score -= piece_values.get(piece.piece_type.name, 0.0)
            
        return score

    def _calculate_position_score(self, board: 'Board') -> float:
        """Tính điểm dựa trên vị trí quân cờ"""
        score = 0.0
        
        # Piece-square tables cho từng loại quân
        piece_square_tables = self._get_piece_square_tables()
        
        for piece in board.get_pieces(self._color):
            table = piece_square_tables.get(piece.piece_type.name, {})
            score += table.get((piece.square.row, piece.square.col), 0.0)
            
        for piece in board.get_pieces(self._color.opposite):
            table = piece_square_tables.get(piece.piece_type.name, {})
            score -= table.get((7 - piece.square.row, piece.square.col), 0.0)
            
        return score

    def _calculate_mobility_score(self, game_state: 'GameState') -> float:
        """Tính điểm dựa trên số nước đi có thể"""
        legal_moves = game_state.get_legal_moves()
        opponent_moves = game_state.get_legal_moves(self._color.opposite)
        
        return len(legal_moves) - len(opponent_moves)

    def _calculate_king_safety(self, game_state: 'GameState') -> float:
        """Tính điểm an toàn của vua"""
        score = 0.0
        board = game_state.board
        
        # Kiểm tra vị trí vua
        king = board.get_king(self._color)
        opponent_king = board.get_king(self._color.opposite)
        
        if not king or not opponent_king:
            return 0.0
            
        # Kiểm tra nhập thành
        if king.has_castled:
            score += 2.0
        if opponent_king.has_castled:
            score -= 2.0
            
        # Kiểm tra quân bảo vệ xung quanh
        king_protectors = self._count_king_protectors(game_state, king)
        opponent_protectors = self._count_king_protectors(game_state, opponent_king)
        
        score += (king_protectors - opponent_protectors) * 0.2
        
        return score

    def _count_king_protectors(self, game_state: 'GameState', king: 'King') -> int:
        """Đếm số quân bảo vệ vua"""
        count = 0
        adjacent_squares = king.get_adjacent_squares()
        
        for square in adjacent_squares:
            piece = game_state.board.get_piece_at(square)
            if piece and piece.color == king.color:
                count += 1
                
        return count

    def _get_piece_square_tables(self) -> Dict:
        """
        Lấy bảng giá trị vị trí cho từng loại quân
        Returns:
            Dict chứa giá trị cho từng vị trí của mỗi loại quân
        """
        return {
            'PAWN': {
                # Ưu tiên tốt ở giữa và phía trước
                (1, 3): 0.1, (1, 4): 0.1,
                (2, 3): 0.2, (2, 4): 0.2,
                (3, 3): 0.3, (3, 4): 0.3,
            },
            'KNIGHT': {
                # Ưu tiên mã ở trung tâm
                (2, 2): 0.2, (2, 5): 0.2,
                (5, 2): 0.2, (5, 5): 0.2,
            },
            'BISHOP': {
                # Ưu tiên tượng kiểm soát đường chéo dài
                (2, 2): 0.2, (2, 5): 0.2,
                (5, 2): 0.2, (5, 5): 0.2,
            },
            'ROOK': {
                # Ưu tiên xe ở cột mở
                (0, 3): 0.1, (0, 4): 0.1,
                (7, 3): 0.1, (7, 4): 0.1,
            },
            'QUEEN': {
                # Ưu tiên hậu ở vị trí an toàn và linh hoạt
                (1, 3): 0.1, (1, 4): 0.1,
                (2, 3): 0.2, (2, 4): 0.2,
            }
        }

    def _is_out_of_time(self) -> bool:
        """Kiểm tra đã hết thời gian suy nghĩ chưa"""
        current_time = datetime.now().timestamp() * 1000
        return (current_time - self._start_time) >= self._thinking_time

    def _update_stats(self, depth: int, score: float, move: Move) -> None:
        """
        Cập nhật thống kê
        
        Args:
            depth: Độ sâu của nước đi
            score: Điểm số đánh giá
            move: Nước đi được đánh giá
        """
        self._stats.nodes_evaluated += 1
        self._stats.max_depth = max(self._stats.max_depth, depth)
        
        # Cập nhật độ sâu trung bình
        self._stats.avg_depth = (
            (self._stats.avg_depth * (self._stats.nodes_evaluated - 1) + depth)
            / self._stats.nodes_evaluated
        )
        
        # Cập nhật nước đi tốt nhất
        if score > self._stats.best_score:
            self._stats.best_score = score
            self._stats.best_moves = [move]
        elif score == self._stats.best_score:
            self._stats.best_moves.append(move)

    def reset(self) -> None:
        """Reset trạng thái của AI"""
        self._stats = AIStats()
        self._transposition_table.clear()
        self._move_ordering_scores.clear()
        self._start_time = 0

    def __str__(self) -> str:
        return f"ChessAI(strategy={self._strategy.name})"

    def __repr__(self) -> str:
        return (f"ChessAI(strategy={self._strategy.name}, "
                f"depth={self._search_depth}, time={self._thinking_time}ms)")