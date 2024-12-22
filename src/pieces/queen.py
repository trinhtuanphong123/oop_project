# src/pieces/queen.py

from typing import List, Optional, Tuple, TYPE_CHECKING
from .piece import Piece, PieceType, PieceColor

# Tránh circular imports
if TYPE_CHECKING:
    from ..core.board import Board
    from ..core.square import Square
    from ..core.move import Move

class Queen(Piece):
    """
    Class Queen kế thừa từ Piece, đại diện cho quân hậu trong cờ vua.
    Đặc điểm:
    - Di chuyển kết hợp cả đường thẳng và đường chéo
    - Không giới hạn số ô di chuyển
    - Giá trị: 9 điểm
    """
    def __init__(self, color: PieceColor, square: 'Square'):
        """
        Khởi tạo quân hậu
        Args:
            color: Màu của quân cờ (WHITE/BLACK)
            square: Ô cờ mà quân hậu đang đứng
        """
        super().__init__(color, square)
        # Định nghĩa các hướng di chuyển có thể (thẳng và chéo)
        self._directions: List[Tuple[int, int]] = [
            # Các hướng thẳng (như xe)
            (-1, 0),  # Lên
            (1, 0),   # Xuống
            (0, -1),  # Trái
            (0, 1),   # Phải
            # Các hướng chéo (như tượng)
            (-1, -1), # Chéo trên trái
            (-1, 1),  # Chéo trên phải
            (1, -1),  # Chéo dưới trái
            (1, 1)    # Chéo dưới phải
        ]

    @property
    def piece_type(self) -> PieceType:
        """Loại quân cờ"""
        return PieceType.QUEEN

    def get_legal_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy tất cả các nước đi hợp lệ của quân hậu
        Args:
            board: Bàn cờ hiện tại
        Returns:
            List[Move]: Danh sách các nước đi hợp lệ
        """
        from ..core.move import Move  # Local import để tránh circular import
        
        legal_moves = []
        current_square = self.square
        row, col = current_square.row, current_square.col

        # Kiểm tra tất cả các hướng (thẳng và chéo)
        for dir_row, dir_col in self._directions:
            next_row, next_col = row + dir_row, col + dir_col
            
            # Tiếp tục di chuyển theo hướng cho đến khi gặp chướng ngại
            while board.is_valid_position(next_row, next_col):
                target_square = board.get_square(next_row, next_col)
                
                # Nếu ô trống
                if target_square.is_empty():
                    legal_moves.append(
                        Move(
                            start_square=current_square,
                            end_square=target_square,
                            moving_piece=self
                        )
                    )
                
                # Nếu gặp quân địch
                elif target_square.has_enemy_piece(self.color):
                    legal_moves.append(
                        Move(
                            start_square=current_square,
                            end_square=target_square,
                            moving_piece=self,
                            captured_piece=target_square.piece
                        )
                    )
                    break
                
                # Nếu gặp quân cùng màu
                else:
                    break

                next_row += dir_row
                next_col += dir_col

        return legal_moves

    def clone(self) -> 'Queen':
        """
        Tạo bản sao của quân hậu
        Returns:
            Queen: Bản sao của quân hậu hiện tại
        """
        clone = Queen(self.color, self.square)
        clone._has_moved = self._has_moved
        return clone

    @property
    def piece_value(self) -> int:
        """
        Giá trị của quân hậu cho việc tính điểm
        Returns:
            int: Giá trị quân hậu (9 điểm)
        """
        return 9

    @property
    def symbol(self) -> str:
        """
        Ký hiệu của quân hậu để hiển thị
        Returns:
            str: 'Q' cho hậu trắng, 'q' cho hậu đen
        """
        return 'Q' if self.color == PieceColor.WHITE else 'q'

    def __str__(self) -> str:
        """String representation của quân hậu"""
        return f"{self.color.value} Queen at {self.square.algebraic}"

    def __repr__(self) -> str:
        """Chi tiết về quân hậu"""
        return f"Queen(color={self.color}, square={self.square.algebraic})"