import pygame
import os
import sys

pygame.init()
os.chdir("/Users/owenreiss/Desktop/Coding/python/chess_images")

class Piece(pygame.sprite.Sprite):
    def __init__(self, color, piece, square, coordinates=None):
        super().__init__()
        self.piece = piece
        self.color = color
        self.square = square
        self.color_piece = color + piece
        self.image = pygame.image.load(color + piece + ".png")
        self.image = pygame.transform.scale(self.image, (60, 60) if piece != "p" else (48, 60))
        self.rect = self.image.get_rect()
        if square is None:
            self.coordinates = coordinates
            self.rect.center = coordinates
        else:
            c = (square % 8, square // 8)
            self.coordinates = ((90 * c[0]) + 45, 720 - ((90 * c[1]) + 45))
        self.rect.center = self.coordinates

    def __repr__(self):
        # return {"w": "white", "b": "black"}[self.color] + " " + {"r": "rook", "n": "knight", "b": "bishop", "q": "queen", "k": "king", "p": "pawn"}[self.piece] + f" on square {self.square}"
        return f'Piece("{self.color}", "{self.piece}", "{self.square}")'

    def draw(self):
        DISPLAY.blit(self.image, self.rect)

class MoveIndicator(pygame.sprite.Sprite):
    def __init__(self, square, is_square, legal_illegal=""):
        super().__init__()
        self.square = square
        self.is_square = is_square
        self.image = pygame.image.load(f"g.png") if is_square else pygame.image.load(f"{legal_illegal}legal_square.png")
        self.rect = self.image.get_rect()
        c = (square % 8, square // 8)
        self.coordinates = ((90 * c[0]) + 45, 720 - ((90 * c[1]) + 45))
        self.rect.center = self.coordinates

    def __repr__(self):
        return f"Indicator on square {self.square}"
    
    def draw(self):
        DISPLAY.blit(self.image, self.rect)

class Text(pygame.sprite.Sprite):
    def __init__(self, text, coordinates, size, side):
        super().__init__()
        font = pygame.font.Font("freesansbold.ttf", size)
        self.image = font.render(text, True, (0,) * 3)
        self.text = text
        self.rect = self.image.get_rect()
        if side is None:
            self.rect.center = coordinates
        elif side == "bl":
            self.rect.bottomleft = coordinates
        elif side:
            self.rect.midleft = coordinates
        else:
            self.rect.midright = coordinates

    def __repr__(self):
        return f'Text object saying "{self.text}"'

    def draw(self):
        DISPLAY.blit(self.image, self.rect)

DISPLAY = pygame.display.set_mode((1100, 720))
pygame.display.set_caption("Chess")
FPS = pygame.time.Clock()
BOARDIMG = pygame.image.load("board.png")
BOARDIMG = pygame.transform.scale(BOARDIMG, (720,) * 2)
BOARDRECT = BOARDIMG.get_rect()
BOARDRECT.bottomleft = (0, 720)
LEGAL_MOVES = {"k": {(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)}, "n": {(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)}, "b": {tuple((x, x) for x in range(1, 8)), tuple((x, x) for x in reversed(range(-7, 0))), tuple((x, -x) for x in range(1, 8)), tuple((x, -x) for x in reversed(range(-7, 0)))}, "r": {tuple((0, x) for x in range(1, 8)), tuple((0, x) for x in reversed(range(-7, 0))), tuple((x, 0) for x in range(1, 8)), tuple((x, 0) for x in reversed(range(-7, 0)))}}
LEGAL_MOVES["q"] = LEGAL_MOVES["b"] | LEGAL_MOVES["r"]
START_BOARD = tuple(Piece("w", "rnbqkbnr"[x], x) for x in range(8)) + tuple(Piece("w", "p", x) for x in range(8, 16)) + ((None,) * 32) + tuple(Piece("b", "p", x) for x in range(48, 56)) + tuple(Piece("b", "rnbqkbnr"[x], x + 56) for x in range(8))
FILES = "abcdefgh"

def get_legal_moves(square, board):
    piece = board[square]
    if piece is None:
        raise ValueError(f"No piece on square {square}")
    piece_type = piece.piece
    piece_color = piece.color
    legal_squares = set()
    if piece_type == "p":
        if piece_color == "w":
            if board[square + 8] is None:
                legal_squares.add(square + 8)
            if square in range(8, 16) and board[square + 16] is None and legal_squares:
                legal_squares.add(square + 16)
            if square % 8 and not board[square + 7] is None:
                if board[square + 7].color == "b":
                    legal_squares.add(square + 7)
            if (square - 7) % 8 and not board[square + 9] is None:
                if board[square + 9].color == "b":
                    legal_squares.add(square + 9)
            promote = (square + 8) // 8 == 7
        if piece_color == "b":
            if board[square - 8] is None:
                legal_squares.add(square - 8)
            if square in range(48, 56) and board[square - 16] is None and legal_squares:
                legal_squares.add(square - 16)
            if square % 8 and not board[square - 9] is None:
                if board[square - 9].color == "w":
                    legal_squares.add(square - 9)
            if (square - 7) % 8 and not board[square - 7] is None:
                if board[square - 7].color == "w":
                    legal_squares.add(square - 7)
            promote = (square - 8) // 8 == 0
        return legal_squares, promote
    if piece_type in "nk":
        moves = LEGAL_MOVES[piece_type]
        for move in moves:
            new_square = square + (8 * move[1]) + move[0]
            if new_square in range(64) and (new_square // 8) - (square // 8) == move[1]:
                if board[new_square] is None:
                    legal_squares.add(new_square)
                elif board[new_square].color != piece_color:
                    legal_squares.add(new_square)
        return legal_squares
    if piece_type in "brq":
        directions = LEGAL_MOVES[piece_type]
        for direction in directions:
            for move in direction:
                new_square = square + (8 * move[1]) + move[0]
                if new_square in range(64) and (new_square // 8) - (square // 8) == move[1]:
                    if board[new_square] is None:
                        legal_squares.add(new_square)
                    elif board[new_square].color != piece_color:
                        legal_squares.add(new_square)
                        break
                    else:
                        break
                else:
                    break
        return legal_squares
    
def king_in_danger(king_color, board):
    controlled_squares = set()
    for square in board:
        if not square is None:
            if square.color != king_color and square.piece != "p":
                controlled_squares |= get_legal_moves(square.square, board)
            elif square.color != king_color:
                controlled_squares |= {(square.square + (7 if king_color == "b" else -9)) if square.square % 8 else None, (square.square + (9 if king_color == "b" else -7)) if (square.square - 7) % 8 else None}
                if None in controlled_squares:
                    controlled_squares.remove(None)
            if square.piece == "k" and square.color == king_color:
                king_location = square.square
    return king_location in controlled_squares

def side_has_legal_moves(color, arg_board, double_advance_pawn):
    own_pieces = []
    for piece in arg_board:
        if not piece is None:
            if piece.color == color:
                own_pieces.append(piece)
    for piece in own_pieces:
        if piece.piece == "p":
            squares = get_legal_moves(piece.square, arg_board)[0]

            if color == "w" and not double_advance_pawn is None:
                if piece.square == 33 + double_advance_pawn:
                    squares.add((piece.square + 7,))
                elif piece.square == 31 + double_advance_pawn:
                    squares.add((piece.square + 9,))
            if color == "b" and not double_advance_pawn is None:
                if piece.square == 25 + double_advance_pawn:
                    squares.add((piece.square - 9,))
                elif piece.square == 23 + double_advance_pawn:
                    squares.add((piece.square - 7,))

        else:
            squares = get_legal_moves(piece.square, arg_board)
        for square in squares:
            board = list(arg_board)
            if isinstance(square, tuple):
                board[square[0]] = Piece(color, piece.piece, square[0])
                board[piece.square] = None
                board[square[0] - (8 if color == "w" else -8)] = None
            else:
                board[square] = Piece(color, piece.piece, square)
                board[piece.square] = None
            if not king_in_danger(color, board):
                return True

def main():
    board = list(START_BOARD)
    clicking = [False, False]
    move = "w"
    clicked_square = 24
    squares = set()
    removed_squares = set()
    first_click = False
    second_click = False
    checkmate = False
    stalemate = False
    double_advance_pawn = {"w": None, "b": None}
    castling_rights = {"w": {"k": True, "q": True}, "b": {"k": True, "q": True}}
    en_passant = False, None
    castling_available = [False, False]
    in_check = False
    threefold = False
    state = (tuple(x if x is None else x.color + x.piece + str(x.square) for x in board), move, (castling_rights["w"]["k"], castling_rights["w"]["q"], castling_rights["b"]["k"], castling_rights["b"]["q"]), None)
    states_seen = {state: 1}
    capture = False
    move_list = []
    _50_move_list = []
    _50_move = False
    insufficient_material = False
    castled = False
    size_length = {2: 25, 3: 25, 4: 25, 5: 22, 6: 19, 7: 16}
    announcement = []
    rank_file_letters = ("abcdefgh12345678", [((x * 90) + 15, 720) for x in range(8)] + [(2, 705 - (x * 90)) for x in range(8)])
    rank_file_letters = {Text(rank_file_letters[0][idx], rank_file_letters[1][idx], 15, "bl") for idx in range(16)}
    promotion_pieces = tuple({Piece(x, "q", None, (765, 650)), Piece(x, "r", None, (860, 650)), Piece(x, "b", None, (955, 650)), Piece(x, "n", None, (1050, 650))} for x in "wb")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clicking = clicking[1:] + [pygame.mouse.get_pressed()[0]]
        if clicking == [False, True] and not threefold and not _50_move and not insufficient_material:
            previous_clicked_square = clicked_square
            clicked_square = pygame.mouse.get_pos()
            clicked_square = (clicked_square[0] // 90, (720 - clicked_square[1]) // 90)
            clicked_square = (clicked_square[1] * 8) + clicked_square[0]
            if not first_click:
                first_click = True
            elif clicked_square in squares:
                second_click = True
        if not second_click and not board[clicked_square] is None:
            if board[clicked_square].color == move and clicked_square != previous_clicked_square:
                squares = get_legal_moves(clicked_square, board)
                if isinstance(squares, tuple):
                    if squares[1]:
                        promote = True
                    else:
                        promote = False
                    squares = squares[0]
                else:
                    promote = False
                if move == "w" and not double_advance_pawn["b"] is None:
                    if (clicked_square == 33 + double_advance_pawn["b"]) and board[clicked_square].piece == "p":
                        squares.add(clicked_square + 7)
                        en_passant = True, 7
                    else:
                        en_passant = False, None
                    if (clicked_square == 31 + double_advance_pawn["b"]) and board[clicked_square].piece == "p":
                        squares.add(clicked_square + 9)
                        en_passant = True, 9
                elif move == "b" and not double_advance_pawn["w"] is None:
                    if (clicked_square == 25 + double_advance_pawn["w"]) and board[clicked_square].piece == "p":
                        squares.add(clicked_square - 9)
                        en_passant = True, -9
                    else:
                        en_passant = False, None
                    if (clicked_square == 23 + double_advance_pawn["w"]) and board[clicked_square].piece == "p":
                        squares.add(clicked_square - 7)
                        en_passant = True, -7
                else:
                    en_passant = False, None
                if en_passant[0]:
                    removed_squares = set()
                    for square in squares:
                        temp_board = list(board)
                        if square - clicked_square == en_passant[1]:
                            temp_board[square] = temp_board[clicked_square]
                            temp_board[clicked_square] = None
                            temp_board[square - (8 if move == "w" else -8)] = None
                            if king_in_danger(move, temp_board):
                                removed_squares.add(square)
                        else:
                            temp_board[square] = Piece(move, "p", square)
                            temp_board[clicked_square] = None
                            if king_in_danger(move, temp_board):
                                removed_squares.add(square)
                else:
                    removed_squares = set()
                    for square in squares:
                        temp_board = list(board)
                        temp_board[square] = Piece(move, temp_board[clicked_square].piece, square)
                        temp_board[clicked_square] = None
                        if king_in_danger(move, temp_board):
                            removed_squares.add(square)
                for square in removed_squares:
                    squares.remove(square)
                if move == "w" and board[clicked_square].piece == "k":
                    if board[5] is None and board[6] is None and castling_rights["w"]["k"]:
                        if not in_check and not king_in_danger("w", board[:4] + [None, Piece("w", "r", 5), Piece("w", "k", 6), None] + board[8:]) and not king_in_danger("w", board[:4] + [None, Piece("w", "k", 5)] + board[6:]):
                            castling_available[0] = True
                            squares.add(6)
                        else:
                            removed_squares.add(6)
                            castling_available[0] = False
                    else:
                        castling_available[0] = False
                    if board[1] is None and board[2] is None and board[3] is None and castling_rights["w"]["q"]:
                        if not in_check and not king_in_danger("w", [None, None, Piece("w", "k", 2), Piece("w", "r", 3), None] + board[5:]) and not king_in_danger("w", board[:3] + [Piece("w", "k", 3), None] + board[5:]):
                            castling_available[1] = True
                            squares.add(2)
                        else:
                            removed_squares.add(2)
                            castling_available[1] = False
                    else:
                        castling_available[1] = False
                if move == "b" and board[clicked_square].piece == "k":
                    if board[61] is None and board[62] is None and castling_rights["b"]["k"]:
                        if not in_check and not king_in_danger("b", board[:60] + [None, Piece("b", "r", 61), Piece("b", "k", 62), None]) and not king_in_danger("b", board[:60] + [None, Piece("b", "k", 61)] + board[62:]):
                            castling_available[0] = True
                            squares.add(62)
                        else:
                            removed_squares.add(62)
                            castling_available[0] = False
                    else:
                        castling_available[0] = False
                    if board[57] is None and board[58] is None and board[59] is None and castling_rights["b"]["q"]:
                        if not in_check and not king_in_danger("b", board[:56] + [None, None, Piece("b", "k", 58), Piece("b", "r", 59), None] + board[61:]) and not king_in_danger("b", board[:59] + [Piece("b", "k", 59), None] + board[61:]):
                            castling_available[1] = True
                            squares.add(58)
                        else:
                            removed_squares.add(58)
                            castling_available[1] = False
                    else:
                        castling_available[1] = False
            elif clicked_square == previous_clicked_square or board[clicked_square].color != move:
                squares = set()
                removed_squares = set()
                clicked_square = board.index(None)
        elif board[clicked_square] is None and not second_click:
            squares = set()
            removed_squares = set()
            clicked_square = board.index(None)
        if second_click:
            if "check." in (announcement + ["x"])[0]:
                announcement = []
            temp_board = list(board)
            if board[previous_clicked_square].piece == "p":
                if (move == "w" and clicked_square - previous_clicked_square == 16) or (move == "b" and previous_clicked_square - clicked_square == 16):
                    double_advance_pawn[move] = clicked_square % 8
                else:
                    double_advance_pawn[move] = None
            else:
                double_advance_pawn[move] = None
            if board[clicked_square] is None:
                capture = False
            else:
                capture = True
                if board[clicked_square].piece == "r":
                    castling_rights["w" if move == "b" else "b"]["k" if clicked_square % 8 else "q"] = False
            if promote:
                announcement = ["Select promotion piece."]
                done = False
                while not done:
                    mouse_pos = pygame.mouse.get_pos()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    clicking = clicking[1:] + [pygame.mouse.get_pressed()[0]]
                    DISPLAY.fill((127,) * 3)
                    DISPLAY.blit(BOARDIMG, BOARDRECT)
                    for fidx, move_pair in enumerate(move_list[-15:]):
                        Text(str((fidx + 1) if len(move_list) <= 15 else (len(move_list) + fidx - 14)) + ".", (800, 50 + (30 * fidx)), 25, None).draw()
                        for idx, _move in enumerate(move_pair):
                            Text(_move, (890 + (40 * idx), (50 + (30 * fidx))), 25 if idx else size_length[len(_move)], bool(idx)).draw()
                    for square in board:
                        if not square is None and square.square not in {clicked_square, previous_clicked_square}:
                            square.draw()
                    MoveIndicator(clicked_square, True).draw()
                    for letter in rank_file_letters:
                        letter.draw()
                    for idx, line in enumerate(announcement):
                        Text(line, (910, 540 + (35 * idx)), 30, None).draw()
                    for piece in promotion_pieces["wb".index(move)]:
                        piece.draw()
                        if piece.rect.collidepoint(*mouse_pos) and clicking[1]:
                            x = piece.piece
                            done = True
                    pygame.display.update()
                    FPS.tick(30)

                board[clicked_square] = Piece(move, x, clicked_square)
                del x
                announcement = []
            else:
                if len(_50_move_list) == 100:
                    _50_move_list = _50_move_list[1:]
                _50_move_list.append(capture or board[previous_clicked_square].piece == "p")
                if not any(_50_move_list) and len(_50_move_list) == 100:
                    _50_move = True
                    announcement = ["Draw by 50", "move rule!"]
                board[clicked_square] = Piece(board[previous_clicked_square].color, board[previous_clicked_square].piece, clicked_square)
                if en_passant[0] and clicked_square - previous_clicked_square == en_passant[1]:
                    board[clicked_square - (8 if move == "w" else -8)] = None
                    en_passant = False, None
                    capture = True
                if castling_available[0] and board[previous_clicked_square].piece == "k" and move == "w" and clicked_square == 6:
                    board[5] = Piece("w", "r", 5)
                    board[7] = None
                    castling_rights["w"] = {"k": False, "q": False}
                    castled = True
                if castling_available[1] and board[previous_clicked_square].piece == "k" and move == "w" and clicked_square == 2:
                    board[3] = Piece("w", "r", 3)
                    board[0] = None
                    castling_rights["w"] = {"k": False, "q": False}
                    castled = True
                if castling_available[0] and board[previous_clicked_square].piece == "k" and move == "b" and clicked_square == 62:
                    board[61] = Piece("b", "r", 61)
                    board[63] = None
                    castling_rights["b"] = {"k": False, "q": False}
                    castled = True
                if castling_available[1] and board[previous_clicked_square].piece == "k" and move == "b" and clicked_square == 58:
                    board[59] = Piece("b", "r", 59)
                    board[56] = None
                    castling_rights["b"] = {"k": False, "q": False}
                    castled = True
                if board[previous_clicked_square].piece == "k" and (castling_rights[move]["k"] or castling_rights[move]["q"]):
                    castling_rights[move] = {"k": False, "q": False}
                if board[previous_clicked_square].piece == "r":
                    if (not previous_clicked_square % 8) and castling_rights[move]["q"]:
                        castling_rights[move]["q"] = False
                    if (not (previous_clicked_square - 7) % 8) and castling_rights[move]["k"]:
                        castling_rights[move]["k"] = False
            board[previous_clicked_square] = None
            first_click = False
            second_click = False
            move = "w" if move == "b" else "b"
            in_check = king_in_danger(move, board)
            x = not side_has_legal_moves(move, board, double_advance_pawn["w" if move == "b" else "b"])
            checkmate = x and in_check
            stalemate = x and not in_check
            del x
            if board[clicked_square].piece == "p" or promote:
                if capture:
                    move_played = FILES[previous_clicked_square % 8] + "x" + FILES[clicked_square % 8] + str((clicked_square // 8) + 1)
                else:
                    move_played = FILES[clicked_square % 8] + str((clicked_square // 8) + 1)
                if promote:
                    move_played = move_played + f"={board[clicked_square].piece.upper()}"
            elif board[clicked_square].piece == "k" and not castled:
                move_played = "K" + FILES[clicked_square % 8] + str((clicked_square // 8) + 1)
                if capture:
                    move_played = "Kx" + move_played[1:]
            elif castled:
                move_played = "O-O" + ("-O" if (clicked_square - 6) % 8 else "")
                castled = False
            else:
                move_played = board[clicked_square].piece.upper() + FILES[clicked_square % 8] + str((clicked_square // 8) + 1)
                color_piece = board[clicked_square].color_piece
                same_pieces = {}
                for square in temp_board:
                    if not square is None:
                        if square.square != previous_clicked_square and square.color_piece == color_piece:
                            same_pieces[square] = get_legal_moves(square.square, temp_board)
                if same_pieces:
                    overlap_pieces = set()
                    for piece, _squares in same_pieces.items():
                        if clicked_square in _squares:
                            overlap_pieces.add(piece)
                    if overlap_pieces:
                        file_ok = True
                        rank_ok = True
                        for piece in overlap_pieces:
                            if piece.square % 8 == previous_clicked_square % 8:
                                file_ok = False
                            if piece.square // 8 == previous_clicked_square // 8:
                                rank_ok = False
                        if file_ok:
                            move_played = move_played[0] + FILES[previous_clicked_square % 8] + move_played[1:]
                        elif rank_ok:
                            move_played = move_played[0] + str((previous_clicked_square // 8) + 1) + move_played[1:]
                        else:
                            move_played = move_played[0] + FILES[previous_clicked_square % 8] + str((previous_clicked_square // 8) + 1) + move_played[1:]
                if capture:
                    move_played = move_played[:-2] + "x" + move_played[-2:] 
            if checkmate:
                move_played = move_played + "#"
            elif in_check:
                move_played = move_played + "+"
            try:
                move_list[-1]
            except IndexError:
                move_list.append([])
            if len(move_list[-1]) == 2:
                move_list[-1] = tuple(move_list[-1])
                move_list.append([])
            move_list[-1].append(move_played)
            if checkmate:
                announcement = ["Checkmate,", f"{'white' if move == 'b' else 'black'} wins!"]
            elif stalemate:
                announcement = ["Draw by stalemate!"]
            else:
                if move == "w" and not double_advance_pawn["b"] is None:
                    if ((board[33 + double_advance_pawn["b"]].color_piece == "wp") if double_advance_pawn["b"] % 8 != 7 and not board[33 + double_advance_pawn["b"]] is None else False) or ((board[31 + double_advance_pawn["b"]].color_piece == "wp") if double_advance_pawn["b"] % 8 and not board[31 + double_advance_pawn["b"]] is None else False):
                       en_passant_state = 32 + double_advance_pawn["b"]
                    else:
                        en_passant_state = None
                elif move == "b" and not double_advance_pawn["w"] is None:
                    if ((board[25 + double_advance_pawn["w"]].color_piece == "bp") if double_advance_pawn["w"] % 8 != 7 and not board[25 + double_advance_pawn["w"]] is None else False) or ((board[23 + double_advance_pawn["w"]].color_piece == "bp") if double_advance_pawn["w"] % 8 and not board[23 + double_advance_pawn["w"]] is None else False):
                        en_passant_state = 24 + double_advance_pawn["w"]
                    else:
                        en_passant_state = None
                else:
                    en_passant_state = None
                state = (tuple(x if x is None else x.color + x.piece + str(x.square) for x in board), move, (castling_rights["w"]["k"], castling_rights["w"]["q"], castling_rights["b"]["k"], castling_rights["b"]["q"]), en_passant_state)
                if state in states_seen:
                    states_seen[state] = states_seen[state] + 1
                    if states_seen[state] == 3:
                        announcement = ["Draw by threefold", "repetition!"]
                        threefold = True
                else:
                    states_seen[state] = 1
                all_pieces = []
                for square in board:
                    if not square is None:
                        if square.piece == "k":
                            all_pieces.insert(0, square)
                        else:
                            all_pieces.append(square)
                if len(all_pieces) == 2 or (len(all_pieces) == 3 and all_pieces[-1].piece in {"b", "n"}):
                    insufficient_material = True
                    announcement = ["Draw by insufficient", "material!"]
                if not announcement and in_check:
                    announcement = [f"{'White' if move == 'w' else 'Black'} is in check."]
        DISPLAY.fill((127,) * 3)
        DISPLAY.blit(BOARDIMG, BOARDRECT)
        for fidx, move_pair in enumerate(move_list[-15:]):
            Text(str((fidx + 1) if len(move_list) <= 15 else (len(move_list) + fidx - 14)) + ".", (800, 50 + (30 * fidx)), 25, None).draw()
            for idx, _move in enumerate(move_pair):
                Text(_move, (890 + (40 * idx), (50 + (30 * fidx))), 25 if idx else size_length[len(_move)], bool(idx)).draw()
        for square in board:
            if not square is None:
                square.draw()
        if clicked_square not in squares:
            for square in squares:
                MoveIndicator(square, False).draw()
            for square in removed_squares:
                MoveIndicator(square, False, "il").draw()
        MoveIndicator(clicked_square, True).draw() if (not board[clicked_square] is None) and clicked_square not in squares else None
        for letter in rank_file_letters:
            letter.draw()
        for idx, line in enumerate(announcement):
            Text(line, (910, 540 + (35 * idx)), 30, None).draw()
        pygame.display.update()
        FPS.tick(30)


main()