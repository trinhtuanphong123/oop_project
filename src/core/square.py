# src/core/square.py

from typing import Optional, Tuple
from ..pieces.piece import Piece, PieceColor  # Import từ pieces package

class Square:
    """
    Class đại diện cho một ô trên bàn cờ.
    Quản lý:
    - Vị trí của ô
    - Quân cờ đang đứng trên ô
    - Trạng thái của ô
    """
    def __init__(self, row: int, col: int):
        """
        Khởi tạo một ô với vị trí xác định
        Args:
            row: Số hàng (0-7)
            col: Số cột (0-7)
        """
        if not (0 <= row < 8 and 0 <= col < 8):
            raise ValueError(f"Invalid position: ({row}, {col})")
            
        self._row = row
        self._col = col
        self._piece: Optional[Piece] = None

    # Properties cơ bản
    @property
    def row(self) -> int:
        """Số hàng của ô"""
        return self._row

    @property
    def col(self) -> int:
        """Số cột của ô"""
        return self._col

    @property
    def piece(self) -> Optional[Piece]:
        """Quân cờ trên ô"""
        return self._piece

    @piece.setter
    def piece(self, piece: Optional[Piece]) -> None:
        """Đặt quân cờ lên ô"""
        self._piece = piece
        if piece:
            piece.square = self  # Cập nhật reference đến Square trong Piece

    @property
    def position(self) -> Tuple[int, int]:
        """Lấy vị trí dưới dạng tuple"""
        return (self._row, self._col)

    @property
    def is_empty(self) -> bool:
        """Kiểm tra ô có trống không"""
        return self._piece is None

    @property
    def algebraic(self) -> str:
        """
        Chuyển đổi vị trí sang ký hiệu đại số
        Ví dụ: (0,0) -> 'a8', (7,7) -> 'h1'
        """
        col_letter = chr(ord('a') + self._col)
        row_number = 8 - self._row
        return f"{col_letter}{row_number}"

    # Phương thức kiểm tra trạng thái
    def is_occupied(self) -> bool:
        """Kiểm tra ô có quân không"""
        return self._piece is not None

    def has_enemy_piece(self, color: PieceColor) -> bool:
        """
        Kiểm tra có quân địch không
        Args:
            color: Màu quân cờ cần so sánh
        """
        return self.is_occupied() and self._piece.color != color

    def has_friendly_piece(self, color: PieceColor) -> bool:
        """
        Kiểm tra có quân đồng minh không
        Args:
            color: Màu quân cờ cần so sánh
        """
        return self.is_occupied() and self._piece.color == color

    # Phương thức thao tác với quân cờ
    def place_piece(self, piece: Piece) -> None:
        """
        Đặt quân cờ lên ô
        Args:
            piece: Quân cờ cần đặt
        """
        self._piece = piece
        if piece:
            piece.square = self

    def remove_piece(self) -> Optional[Piece]:
        """
        Lấy quân cờ ra khỏi ô
        Returns:
            Quân cờ đã lấy ra hoặc None
        """
        piece = self._piece
        self._piece = None
        if piece:
            piece.square = None
        return piece

    # Magic methods
    def __eq__(self, other: object) -> bool:
        """So sánh hai ô dựa trên vị trí"""
        if not isinstance(other, Square):
            return NotImplemented
        return self._row == other._row and self._col == other._col

    def __hash__(self) -> int:
        """Hash của ô dựa trên vị trí"""
        return hash((self._row, self._col))

    def __str__(self) -> str:
        """String representation ngắn gọn"""
        return f"{self.algebraic}: {self._piece if self._piece else 'empty'}"