# src/ai/strategies/negamax.py

from typing import Optional, Tuple, Dict, List
from ..chess_ai import ChessAI, AIStrategy, AIStats
from ...core.move import Move
from ...core.game_state import GameState
from ...pieces.piece import PieceColor

class NegamaxStrategy(ChessAI):
    """
    Chiến thuật sử dụng thuật toán Negamax với Alpha-Beta pruning.
    Phù hợp cho cấp độ MEDIUM và HARD.
    """
    
    def __init__(self):
        super().__init__(AIStrategy.NEGAMAX)
        self._piece_values = {
            'PAWN': 100,
            'KNIGHT': 320,
            'BISHOP': 330,
            'ROOK': 500,
            'QUEEN': 900,
            'KING': 20000
        }
        
    def _negamax(self, game_state: GameState, depth: int, alpha: float, 
                 beta: float, color: int) -> float:
        """
        Thuật toán Negamax với Alpha-Beta pruning
        
        Args:
            game_state: Trạng thái game
            depth: Độ sâu còn lại
            alpha: Alpha value cho pruning
            beta: Beta value cho pruning 
            color: 1 cho white, -1 cho black
            
        Returns:
            float: Điểm số tốt nhất cho vị trí hiện tại
        """
        self._stats.nodes_evaluated += 1
        
        if depth == 0 or game_state.is_game_over():
            return color * self._evaluate_position(game_state)
            
        if self.is_time_up():
            return color * self._evaluate_position(game_state)
            
        max_score = float('-inf')
        legal_moves = game_state.get_legal_moves()
        ordered_moves = self._order_moves(game_state, legal_moves)
        
        for move in ordered_moves:
            game_state.make_move(move)
            score = -self._negamax(game_state, depth - 1, -beta, -alpha, -color)
            game_state.undo_move()
            
            max_score = max(max_score, score)
            alpha = max(alpha, score)
            
            if alpha >= beta:
                self._stats.branches_pruned += 1
                break
                
        return max_score

    def _order_moves(self, game_state: GameState, moves: List[Move]) -> List[Move]:
        """
        Sắp xếp các nước đi để tối ưu alpha-beta pruning
        """
        move_scores = []
        for move in moves:
            score = self._rate_move(game_state, move)
            move_scores.append((move, score))
            
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in move_scores]

    def _rate_move(self, game_state: GameState, move: Move) -> int:
        """Đánh giá sơ bộ một nước đi"""
        score = 0
        
        # Capture moves
        if move.is_capture():
            captured_piece = game_state.board.get_piece(move.to_square)
            if captured_piece:
                score += 10 * self._piece_values.get(captured_piece.type_name, 0)
                
        # Center control
        if move.to_square.is_center():
            score += 30
            
        # Promotion moves
        if move.is_promotion():
            score += 900
            
        return score

    def _evaluate_position(self, game_state: GameState) -> float:
        """
        Đánh giá vị trí hiện tại
        Returns:
            float: Điểm số cho vị trí (dương lợi thế trắng, âm lợi thế đen)
        """
        score = 0
        
        # Material score
        score += self._evaluate_material(game_state)
        
        # Position score  
        score += self._evaluate_piece_positions(game_state)
        
        # King safety
        score += self._evaluate_king_safety(game_state)
        
        return score if game_state.current_player == PieceColor.WHITE else -score