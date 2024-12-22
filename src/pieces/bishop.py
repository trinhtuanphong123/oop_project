# src/pieces/bishop.py

from typing import List, Tuple, TYPE_CHECKING
from .piece import Piece, PieceType, PieceColor

# Tránh circular imports
if TYPE_CHECKING:
    from ..core.board import Board
    from ..core.square import Square
    from ..core.move import Move

class Bishop(Piece):
    """
    Class Bishop kế thừa từ Piece, đại diện cho quân tượng trong cờ vua.
    Đặc điểm:
    - Di chuyển theo đường chéo
    - Không giới hạn số ô di chuyển
    - Không thể nhảy qua quân khác
    - Giá trị: 3 điểm
    """
    def __init__(self, color: PieceColor, square: 'Square'):
        """
        Khởi tạo quân tượng
        Args:
            color: Màu của quân cờ (WHITE/BLACK)
            square: Ô cờ mà quân tượng đang đứng
        """
        super().__init__(color, square)
        # Các hướng di chuyển chéo
        self._directions: List[Tuple[int, int]] = [
            (-1, -1),  # Chéo trên trái
            (-1, 1),   # Chéo trên phải
            (1, -1),   # Chéo dưới trái
            (1, 1)     # Chéo dưới phải
        ]

    @property
    def piece_type(self) -> PieceType:
        """Loại quân cờ"""
        return PieceType.BISHOP

    def get_legal_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy tất cả các nước đi hợp lệ của quân tượng
        Args:
            board: Bàn cờ hiện tại
        Returns:
            List[Move]: Danh sách các nước đi hợp lệ
        """
        from ..core.move import Move  # Local import để tránh circular import
        
        legal_moves = []
        current_square = self.square
        row, col = current_square.row, current_square.col

        # Kiểm tra từng hướng chéo
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

    def is_diagonal_move(self, start_row: int, start_col: int,
                        end_row: int, end_col: int) -> bool:
        """
        Kiểm tra xem một nước đi có phải là nước đi chéo không
        Args:
            start_row: Hàng xuất phát
            start_col: Cột xuất phát
            end_row: Hàng đích
            end_col: Cột đích
        Returns:
            bool: True nếu là nước đi chéo hợp lệ
        """
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        return row_diff == col_diff and row_diff > 0

    def clone(self) -> 'Bishop':
        """
        Tạo bản sao của quân tượng
        Returns:
            Bishop: Bản sao của quân tượng hiện tại
        """
        clone = Bishop(self.color, self.square)
        clone._has_moved = self._has_moved
        return clone

    @property
    def piece_value(self) -> int:
        """
        Giá trị của quân tượng cho việc tính điểm
        Returns:
            int: Giá trị quân tượng (3 điểm)
        """
        return 3

    @property
    def symbol(self) -> str:
        """
        Ký hiệu của quân tượng để hiển thị
        Returns:
            str: 'B' cho tượng trắng, 'b' cho tượng đen
        """
        return 'B' if self.color == PieceColor.WHITE else 'b'

    def __str__(self) -> str:
        """String representation của quân tượng"""
        return f"{self.color.value} Bishop at {self.square.algebraic}"

    def __repr__(self) -> str:
        """Chi tiết về quân tượng"""
        return f"Bishop(color={self.color}, square={self.square.algebraic})"