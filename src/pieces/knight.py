# src/pieces/knight.py

from typing import List, Tuple, TYPE_CHECKING
from .piece import Piece, PieceType, PieceColor

# Tránh circular imports
if TYPE_CHECKING:
    from ..core.board import Board
    from ..core.square import Square
    from ..core.move import Move

class Knight(Piece):
    """
    Class Knight kế thừa từ Piece, đại diện cho quân mã trong cờ vua.
    Đặc điểm:
    - Di chuyển theo hình chữ L (2 ô theo một hướng và 1 ô theo hướng vuông góc)
    - Có thể nhảy qua các quân khác
    - Giá trị: 3 điểm
    """
    def __init__(self, color: PieceColor, square: 'Square'):
        """
        Khởi tạo quân mã
        Args:
            color: Màu của quân cờ (WHITE/BLACK)
            square: Ô cờ mà quân mã đang đứng
        """
        super().__init__(color, square)
        # Các hướng di chuyển có thể của mã
        self._move_offsets: List[Tuple[int, int]] = [
            (-2, -1), (-2, 1),  # Lên 2, trái/phải 1
            (-1, -2), (-1, 2),  # Lên 1, trái/phải 2
            (1, -2), (1, 2),    # Xuống 1, trái/phải 2
            (2, -1), (2, 1)     # Xuống 2, trái/phải 1
        ]

    @property
    def piece_type(self) -> PieceType:
        """Loại quân cờ"""
        return PieceType.KNIGHT

    def get_legal_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy tất cả các nước đi hợp lệ của quân mã
        Args:
            board: Bàn cờ hiện tại
        Returns:
            List[Move]: Danh sách các nước đi hợp lệ
        """
        from ..core.move import Move  # Local import để tránh circular import
        
        legal_moves = []
        current_square = self.square
        current_row, current_col = current_square.row, current_square.col

        # Kiểm tra từng hướng di chuyển có thể
        for offset_row, offset_col in self._move_offsets:
            new_row = current_row + offset_row
            new_col = current_col + offset_col

            # Kiểm tra vị trí mới có hợp lệ không
            if board.is_valid_position(new_row, new_col):
                target_square = board.get_square(new_row, new_col)

                # Nếu ô trống
                if target_square.is_empty():
                    legal_moves.append(
                        Move(
                            start_square=current_square,
                            end_square=target_square,
                            moving_piece=self
                        )
                    )
                
                # Nếu có quân địch
                elif target_square.has_enemy_piece(self.color):
                    legal_moves.append(
                        Move(
                            start_square=current_square,
                            end_square=target_square,
                            moving_piece=self,
                            captured_piece=target_square.piece
                        )
                    )

        return legal_moves

    def is_knight_move(self, start_row: int, start_col: int, 
                      end_row: int, end_col: int) -> bool:
        """
        Kiểm tra xem một nước đi có phải là nước đi hợp lệ của mã không
        Args:
            start_row: Hàng xuất phát
            start_col: Cột xuất phát
            end_row: Hàng đích
            end_col: Cột đích
        Returns:
            bool: True nếu là nước đi hợp lệ của mã, False nếu không
        """
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        
        # Nước đi hợp lệ của mã là 2-1 hoặc 1-2
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def clone(self) -> 'Knight':
        """
        Tạo bản sao của quân mã
        Returns:
            Knight: Bản sao của quân mã hiện tại
        """
        clone = Knight(self.color, self.square)
        clone._has_moved = self._has_moved
        return clone

    @property
    def piece_value(self) -> int:
        """
        Giá trị của quân mã cho việc tính điểm
        Returns:
            int: Giá trị quân mã (3 điểm)
        """
        return 3

    @property
    def symbol(self) -> str:
        """
        Ký hiệu của quân mã để hiển thị
        Returns:
            str: 'N' cho mã trắng, 'n' cho mã đen
        """
        return 'N' if self.color == PieceColor.WHITE else 'n'

    def __str__(self) -> str:
        """String representation của quân mã"""
        return f"{self.color.value} Knight at {self.square.algebraic}"

    def __repr__(self) -> str:
        """Chi tiết về quân mã"""
        return f"Knight(color={self.color}, square={self.square.algebraic})"