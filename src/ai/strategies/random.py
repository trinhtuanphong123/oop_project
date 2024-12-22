# src/ai/strategies/random.py

import random
from typing import Optional, List
from ..chess_ai import ChessAI, AIStrategy
from ...core.move import Move
from ...core.game_state import GameState

class RandomStrategy(ChessAI):
    """
    Chiến thuật chọn nước đi ngẫu nhiên.
    Đây là chiến thuật đơn giản nhất, dùng cho cấp độ EASY.
    """
    
    def __init__(self):
        super().__init__(AIStrategy.RANDOM)

    def get_best_move(self, game_state: GameState) -> Optional[Move]:
        """
        Chọn ngẫu nhiên một nước đi hợp lệ
        
        Args:
            game_state: Trạng thái game hiện tại
            
        Returns:
            Optional[Move]: Nước đi được chọn hoặc None nếu không có
        """
        self._start_time = self.get_current_time()
        legal_moves = game_state.get_legal_moves()
        
        if not legal_moves:
            return None
            
        chosen_move = random.choice(legal_moves)
        self._stats.time_spent = self.get_time_spent()
        self._stats.nodes_evaluated = 1
        self._stats.best_moves = [chosen_move]
        
        return chosen_move