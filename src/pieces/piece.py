# src/pieces/piece.py

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, TYPE_CHECKING

# Sử dụng TYPE_CHECKING để tránh circular imports
if TYPE_CHECKING:
    from ..core.square import Square
    from ..core.board import Board
    from ..core.move import Move

class PieceColor(Enum):
    """Màu quân cờ"""
    WHITE = "white"
    BLACK = "black"

    @property
    def opposite(self) -> 'PieceColor':
        """Lấy màu đối lập"""
        return PieceColor.BLACK if self == PieceColor.WHITE else PieceColor.WHITE

class PieceType(Enum):
    """Loại quân cờ"""
    PAWN = "pawn"
    KNIGHT = "knight" 
    BISHOP = "bishop"
    ROOK = "rook"
    QUEEN = "queen"
    KING = "king"

    @property
    def symbol(self) -> str:
        """Ký hiệu của quân cờ"""
        return self.name[0]

class Piece(ABC):
    """
    Class trừu tượng cho tất cả các quân cờ.
    Định nghĩa interface chung và logic cơ bản.
    """
    def __init__(self, color: PieceColor, square: 'Square'):
        """
        Khởi tạo quân cờ.
        
        Args:
            color: Màu của quân cờ (WHITE/BLACK)
            square: Ô hiện tại của quân cờ
        """
        self._color = color
        self._square = square
        self._has_moved = False

    # Properties cơ bản
    @property
    def color(self) -> PieceColor:
        """Màu của quân cờ"""
        return self._color

    @property
    def square(self) -> 'Square':
        """Ô hiện tại"""
        return self._square

    @square.setter
    def square(self, square: Optional['Square']) -> None:
        """Cập nhật ô mới"""
        self._square = square

    @property
    @abstractmethod
    def piece_type(self) -> PieceType:
        """Loại quân cờ - được implement bởi các class con"""
        pass

    @property
    def has_moved(self) -> bool:
        """Đã di chuyển lần nào chưa"""
        return self._has_moved

    @property
    def symbol(self) -> str:
        """
        Ký hiệu của quân cờ
        Returns:
            str: Ký tự viết hoa cho quân trắng, viết thường cho quân đen
        """
        symbol = self.piece_type.symbol
        return symbol if self.color == PieceColor.WHITE else symbol.lower()

    # Methods cho di chuyển
    @abstractmethod
    def get_legal_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy tất cả nước đi hợp lệ của quân cờ.
        Mỗi quân cờ cụ thể sẽ implement theo cách di chuyển riêng.

        Args:
            board: Bàn cờ hiện tại

        Returns:
            Danh sách các nước đi hợp lệ
        """
        pass

    def can_move_to(self, target_square: 'Square', board: 'Board') -> bool:
        """
        Kiểm tra quân cờ có thể di chuyển đến ô này không.

        Args:
            target_square: Ô đích
            board: Bàn cờ hiện tại

        Returns:
            True nếu có thể di chuyển đến ô đó
        """
        return target_square in [move.end_square for move in self.get_legal_moves(board)]

    def move_to(self, target_square: 'Square') -> None:
        """
        Di chuyển đến ô mới.

        Args:
            target_square: Ô đích
        """
        self._square = target_square
        self._has_moved = True

    # Utility methods
    def is_enemy(self, other: Optional['Piece']) -> bool:
        """
        Kiểm tra có phải quân địch không
        Args:
            other: Quân cờ cần kiểm tra
        """
        return other is not None and other.color != self.color

    def is_friend(self, other: Optional['Piece']) -> bool:
        """
        Kiểm tra có phải quân cùng phe không
        Args:
            other: Quân cờ cần kiểm tra
        """
        return other is not None and other.color == self.color

    @abstractmethod
    def clone(self) -> 'Piece':
        """
        Tạo bản sao của quân cờ
        Returns:
            Piece: Bản sao của quân cờ hiện tại
        """
        pass

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return f"{self.color.value} {self.piece_type.value} at {self.square.algebraic}"

    def __repr__(self) -> str:
        """String representation chi tiết"""
        return (f"{self.__class__.__name__}("
                f"color={self.color.value}, "
                f"square={self.square.algebraic})")