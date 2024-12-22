# src/core/game_rules.py

from typing import List, Optional, Set, TYPE_CHECKING
from .board import Board
from ..pieces.piece import Piece, PieceColor, PieceType
from .move import Move
from .square import Square

# Import trực tiếp các class cần thiết để kiểm tra instance
from ..pieces.king import King
from ..pieces.pawn import Pawn
from ..pieces.rook import Rook

# Import các class chỉ dùng cho type hints
if TYPE_CHECKING:
    from ..pieces.queen import Queen
    from ..pieces.bishop import Bishop
    from ..pieces.knight import Knight
class GameRules:
    """
    Class GameRules - Quản lý và thực thi luật chơi cờ vua.
    
    Trách nhiệm:
    1. Kiểm tra tính hợp lệ của nước đi:
       - Luật di chuyển cơ bản của từng loại quân
       - Các nước đi đặc biệt (nhập thành, bắt tốt qua đường, phong cấp)
       - Kiểm tra tình trạng chiếu
       
    2. Xác định các nước đi có thể:
       - Lấy tất cả nước đi hợp lệ của một quân
       - Kiểm tra đường đi có bị chặn
       - Xác định các ô bị tấn công
    """

    def __init__(self, board: Board):
        self._board = board

    def is_valid_move(self, move: Move) -> bool:
        """
        Kiểm tra một nước đi có hợp lệ không
        Args:
            move: Nước đi cần kiểm tra
        Returns:
            True nếu nước đi hợp lệ
        """
        # 1. Kiểm tra vị trí hợp lệ
        if not self._is_valid_position(move.start_square) or \
           not self._is_valid_position(move.end_square):
            return False

        # 2. Kiểm tra quân cờ
        piece = move.moving_piece
        if not piece:
            return False

        # 3. Kiểm tra đường đi
        if not self._is_path_clear(move):
            return False

        # 4. Kiểm tra nước đi đặc biệt
        if move.is_castle:
            return self.is_valid_castling(move)
        elif move.is_en_passant:
            return self.is_valid_en_passant(move)
        elif move.is_promotion:
            return self.is_valid_promotion(move)
        
        # 5. Kiểm tra bắt quân
        if move.is_capture:
            return self._is_valid_capture(move)

        return True

    def get_legal_moves(self, piece: Piece) -> List[Move]:
        """
        Lấy tất cả nước đi hợp lệ của một quân
        Args:
            piece: Quân cờ cần kiểm tra
        Returns:
            Danh sách các nước đi hợp lệ
        """
        moves = []
        start_square = piece.square

        # Lấy các hướng di chuyển có thể của quân cờ
        directions = piece.get_move_directions()
        
        for direction in directions:
            # Với quân có thể di chuyển nhiều ô (Queen, Rook, Bishop)
            if piece.can_move_multiple_steps():
                moves.extend(self._get_moves_in_direction(piece, direction))
            # Với quân chỉ di chuyển 1 ô (King) hoặc đặc biệt (Knight)
            else:
                end_row = start_square.row + direction[0]
                end_col = start_square.col + direction[1]
                
                if self._board.is_valid_position(end_row, end_col):
                    end_square = self._board.get_square(end_row, end_col)
                    move = Move(start_square, end_square)
                    if self.is_valid_move(move):
                        moves.append(move)

        # Thêm các nước đi đặc biệt
        if isinstance(piece, King):
            moves.extend(self._get_castling_moves(piece))
        elif isinstance(piece, Pawn):
            moves.extend(self._get_pawn_special_moves(piece))

        return moves

    def is_valid_castling(self, move: Move) -> bool:
        """
        Kiểm tra nước nhập thành có hợp lệ không
        Args:
            move: Nước nhập thành cần kiểm tra
        Returns:
            True nếu nước nhập thành hợp lệ
        """
        king = move.moving_piece
        if not isinstance(king, King) or king.has_moved:
            return False

        # Xác định phía nhập thành
        row = king.square.row
        is_kingside = move.end_square.col > move.start_square.col
        rook_col = 7 if is_kingside else 0
        path_cols = range(5, 7) if is_kingside else range(1, 4)

        # Kiểm tra xe
        rook_square = self._board.get_square(row, rook_col)
        rook = rook_square.piece
        if not isinstance(rook, Rook) or rook.has_moved:
            return False

        # Kiểm tra đường đi trống
        for col in path_cols:
            if self._board.get_square(row, col).is_occupied():
                return False

        # Kiểm tra không bị chiếu khi nhập thành
        if self.is_square_attacked(king.square, king.color.opposite):
            return False
            
        # Kiểm tra các ô vua đi qua không bị chiếu
        for col in path_cols:
            square = self._board.get_square(row, col)
            if self.is_square_attacked(square, king.color.opposite):
                return False

        return True

    def is_valid_en_passant(self, move: Move) -> bool:
        """
        Kiểm tra nước bắt tốt qua đường có hợp lệ không
        Args:
            move: Nước đi cần kiểm tra
        Returns:
            True nếu nước bắt tốt qua đường hợp lệ
        """
        pawn = move.moving_piece
        if not isinstance(pawn, Pawn):
            return False

        # Kiểm tra điều kiện bắt tốt qua đường
        if pawn.color == PieceColor.WHITE:
            if move.start_square.row != 3:  # Tốt trắng phải ở hàng 5
                return False
        else:
            if move.start_square.row != 4:  # Tốt đen phải ở hàng 4
                return False

        # Kiểm tra tốt địch
        captured_square = self._board.get_square(
            move.start_square.row,
            move.end_square.col
        )
        captured_pawn = captured_square.piece
        
        if not isinstance(captured_pawn, Pawn) or \
           captured_pawn.color == pawn.color:
            return False

        # Kiểm tra tốt địch vừa đi 2 bước
        last_move = self._board.last_move
        if not last_move or \
           last_move.moving_piece != captured_pawn or \
           abs(last_move.start_square.row - last_move.end_square.row) != 2:
            return False

        return True

    def is_valid_promotion(self, move: Move) -> bool:
        """
        Kiểm tra nước phong cấp có hợp lệ không
        Args:
            move: Nước đi cần kiểm tra
        Returns:
            True nếu nước phong cấp hợp lệ
        """
        pawn = move.moving_piece
        if not isinstance(pawn, Pawn):
            return False

        # Kiểm tra vị trí phong cấp
        end_row = move.end_square.row
        if pawn.color == PieceColor.WHITE:
            return end_row == 0  # Tốt trắng phải đến hàng 8
        else:
            return end_row == 7  # Tốt đen phải đến hàng 1

    def is_square_attacked(self, square: Square, by_color: PieceColor) -> bool:
        """
        Kiểm tra một ô có bị tấn công bởi quân địch không
        Args:
            square: Ô cần kiểm tra
            by_color: Màu của bên tấn công
        Returns:
            True nếu ô bị tấn công
        """
        attacking_pieces = self._board.get_pieces(by_color)
        
        for piece in attacking_pieces:
            if any(move.end_square == square 
                  for move in self.get_legal_moves(piece)):
                return True
        return False

    def _is_valid_position(self, square: Square) -> bool:
        """Kiểm tra vị trí có hợp lệ trên bàn cờ"""
        return 0 <= square.row < 8 and 0 <= square.col < 8

    def _is_path_clear(self, move: Move) -> bool:
        """
        Kiểm tra đường đi có bị chặn không
        Args:
            move: Nước đi cần kiểm tra
        Returns:
            True nếu đường đi trống
        """
        # Knight có thể nhảy qua quân khác
        if move.moving_piece.piece_type == PieceType.KNIGHT:
            return True

        path = self._get_path_squares(move)
        return all(not square.is_occupied() for square in path)

    def _is_valid_capture(self, move: Move) -> bool:
        """
        Kiểm tra nước bắt quân có hợp lệ không
        Args:
            move: Nước đi cần kiểm tra
        Returns:
            True nếu nước bắt quân hợp lệ
        """
        target = move.end_square.piece
        return target and target.color != move.moving_piece.color

    def _get_moves_in_direction(self, piece: Piece, direction: tuple) -> List[Move]:
        """
        Lấy các nước đi theo một hướng
        Args:
            piece: Quân cờ đang xét
            direction: Tuple (dx, dy) chỉ hướng di chuyển
        Returns:
            Danh sách các nước đi có thể
        """
        moves = []
        start = piece.square
        dx, dy = direction
        
        current_row = start.row + dx
        current_col = start.col + dy
        
        while self._board.is_valid_position(current_row, current_col):
            end_square = self._board.get_square(current_row, current_col)
            
            # Nếu gặp quân cùng màu thì dừng
            if end_square.is_occupied() and \
               end_square.piece.color == piece.color:
                break
                
            # Thêm nước đi
            move = Move(start, end_square)
            moves.append(move)
            
            # Nếu gặp quân địch thì dừng sau khi thêm nước bắt
            if end_square.is_occupied():
                break
                
            current_row += dx
            current_col += dy
            
        return moves

    def _get_castling_moves(self, king: 'King') -> List[Move]:
        """
        Lấy các nước nhập thành có thể
        Args:
            king: Quân vua cần kiểm tra
        Returns:
            Danh sách các nước nhập thành có thể
        """
        moves = []
        if king.has_moved:
            return moves

        row = king.square.row
        # Nhập thành ngắn
        kingside_square = self._board.get_square(row, 6)
        kingside_move = Move(king.square, kingside_square, is_castle=True)
        if self.is_valid_castling(kingside_move):
            moves.append(kingside_move)

        # Nhập thành dài
        queenside_square = self._board.get_square(row, 2)
        queenside_move = Move(king.square, queenside_square, is_castle=True)
        if self.is_valid_castling(queenside_move):
            moves.append(queenside_move)

        return moves

    def _get_pawn_special_moves(self, pawn: 'Pawn') -> List[Move]:
        """
        Lấy các nước đi đặc biệt của tốt
        Args:
            pawn: Quân tốt cần kiểm tra
        Returns:
            Danh sách các nước đi đặc biệt
        """
        moves = []
        start = pawn.square
        
        # Đi 2 ô lần đầu
        if not pawn.has_moved:
            direction = -2 if pawn.color == PieceColor.WHITE else 2
            end_row = start.row + direction
            if self._board.is_valid_position(end_row, start.col):
                end_square = self._board.get_square(end_row, start.col)
                if not end_square.is_occupied():
                    moves.append(Move(start, end_square))

        # Bắt tốt qua đường
        for col_offset in [-1, 1]:
            end_col = start.col + col_offset
            if self._board.is_valid_position(start.row, end_col):
                end_square = self._board.get_square(
                    start.row + (1 if pawn.color == PieceColor.BLACK else -1),
                    end_col
                )
                move = Move(start, end_square, is_en_passant=True)
                if self.is_valid_en_passant(move):
                    moves.append(move)

        return moves

    def _get_path_squares(self, move: Move) -> List[Square]:
        """
        Lấy danh sách các ô trên đường đi
        Args:
            move: Nước đi cần kiểm tra
        Returns:
            Danh sách các ô trên đường đi
        """
        path = []
        start = move.start_square
        end = move.end_square
        
        # Tính hướng di chuyển
        row_step = 0 if start.row == end.row else \
                  (end.row - start.row) // abs(end.row - start.row)
        col_step = 0 if start.col == end.col else \
                  (end.col - start.col) // abs(end.col - start.col)
        
        # Thêm các ô trung gian (không bao gồm ô đích)
        current_row = start.row + row_step
        current_col = start.col + col_step
        
        while (current_row, current_col) != (end.row, end.col):
            path.append(self._board.get_square(current_row, current_col))
            current_row += row_step
            current_col += col_step
            
        return path