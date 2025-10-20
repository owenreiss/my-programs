import os
import pickle
import pygame
import sys

pygame.init()
os.chdir("/Users/owenreiss/Desktop/Coding/python/tictactoe")
WINS = {(0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 4, 8), (2, 4, 6)}

tablebase = {}
DISPLAY = pygame.display.set_mode((900, 600))
BOARDIMG = pygame.image.load("board.png")
BOARDRCT = BOARDIMG.get_rect()
BOARDRCT.bottomleft = (0, 600)
FPS = pygame.time.Clock()

class Piece(pygame.sprite.Sprite):
    def __init__(self, piece_type, cell):
        self.piece_type = piece_type
        self.cell = cell
        self.image = pygame.image.load(piece_type + ".png")
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = ((24, 225, 424)[cell % 3], (171, 380, 584)[cell // 3])

    def __repr__(self):
        return f'Piece("{self.piece_type}", {self.cell})'

    def draw(self):
        DISPLAY.blit(self.image, self.rect)

class Text(pygame.sprite.Sprite):
    def __init__(self, text, coordinates, color=(127,)*3, size=30):
        font = pygame.font.Font("freesansbold.ttf", size)
        self.size = size
        self.coordinates = coordinates
        self.color = color
        self.text = text
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = coordinates

    def __repr__(self):
        return f'Text("{self.text}", {self.coordinates}, "{self.color}", {self.size})'
    
    def draw(self):
        DISPLAY.blit(self.image, self.rect)

def alt(arg):
    return "o" if arg == "x" else "x"
    
def best_move(board, want_all=False, make_tablebase=False):
    empty_cells = {idx for idx, x in enumerate(board) if x == "n"}
    turn = "ox"[board.count("n") % 2]
    win, draw, loss = {}, [], {}
    for cell in empty_cells:
        if board == "n" * 9:
            print(cell, "main")
        if board.count("n") == 8:
            print(cell, "alt")
        if board.count("n") == 7:
            print(cell, "x")
        counter = 0
        my_move = cell
        new_board = board
        while True:
            done = False
            new_board = new_board[:my_move] + turn + new_board[my_move + 1:]
            counter += 1
            for _win in WINS:
                if all(new_board[x] == turn for x in _win):
                    win[cell] = counter
                    done = True
                    break
                if all(new_board[x] == alt(turn) for x in _win):
                    loss[cell] = counter
                    done = True
                    break
            if not new_board.count("n") and not done:
                draw.append(cell)
                done = True
            if done:
                break
            done = False
            opp_cell = best_move(new_board, False, make_tablebase)
            new_board = new_board[:opp_cell] + alt(turn) + new_board[opp_cell + 1:]
            counter += 1
            for _win in WINS:
                if all(new_board[x] == alt(turn) for x in _win):
                    loss[cell] = counter
                    done = True
                    break
                if all(new_board[x] == turn for x in _win):
                    win[cell] = counter
                    done = True
                    break
            if not new_board.count("n") and not done:
                draw.append(cell)
                done = True
            if done:
                break
            my_move = best_move(new_board, False, make_tablebase)
    if make_tablebase:
        tablebase[board] = win, draw, loss
    if want_all:
        return win, draw, loss
    else:
        win = [x[1] for x in sorted((k, v) for v, k in win.items())]
        loss = [x[1] for x in reversed(sorted((k, v) for v, k in loss.items()))]
        return (win + draw + loss)[0]

def make_tablebase():
    best_move("n" * 9, True, True)
    with open("pickled_tablebase", "wb") as file:
        pickle.dump(tablebase, file)
    print("Done")

def main():
    with open("pickled_tablebase", "rb") as file:
        main_tablebase = pickle.load(file)
    turn = "x"
    board = "n" * 9
    remaining_pieces = {Piece(piece, x) for x in range(9) for piece in "xo"}
    query_mode = True
    queries = {Text("On which turns should the tablebase be shown?", (450, 250), size=30): None, Text("X", (215, 400), size=50): (True, False), Text("O", (305, 400), size=50): (False, True), Text("Both", (430, 400), size=50): (True, True), Text("Neither", (615, 400), size=50): (False, False)}
    used_cells = set()
    drawn_pieces = set()
    clicking = [False, False]
    winner = False
    mode = (False, False)
    status = ({}, list(range(9)), {})
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        DISPLAY.fill((255,) * 3)
        if not query_mode:
            DISPLAY.blit(BOARDIMG, BOARDRCT)
        else:
            for text in queries:
                text.draw()
                if text.size == 50 and clicking == [False, True] and text.rect.collidepoint(*pygame.mouse.get_pos()):
                    mode = queries[text]
                    query_mode = False
        for piece in drawn_pieces:
            piece.draw()
        clicking = clicking[1:]
        clicking.append(pygame.mouse.get_pressed()[0])
        if clicking == [False, True] and not winner and not query_mode:
            for piece in remaining_pieces:
                if piece.rect.collidepoint(*pygame.mouse.get_pos()):
                    drawn_pieces.add(Piece(turn, piece.cell))
                    used_cells.add(piece.cell)
                    board = board[:piece.cell] + turn + board[piece.cell + 1:]
                    remaining_pieces = {x for x in remaining_pieces if x.cell not in used_cells}
                    turn = alt(turn)
                    for win in WINS:
                        if all(board[x] == "x" for x in win):
                            winner = "x"
                        if all(board[x] == "o" for x in win):
                            winner = "o"
                    if not winner and not board.count("n"):
                        winner = "d"
                    if not winner:
                        status = main_tablebase[board]
                    break
        if winner and winner != "d":
            Text(f"{winner.upper()} is the winner!", (750, 300)).draw()
        elif winner:
            Text("It's a draw!", (750, 300)).draw()
        elif not query_mode and mode["xo".index(turn)]:
            for idx, condition in enumerate(status):
                for cell in condition:
                    Text(str(board.count("n") if idx == 1 else condition[cell]), ((100, 300, 500)[cell % 3], (100, 300, 500)[cell // 3]), ((0, 255, 0), (127,) * 3, (255, 0, 0))[idx]).draw()
        pygame.display.update()
        FPS.tick(30)

main()