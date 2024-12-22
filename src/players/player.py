# src/players/player.py

from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum

# Import từ core package
from ..pieces.piece import PieceColor
from ..core.move import Move

# Type checking imports
if TYPE_CHECKING:
    from ..core.game_state import GameState
    from ..core.board import Board

class PlayerType(Enum):
    """Loại người chơi"""
    HUMAN = "human"
    AI = "ai"

class GameResult(Enum):
    """Kết quả trận đấu"""
    WIN = "win"
    LOSS = "loss" 
    DRAW = "draw"

class PlayerStats:
    """
    Class lưu trữ thống kê của người chơi
    
    Attributes:
        games_played (int): Số trận đã chơi
        games_won (int): Số trận thắng
        games_lost (int): Số trận thua
        games_drawn (int): Số trận hòa
        total_moves (int): Tổng số nước đã đi
        total_time (int): Tổng thời gian chơi (ms)
        best_time (float): Thời gian tốt nhất để thắng (ms)
        last_game (datetime): Thời gian trận gần nhất
    """
    
    def __init__(self):
        self.games_played: int = 0
        self.games_won: int = 0
        self.games_lost: int = 0
        self.games_drawn: int = 0
        self.total_moves: int = 0
        self.total_time: int = 0  
        self.best_time: float = float('inf')
        self.last_game: Optional[datetime] = None

    def update(self, result: GameResult, game_time: int) -> None:
        """
        Cập nhật thống kê sau một trận đấu
        
        Args:
            result (GameResult): Kết quả trận đấu
            game_time (int): Thời gian trận đấu (ms)
        """
        self.games_played += 1
        self.total_time += game_time
        self.last_game = datetime.now()

        if result == GameResult.WIN:
            self.games_won += 1
            if game_time < self.best_time:
                self.best_time = game_time
        elif result == GameResult.LOSS:
            self.games_lost += 1
        else:
            self.games_drawn += 1

class Player:
    """
    Class cơ sở cho người chơi cờ.
    
    Trách nhiệm:
    - Quản lý thông tin người chơi (tên, màu quân, loại)
    - Theo dõi trạng thái (thời gian, số nước đi)
    - Lưu trữ thống kê (số trận, tỉ lệ thắng)
    - Xử lý nước đi của người chơi
    """

    def __init__(self, name: str, color: PieceColor, player_type: PlayerType = PlayerType.HUMAN):
        """
        Khởi tạo người chơi
        
        Args:
            name (str): Tên người chơi
            color (PieceColor): Màu quân của người chơi
            player_type (PlayerType, optional): Loại người chơi. Defaults to HUMAN.
        """
        # Thông tin cơ bản
        self._name: str = name
        self._color: PieceColor = color
        self._type: PlayerType = player_type
        
        # Trạng thái hiện tại
        self._time_left: int = 0  # ms
        self._move_count: int = 0
        self._last_move_time: int = 0  # ms
        self._is_in_game: bool = False
        
        # Thống kê và lịch sử
        self._stats: PlayerStats = PlayerStats()
        self._move_history: List[Move] = []

    @property
    def name(self) -> str:
        """Tên người chơi"""
        return self._name

    @property
    def color(self) -> PieceColor:
        """Màu quân của người chơi"""
        return self._color

    @property
    def type(self) -> PlayerType:
        """Loại người chơi"""
        return self._type

    @property
    def time_left(self) -> int:
        """Thời gian còn lại (ms)"""
        return self._time_left

    @property
    def move_count(self) -> int:
        """Số nước đã đi"""
        return self._move_count

    @property
    def is_in_game(self) -> bool:
        """Đang trong game?"""
        return self._is_in_game

    @property
    def stats(self) -> PlayerStats:
        """Thống kê người chơi"""
        return self._stats

    @property
    def move_history(self) -> List[Move]:
        """Lịch sử nước đi"""
        return self._move_history.copy()

    def start_game(self, initial_time: int = 0) -> None:
        """
        Bắt đầu game mới
        
        Args:
            initial_time (int, optional): Thời gian ban đầu (ms). Defaults to 0.
        """
        self._is_in_game = True
        self._time_left = initial_time
        self._move_count = 0
        self._move_history.clear()
        self._last_move_time = datetime.now().timestamp() * 1000

    def end_game(self, result: GameResult) -> None:
        """
        Kết thúc game
        
        Args:
            result (GameResult): Kết quả trận đấu
        """
        if not self._is_in_game:
            return

        self._is_in_game = False
        game_time = self._stats.total_time - self._time_left
        self._stats.update(result, game_time)

    def get_move(self, game_state: 'GameState') -> Optional[Move]:
        """
        Lấy nước đi từ người chơi
        
        Args:
            game_state (GameState): Trạng thái game hiện tại
        
        Returns:
            Optional[Move]: Nước đi được chọn hoặc None nếu không có
            
        Raises:
            NotImplementedError: Class con phải implement phương thức này
        """
        raise NotImplementedError("Subclass must implement get_move()")

    def make_move(self, move: Move) -> bool:
        """
        Thực hiện một nước đi
        
        Args:
            move (Move): Nước đi cần thực hiện
            
        Returns:
            bool: True nếu thực hiện thành công
        """
        if not self._is_in_game:
            return False

        # Cập nhật thời gian
        current_time = datetime.now().timestamp() * 1000
        move_time = current_time - self._last_move_time
        self._time_left -= move_time
        
        # Kiểm tra hết giờ
        if self._time_left < 0:
            return False

        # Cập nhật thông tin
        self._move_count += 1
        self._move_history.append(move)
        self._last_move_time = current_time
        self._stats.total_moves += 1
        
        return True

    def undo_last_move(self) -> Optional[Move]:
        """
        Hoàn tác nước đi cuối cùng
        
        Returns:
            Optional[Move]: Nước đi đã hoàn tác hoặc None nếu không có
        """
        if not self._move_history:
            return None
            
        self._move_count -= 1
        return self._move_history.pop()

    def update_time(self, delta_ms: int) -> None:
        """
        Cập nhật thời gian còn lại
        
        Args:
            delta_ms (int): Thời gian cần thêm/bớt (ms)
        """
        self._time_left = max(0, self._time_left + delta_ms)
        if delta_ms > 0:
            self._stats.total_time += delta_ms

    def has_time_left(self) -> bool:
        """
        Kiểm tra còn thời gian không
        
        Returns:
            bool: True nếu còn thời gian
        """
        return self._time_left > 0

    def get_move_time(self) -> int:
        """
        Lấy thời gian đã dùng cho nước đi hiện tại
        
        Returns:
            int: Thời gian đã dùng (ms)
        """
        if not self._last_move_time:
            return 0
        current_time = datetime.now().timestamp() * 1000
        return int(current_time - self._last_move_time)

    def reset(self) -> None:
        """Reset trạng thái người chơi"""
        self._time_left = 0
        self._move_count = 0
        self._move_history.clear()
        self._is_in_game = False
        self._last_move_time = 0

    def get_win_rate(self) -> float:
        """
        Tính tỉ lệ thắng
        
        Returns:
            float: Tỉ lệ thắng (0.0 - 1.0)
        """
        if self._stats.games_played == 0:
            return 0.0
        return self._stats.games_won / self._stats.games_played

    def __str__(self) -> str:
        """Hiển thị thông tin người chơi"""
        return f"{self.name} ({self.color.name})"

    def __repr__(self) -> str:
        """Hiển thị thông tin debug"""
        return (f"Player(name='{self.name}', color={self.color.name}, "
                f"type={self.type.name}, moves={self.move_count})")