# src/pieces/king.py

from typing import List, Tuple, TYPE_CHECKING
from .piece import Piece, PieceType, PieceColor

# Tránh circular imports
if TYPE_CHECKING:
    from ..core.board import Board
    from ..core.square import Square
    from ..core.move import Move

class King(Piece):
    """
    Class quân Vua kế thừa từ Piece.
    Đặc điểm:
    - Di chuyển 1 ô theo mọi hướng
    - Có thể nhập thành với xe khi chưa di chuyển
    - Không thể đi vào ô bị tấn công
    - Là quân cờ quan trọng nhất, không có giá trị điểm
    """
    def __init__(self, color: PieceColor, square: 'Square'):
        """
        Khởi tạo quân Vua
        Args:
            color: Màu quân Vua (WHITE/BLACK)
            square: Ô ban đầu của quân Vua
        """
        super().__init__(color, square)
        # 8 hướng di chuyển của Vua
        self._directions: List[Tuple[int, int]] = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

    @property
    def piece_type(self) -> PieceType:
        """Loại quân cờ"""
        return PieceType.KING

    def get_legal_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy danh sách nước đi hợp lệ của Vua
        Args:
            board: Bàn cờ hiện tại
        Returns:
            List[Move]: Danh sách các nước đi hợp lệ
        """
        from ..core.move import Move  # Local import để tránh circular import
        
        legal_moves = []
        curr_row, curr_col = self.square.row, self.square.col

        # Kiểm tra các nước đi thông thường
        for d_row, d_col in self._directions:
            new_row, new_col = curr_row + d_row, curr_col + d_col
            
            if not board.is_valid_position(new_row, new_col):
                continue

            target_square = board.get_square(new_row, new_col)

            # Nếu ô trống
            if target_square.is_empty():
                legal_moves.append(
                    Move(
                        start_square=self.square,
                        end_square=target_square,
                        moving_piece=self
                    )
                )
            
            # Nếu có quân địch
            elif target_square.has_enemy_piece(self.color):
                legal_moves.append(
                    Move(
                        start_square=self.square,
                        end_square=target_square,
                        moving_piece=self,
                        captured_piece=target_square.piece
                    )
                )

        # Thêm nước nhập thành nếu có thể
        if not self.has_moved:
            castle_moves = self._get_castle_moves(board)
            legal_moves.extend(castle_moves)

        return legal_moves

    def _get_castle_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy các nước nhập thành hợp lệ
        Args:
            board: Bàn cờ hiện tại
        Returns:
            List[Move]: Danh sách nước nhập thành có thể
        """
        from ..core.move import Move
        castle_moves = []
        
        # Vị trí cơ bản cho nhập thành
        base_row = 7 if self.color == PieceColor.WHITE else 0
        king_col = 4

        # Kiểm tra nhập thành phải
        if self._can_castle_kingside(board, base_row):
            target_square = board.get_square(base_row, king_col + 2)
            castle_moves.append(
                Move(
                    start_square=self.square,
                    end_square=target_square,
                    moving_piece=self,
                    is_castle=True
                )
            )

        # Kiểm tra nhập thành trái
        if self._can_castle_queenside(board, base_row):
            target_square = board.get_square(base_row, king_col - 2)
            castle_moves.append(
                Move(
                    start_square=self.square,
                    end_square=target_square,
                    moving_piece=self,
                    is_castle=True
                )
            )

        return castle_moves

    def _can_castle_kingside(self, board: 'Board', row: int) -> bool:
        """
        Kiểm tra có thể nhập thành cánh vua
        Args:
            board: Bàn cờ hiện tại
            row: Hàng của quân vua
        Returns:
            bool: True nếu có thể nhập thành cánh vua
        """
        # Kiểm tra đường đi trống
        if not all(board.get_square(row, col).is_empty() 
                  for col in [5, 6]):
            return False

        # Kiểm tra xe còn tại vị trí
        rook_square = board.get_square(row, 7)
        rook = rook_square.piece
        return (rook is not None and 
                rook.piece_type == PieceType.ROOK and
                rook.color == self.color and
                not rook.has_moved)

    def _can_castle_queenside(self, board: 'Board', row: int) -> bool:
        """
        Kiểm tra có thể nhập thành cánh hậu
        Args:
            board: Bàn cờ hiện tại
            row: Hàng của quân vua
        Returns:
            bool: True nếu có thể nhập thành cánh hậu
        """
        # Kiểm tra đường đi trống
        if not all(board.get_square(row, col).is_empty() 
                  for col in [1, 2, 3]):
            return False

        # Kiểm tra xe còn tại vị trí
        rook_square = board.get_square(row, 0)
        rook = rook_square.piece
        return (rook is not None and 
                rook.piece_type == PieceType.ROOK and
                rook.color == self.color and
                not rook.has_moved)

    def clone(self) -> 'King':
        """
        Tạo bản sao của quân Vua
        Returns:
            King: Bản sao của quân Vua hiện tại
        """
        clone = King(self.color, self.square)
        clone._has_moved = self._has_moved
        return clone

    @property
    def symbol(self) -> str:
        """
        Ký hiệu của quân Vua để hiển thị
        Returns:
            str: 'K' cho Vua trắng, 'k' cho Vua đen
        """
        return 'K' if self.color == PieceColor.WHITE else 'k'

    def __str__(self) -> str:
        """String representation của quân Vua"""
        return f"{self.color.value} King at {self.square.algebraic}"

    def __repr__(self) -> str:
        """Chi tiết về quân Vua"""
        return f"King(color={self.color}, square={self.square.algebraic})"