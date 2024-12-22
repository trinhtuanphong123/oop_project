# src/players/ai_player.py

from enum import Enum
from typing import Optional, Dict, TYPE_CHECKING
from datetime import datetime

from .player import Player, PlayerType, GameResult
from ..pieces.piece import PieceColor
from ..core.move import Move
from ..ai.chess_ai import ChessAI

if TYPE_CHECKING:
    from ..core.game_state import GameState
    from ..ai.strategies.random import RandomStrategy
    from ..ai.strategies.negamax import NegamaxStrategy
    from ..ai.strategies.mcts import MCTSStrategy

class AILevel(Enum):
    """Cấp độ AI"""
    EASY = 1      # Random moves
    MEDIUM = 2    # Negamax depth 3
    HARD = 3      # Negamax depth 5 
    EXPERT = 4    # MCTS with 1000 simulations

class AIConfig:
    """
    Cấu hình cho AI player
    
    Attributes:
        thinking_time (int): Thời gian suy nghĩ tối đa cho mỗi nước đi (ms)
        search_depth (int): Độ sâu tìm kiếm tối đa
        max_simulations (int): Số lần mô phỏng tối đa cho MCTS
        opening_book (bool): Có sử dụng opening book không
    """
    
    def __init__(self):
        self.thinking_time: int = 1000
        self.search_depth: int = 3
        self.max_simulations: int = 1000
        self.opening_book: bool = True
        
    def set_level(self, level: AILevel) -> None:
        """Cài đặt cấu hình theo cấp độ"""
        if level == AILevel.EASY:
            self.search_depth = 1
            self.thinking_time = 500
            self.max_simulations = 100
        elif level == AILevel.MEDIUM:
            self.search_depth = 3
            self.thinking_time = 1000
            self.max_simulations = 500
        elif level == AILevel.HARD:
            self.search_depth = 5
            self.thinking_time = 2000
            self.max_simulations = 1000
        elif level == AILevel.EXPERT:
            self.search_depth = 7
            self.thinking_time = 5000
            self.max_simulations = 2000

class AIPlayer(Player):
    """
    Class đại diện cho người chơi AI.
    
    Trách nhiệm:
    - Sử dụng AI engine để chọn nước đi
    - Quản lý chiến thuật và cấp độ AI
    - Theo dõi hiệu suất và thời gian suy nghĩ
    """

    def __init__(self, name: str, color: PieceColor, ai_engine: ChessAI, level: AILevel = AILevel.MEDIUM):
        """
        Khởi tạo AI player
        
        Args:
            name (str): Tên AI
            color (PieceColor): Màu quân của AI
            ai_engine (ChessAI): Engine AI được sử dụng
            level (AILevel, optional): Cấp độ AI. Defaults to MEDIUM.
        """
        super().__init__(name, color, PlayerType.AI)
        
        self._ai_engine: ChessAI = ai_engine
        self._config: AIConfig = AIConfig()
        self._level: AILevel = level
        self._config.set_level(level)
        
        # Thống kê hiệu suất
        self._avg_thinking_time: float = 0
        self._moves_analyzed: int = 0
        self._performance_stats: Dict = {
            'total_nodes': 0,
            'avg_depth': 0,
            'max_depth': 0,
            'best_moves': []
        }

    @property
    def level(self) -> AILevel:
        """Cấp độ hiện tại của AI"""
        return self._level

    @property
    def config(self) -> AIConfig:
        """Cấu hình hiện tại của AI"""
        return self._config

    @property
    def performance_stats(self) -> Dict:
        """Thống kê hiệu suất của AI"""
        return self._performance_stats.copy()

    def set_level(self, level: AILevel) -> None:
        """
        Thay đổi cấp độ AI
        
        Args:
            level (AILevel): Cấp độ mới
        """
        self._level = level
        self._config.set_level(level)
        self._ai_engine.reset()

    def get_move(self, game_state: 'GameState') -> Optional[Move]:
        """
        Lấy nước đi từ AI
        
        Args:
            game_state (GameState): Trạng thái game hiện tại
        
        Returns:
            Optional[Move]: Nước đi được chọn hoặc None nếu không có
        """
        if not self.is_in_game or game_state.is_game_over():
            return None

        # Bắt đầu tính thời gian suy nghĩ
        start_time = datetime.now().timestamp() * 1000

        # Cấu hình cho AI engine
        self._ai_engine.configure(
            thinking_time=self._config.thinking_time,
            search_depth=self._config.search_depth,
            max_simulations=self._config.max_simulations,
            use_opening_book=self._config.opening_book
        )

        # Lấy nước đi từ AI
        chosen_move = self._ai_engine.get_best_move(game_state)
        
        # Cập nhật thống kê
        if chosen_move:
            end_time = datetime.now().timestamp() * 1000
            thinking_time = end_time - start_time
            
            self._update_performance_stats(
                thinking_time,
                self._ai_engine.get_stats()
            )
            
            # Thực hiện nước đi
            if self.make_move(chosen_move):
                return chosen_move

        return None

    def _update_performance_stats(self, thinking_time: float, engine_stats: Dict) -> None:
        """
        Cập nhật thống kê hiệu suất
        
        Args:
            thinking_time (float): Thời gian suy nghĩ (ms)
            engine_stats (Dict): Thống kê từ engine
        """
        # Cập nhật thời gian suy nghĩ trung bình
        self._moves_analyzed += 1
        self._avg_thinking_time = (
            (self._avg_thinking_time * (self._moves_analyzed - 1) + thinking_time)
            / self._moves_analyzed
        )
        
        # Cập nhật thống kê từ engine
        self._performance_stats['total_nodes'] += engine_stats.get('nodes_evaluated', 0)
        self._performance_stats['avg_depth'] = engine_stats.get('avg_depth', 0)
        self._performance_stats['max_depth'] = max(
            self._performance_stats['max_depth'],
            engine_stats.get('max_depth', 0)
        )
        
        # Lưu các nước đi tốt nhất
        best_moves = engine_stats.get('best_moves', [])
        if best_moves:
            self._performance_stats['best_moves'].extend(best_moves[:3])
            # Giữ tối đa 10 nước đi tốt nhất
            self._performance_stats['best_moves'] = \
                self._performance_stats['best_moves'][-10:]

    def get_average_thinking_time(self) -> float:
        """
        Lấy thời gian suy nghĩ trung bình
        
        Returns:
            float: Thời gian trung bình (ms)
        """
        return self._avg_thinking_time

    def reset(self) -> None:
        """Reset trạng thái AI player"""
        super().reset()
        self._ai_engine.reset()
        self._avg_thinking_time = 0
        self._moves_analyzed = 0
        self._performance_stats = {
            'total_nodes': 0,
            'avg_depth': 0,
            'max_depth': 0,
            'best_moves': []
        }

    def __str__(self) -> str:
        """Hiển thị thông tin AI player"""
        return f"AI {self.name} (Level: {self.level.name})"

    def __repr__(self) -> str:
        """Hiển thị thông tin debug"""
        return (f"AIPlayer(name='{self.name}', color={self.color.name}, "
                f"level={self.level.name}, moves={self.move_count})")