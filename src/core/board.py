# src/core/board.py

from typing import List, Optional, Dict, Set
from ..pieces.piece import Piece, PieceColor
from .square import Square
from .move import Move

class Board:
    """
    Class Board - Đại diện cho bàn cờ vua.
    
    Trách nhiệm:
    1. Quản lý cấu trúc bàn cờ:
       - Ma trận 8x8 ô cờ
       - Vị trí các quân cờ
       - Danh sách quân bị bắt
    
    2. Cung cấp thao tác cơ bản:
       - Đặt/xóa quân cờ
       - Di chuyển quân cờ
       - Truy xuất thông tin ô cờ
    """

    def __init__(self):
        """Khởi tạo bàn cờ trống"""
        # Ma trận 8x8 ô cờ
        self._squares: List[List[Square]] = [
            [Square(row, col) for col in range(8)]
            for row in range(8)
        ]
        
        # Quản lý quân cờ theo màu
        self._pieces: Dict[PieceColor, Set[Piece]] = {
            PieceColor.WHITE: set(),
            PieceColor.BLACK: set()
        }
        
        # Danh sách quân bị bắt
        self._captured_pieces: List[Piece] = []

    def get_square(self, row: int, col: int) -> Optional[Square]:
        """
        Lấy ô cờ tại vị trí chỉ định
        Args:
            row: Số hàng (0-7)
            col: Số cột (0-7)
        Returns:
            Square hoặc None nếu vị trí không hợp lệ
        """
        if self.is_valid_position(row, col):
            return self._squares[row][col]
        return None

    def get_pieces(self, color: PieceColor) -> Set[Piece]:
        """
        Lấy tất cả quân cờ của một màu
        Args:
            color: Màu cần lấy quân
        Returns:
            Set các quân cờ
        """
        return self._pieces[color].copy()

    def get_captured_pieces(self) -> List[Piece]:
        """
        Lấy danh sách quân bị bắt
        Returns:
            List các quân cờ đã bị bắt
        """
        return self._captured_pieces.copy()

    def place_piece(self, piece: Piece, square: Square) -> bool:
        """
        Đặt một quân cờ lên ô chỉ định
        Args:
            piece: Quân cờ cần đặt
            square: Ô cần đặt
        Returns:
            True nếu đặt thành công
        """
        if square.is_occupied():
            return False

        square.piece = piece
        piece.square = square
        self._pieces[piece.color].add(piece)
        return True

    def remove_piece(self, square: Square) -> Optional[Piece]:
        """
        Xóa quân cờ khỏi ô chỉ định
        Args:
            square: Ô cần xóa quân
        Returns:
            Quân cờ đã xóa hoặc None
        """
        piece = square.piece
        if piece:
            square.piece = None
            piece.square = None
            self._pieces[piece.color].remove(piece)
        return piece

    def move_piece(self, from_square: Square, to_square: Square) -> bool:
        """
        Di chuyển quân cờ giữa hai ô
        Args:
            from_square: Ô xuất phát
            to_square: Ô đích
        Returns:
            True nếu di chuyển thành công
        """
        piece = from_square.piece
        if not piece:
            return False

        # Nếu ô đích có quân, thêm vào danh sách bị bắt
        captured = to_square.piece
        if captured:
            self.remove_piece(to_square)
            self._captured_pieces.append(captured)

        # Di chuyển quân
        from_square.piece = None
        to_square.piece = piece
        piece.square = to_square
        return True

    def clear(self) -> None:
        """Xóa tất cả quân cờ khỏi bàn cờ"""
        for row in range(8):
            for col in range(8):
                square = self._squares[row][col]
                if square.piece:
                    self.remove_piece(square)

    def is_valid_position(self, row: int, col: int) -> bool:
        """
        Kiểm tra một vị trí có hợp lệ trên bàn cờ không
        Args:
            row: Số hàng
            col: Số cột
        Returns:
            True nếu vị trí hợp lệ
        """
        return 0 <= row < 8 and 0 <= col < 8

    def get_piece_at(self, row: int, col: int) -> Optional[Piece]:
        """
        Lấy quân cờ tại vị trí chỉ định
        Args:
            row: Số hàng
            col: Số cột
        Returns:
            Quân cờ hoặc None nếu ô trống
        """
        square = self.get_square(row, col)
        return square.piece if square else None

    def __str__(self) -> str:
        """Hiển thị trạng thái bàn cờ dạng text"""
        board_str = []
        for row in range(8):
            row_str = []
            for col in range(8):
                piece = self._squares[row][col].piece
                row_str.append(str(piece) if piece else '.')
            board_str.append(' '.join(row_str))
        return '\n'.join(board_str)

    def __repr__(self) -> str:
        """Hiển thị thông tin debug của bàn cờ"""
        return f"Board(white_pieces={len(self._pieces[PieceColor.WHITE])}, " \
               f"black_pieces={len(self._pieces[PieceColor.BLACK])}, " \
               f"captured_pieces={len(self._captured_pieces)})"