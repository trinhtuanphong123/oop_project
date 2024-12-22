# src/pieces/pawn.py

from typing import List, Optional, TYPE_CHECKING
from .piece import Piece, PieceType, PieceColor

# Sử dụng TYPE_CHECKING để tránh circular imports
if TYPE_CHECKING:
    from ..core.square import Square
    from ..core.board import Board
    from ..core.move import Move

class Pawn(Piece):
    """
    Class quân tốt kế thừa từ Piece.
    Có các đặc điểm riêng:
    - Đi thẳng về phía trước 1 ô
    - Được đi 2 ô ở nước đầu tiên
    - Bắt chéo quân địch
    - Phong cấp khi đến cuối bàn cờ
    - Bắt tốt qua đường (en passant)
    """
    def __init__(self, color: PieceColor, square: 'Square'):
        """
        Khởi tạo quân tốt
        Args:
            color: Màu quân tốt (WHITE/BLACK)
            square: Ô ban đầu của quân tốt
        """
        super().__init__(color, square)
        # Hàng cuối để phong cấp
        self._promotion_row = 0 if color == PieceColor.WHITE else 7
        # Cho phép bắt tốt qua đường
        self._can_be_captured_en_passant = False

    @property
    def piece_type(self) -> PieceType:
        """Loại quân cờ"""
        return PieceType.PAWN

    @property
    def direction(self) -> int:
        """
        Hướng di chuyển của quân tốt
        Returns:
            -1 cho trắng (đi lên), 1 cho đen (đi xuống)
        """
        return -1 if self.color == PieceColor.WHITE else 1

    @property
    def start_row(self) -> int:
        """
        Hàng xuất phát của quân tốt
        Returns:
            6 cho trắng, 1 cho đen
        """
        return 6 if self.color == PieceColor.WHITE else 1

    @property
    def can_be_captured_en_passant(self) -> bool:
        """Kiểm tra có thể bị bắt qua đường không"""
        return self._can_be_captured_en_passant

    @can_be_captured_en_passant.setter
    def can_be_captured_en_passant(self, value: bool):
        """Cập nhật trạng thái có thể bị bắt qua đường"""
        self._can_be_captured_en_passant = value

    def get_legal_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy tất cả nước đi hợp lệ của quân tốt
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước đi hợp lệ
        """
        moves = []
        current_row, current_col = self.square.row, self.square.col

        # Đi thẳng 1 ô
        next_row = current_row + self.direction
        if 0 <= next_row < 8:
            front_square = board.get_square(next_row, current_col)
            if not front_square.is_occupied():
                moves.extend(self._get_promotion_moves(front_square))

                # Đi thẳng 2 ô nếu là nước đầu
                if not self.has_moved and current_row == self.start_row:
                    two_ahead = board.get_square(next_row + self.direction, current_col)
                    if not two_ahead.is_occupied():
                        moves.append(self._create_move(two_ahead, can_be_en_passant=True))

        # Bắt chéo thông thường
        for col_offset in [-1, 1]:
            capture_col = current_col + col_offset
            if 0 <= next_row < 8 and 0 <= capture_col < 8:
                target_square = board.get_square(next_row, capture_col)
                if target_square.has_enemy_piece(self.color):
                    moves.extend(self._get_promotion_moves(target_square, is_capture=True))

        # Bắt tốt qua đường
        moves.extend(self._get_en_passant_moves(board))

        return moves

    def _get_promotion_moves(self, end_square: 'Square', is_capture: bool = False) -> List['Move']:
        """
        Tạo các nước đi phong cấp nếu tốt đến cuối bàn
        Args:
            end_square: Ô đích
            is_capture: Có phải nước bắt quân không
        Returns:
            Danh sách các nước đi phong cấp có thể
        """
        moves = []
        if end_square.row == self._promotion_row:
            promotion_pieces = [PieceType.QUEEN, PieceType.ROOK, 
                             PieceType.BISHOP, PieceType.KNIGHT]
            for piece_type in promotion_pieces:
                moves.append(self._create_move(
                    end_square,
                    is_capture=is_capture,
                    is_promotion=True,
                    promotion_piece_type=piece_type
                ))
        else:
            moves.append(self._create_move(end_square, is_capture=is_capture))
        return moves

    def _get_en_passant_moves(self, board: 'Board') -> List['Move']:
        """
        Lấy các nước đi bắt tốt qua đường
        Args:
            board: Bàn cờ hiện tại
        Returns:
            Danh sách các nước bắt tốt qua đường có thể
        """
        moves = []
        row, col = self.square.row, self.square.col
        
        if row == (3 if self.color == PieceColor.WHITE else 4):
            for col_offset in [-1, 1]:
                if 0 <= col + col_offset < 8:
                    adjacent_square = board.get_square(row, col + col_offset)
                    if (adjacent_square.is_occupied() and 
                        isinstance(adjacent_square.piece, Pawn) and
                        adjacent_square.piece.color != self.color and
                        adjacent_square.piece.can_be_captured_en_passant):
                        
                        target_square = board.get_square(row + self.direction, col + col_offset)
                        moves.append(self._create_move(
                            target_square,
                            is_capture=True,
                            is_en_passant=True
                        ))
        return moves

    def _create_move(self, end_square: 'Square', 
                    is_capture: bool = False,
                    is_promotion: bool = False,
                    is_en_passant: bool = False,
                    promotion_piece_type: Optional[PieceType] = None,
                    can_be_en_passant: bool = False) -> 'Move':
        """
        Tạo nước đi cho quân tốt
        Args:
            end_square: Ô đích
            is_capture: Có phải nước bắt quân không
            is_promotion: Có phải nước phong cấp không
            is_en_passant: Có phải nước bắt tốt qua đường không
            promotion_piece_type: Loại quân phong cấp
            can_be_en_passant: Có thể bị bắt qua đường ở nước tiếp theo không
        Returns:
            Move: Nước đi được tạo
        """
        from ..core.move import Move  # Import cục bộ để tránh circular import
        
        captured_piece = end_square.piece if is_capture else None
        move = Move(
            start_square=self.square,
            end_square=end_square,
            moving_piece=self,
            captured_piece=captured_piece,
            is_promotion=is_promotion,
            is_en_passant=is_en_passant,
            promotion_piece_type=promotion_piece_type
        )
        
        if can_be_en_passant:
            self._can_be_captured_en_passant = True
            
        return move

    def clone(self) -> 'Pawn':
        """
        Tạo bản sao của quân tốt
        Returns:
            Pawn: Bản sao của quân tốt hiện tại
        """
        clone = Pawn(self.color, self.square)
        clone._has_moved = self._has_moved
        clone._can_be_captured_en_passant = self._can_be_captured_en_passant
        return clone

    def __str__(self) -> str:
        """String representation"""
        return f"{self.color.value} Pawn at {self.square.algebraic}"