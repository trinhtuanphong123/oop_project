# src/pieces/rook.py

from typing import List, Tuple, TYPE_CHECKING
from .piece import Piece, PieceType, PieceColor

# Tránh circular imports
if TYPE_CHECKING:
    from ..core.board import Board
    from ..core.square import Square
    from ..core.move import Move

class Rook(Piece):
    """
    Class Rook kế thừa từ Piece, đại diện cho quân xe trong cờ vua.
    Đặc điểm:
    - Di chuyển theo chiều ngang hoặc dọc
    - Không giới hạn số ô di chuyển
    - Có thể thực hiện nhập thành với vua
    - Giá trị: 5 điểm
    """

    def __init__(self, color: PieceColor, square: 'Square'):
        """
        Khởi tạo quân xe
        Args:
            color: Màu của quân cờ (WHITE/BLACK)
            square: Ô cờ mà quân xe đang đứng
        """
        super().__init__(color, square)
        # Các hướng di chuyển của xe: ngang và dọc
        self._directions: List[Tuple[int, int]] = [
            (-1, 0),  # Lên
            (1, 0),   # Xuống
            (0, -1),  # Trái
            (0, 1)    # Phải
        ]

    @property
    def piece_type(self) -> PieceType:
        """Loại quân cờ"""
        return PieceType.ROOK

    def get_legal_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy tất cả các nước đi hợp lệ của quân xe
        Args:
            board: Bàn cờ hiện tại
        Returns:
            List[Move]: Danh sách các nước đi hợp lệ
        """
        from ..core.move import Move  # Local import để tránh circular import
        
        legal_moves = []
        current_square = self.square
        row, col = current_square.row, current_square.col

        # Kiểm tra tất cả các hướng
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

    def move_to(self, target_square: 'Square') -> None:
        """
        Di chuyển quân xe đến ô mới và cập nhật trạng thái
        Args:
            target_square: Ô đích
        """
        super().move_to(target_square)
        self._has_moved = True

    def can_castle(self) -> bool:
        """
        Kiểm tra quân xe có thể thực hiện nhập thành không
        Returns:
            bool: True nếu có thể nhập thành (chưa di chuyển)
        """
        return not self.has_moved

    def clone(self) -> 'Rook':
        """
        Tạo bản sao của quân xe
        Returns:
            Rook: Bản sao của quân xe hiện tại
        """
        clone = Rook(self.color, self.square)
        clone._has_moved = self._has_moved
        return clone

    @property
    def piece_value(self) -> int:
        """
        Giá trị của quân xe cho việc tính điểm
        Returns:
            int: Giá trị quân xe (5 điểm)
        """
        return 5

    @property
    def symbol(self) -> str:
        """
        Ký hiệu của quân xe để hiển thị
        Returns:
            str: 'R' cho xe trắng, 'r' cho xe đen
        """
        return 'R' if self.color == PieceColor.WHITE else 'r'

    def __str__(self) -> str:
        """String representation của quân xe"""
        return f"{self.color.value} Rook at {self.square.algebraic}"

    def __repr__(self) -> str:
        """Chi tiết về quân xe"""
        return (f"Rook(color={self.color}, square={self.square.algebraic}, "
                f"has_moved={self.has_moved})")