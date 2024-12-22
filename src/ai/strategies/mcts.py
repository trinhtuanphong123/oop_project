# src/ai/strategies/mcts.py

import math
import random
from typing import Optional, List, Dict
from ..chess_ai import ChessAI, AIStrategy
from ...core.move import Move
from ...core.game_state import GameState

class MCTSNode:
    """Node trong cây MCTS"""
    
    def __init__(self, game_state: GameState, parent=None, move: Optional[Move] = None):
        self.game_state = game_state
        self.parent = parent
        self.move = move  # Nước đi dẫn đến node này
        self.children: List[MCTSNode] = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = game_state.get_legal_moves()

class MCTSStrategy(ChessAI):
    """
    Monte Carlo Tree Search strategy.
    Phù hợp cho cấp độ EXPERT.
    """
    
    def __init__(self):
        super().__init__(AIStrategy.MCTS)
        self.exploration_constant = 1.414  # UCT constant
        
    def get_best_move(self, game_state: GameState) -> Optional[Move]:
        """Tìm nước đi tốt nhất sử dụng MCTS"""
        self._start_time = self.get_current_time()
        root = MCTSNode(game_state)
        
        # Chạy mô phỏng cho đến khi hết thời gian
        simulation_count = 0
        while not self.is_time_up() and simulation_count < self._max_simulations:
            node = self._select(root)
            if node.game_state.is_game_over():
                self._backpropagate(node, node.game_state.get_result())
            else:
                node = self._expand(node)
                result = self._simulate(node)
                self._backpropagate(node, result)
            simulation_count += 1
            
        # Chọn nước đi tốt nhất
        best_child = self._get_best_child(root, 0)  # exploration=0 for final choice
        
        if best_child:
            self._stats.nodes_evaluated = simulation_count
            self._stats.max_depth = self._get_max_depth(root)
            self._stats.best_moves = [best_child.move]
            return best_child.move
            
        return None
        
    def _select(self, node: MCTSNode) -> MCTSNode:
        """Chọn node để mở rộng"""
        while node.untried_moves == [] and node.children != []:
            node = self._get_best_child(node, self.exploration_constant)
        return node
        
    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Mở rộng node bằng một nước đi chưa thử"""
        if node.untried_moves:
            move = random.choice(node.untried_moves)
            node.untried_moves.remove(move)
            
            new_state = node.game_state.clone()
            new_state.make_move(move)
            
            child = MCTSNode(new_state, node, move)
            node.children.append(child)
            return child
        return node
        
    def _simulate(self, node: MCTSNode) -> float:
        """
        Chạy một mô phỏng từ node hiện tại
        Returns:
            float: 1.0 cho thắng, 0.5 cho hòa, 0.0 cho thua
        """
        state = node.game_state.clone()
        
        while not state.is_game_over():
            moves = state.get_legal_moves()
            if not moves:
                break
            move = random.choice(moves)
            state.make_move(move)
            
        return state.get_result()
        
    def _backpropagate(self, node: MCTSNode, result: float) -> None:
        """Cập nhật thống kê cho các node từ leaf đến root"""
        while node:
            node.visits += 1
            node.wins += result
            node = node.parent
            result = 1 - result  # Đảo kết quả cho đối thủ
            
    def _get_best_child(self, node: MCTSNode, exploration: float) -> Optional[MCTSNode]:
        """
        Chọn child node tốt nhất dựa trên UCT formula
        Args:
            exploration: Hệ số exploration (0 để chọn nước đi cuối cùng)
        """
        if not node.children:
            return None
            
        def uct_score(n: MCTSNode) -> float:
            if n.visits == 0:
                return float('inf')
            exploitation = n.wins / n.visits
            exploration_term = exploration * math.sqrt(math.log(node.visits) / n.visits)
            return exploitation + exploration_term
            
        return max(node.children, key=uct_score)
        
    def _get_max_depth(self, root: MCTSNode) -> int:
        """Tính độ sâu tối đa của cây MCTS"""
        if not root.children:
            return 0
        return 1 + max(self._get_max_depth(child) for child in root.children)