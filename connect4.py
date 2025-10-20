import pygame
import sys
import os

os.chdir("/Users/owenreiss/Desktop/Coding/python/Connect 4")
pygame.init()

class Board(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Board.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)

    def draw(self):
        DISPLAY.blit(self.image, self.rect)

class CircleOrX(Board):
    def __init__(self, color, cell):
        self.color = color
        self.cell = cell
        self.image = pygame.image.load(color + ".png")
        self.rect = self.image.get_rect()
        div, mod = divmod(cell, 7)
        if color == "X":
            self.rect.center = WIDTHS[mod] + 29, HEIGHTS[div] + 29
        else:
            self.rect.topleft = WIDTHS[mod], HEIGHTS[div]

BOARD = Board()
DISPLAY = pygame.display.set_mode((639, 553))
WIDTHS = (29, 116, 203, 290, 377, 464, 552)
HEIGHTS = (465, 378, 291, 204, 117, 30)
WINS = {(28, 29, 30, 31), (29, 30, 31, 32), (10, 16, 22, 28), (0, 8, 16, 24), (24, 25, 26, 27), (5, 11, 17, 23), (3, 10, 17, 24), (9, 10, 11, 12), (1, 2, 3, 4), (16, 24, 32, 40), (19, 26, 33, 40), (14, 21, 28, 35), (13, 20, 27, 34), (18, 25, 32, 39), (8, 16, 24, 32), (4, 11, 18, 25), (8, 15, 22, 29), (3, 4, 5, 6), (8, 9, 10, 11), (37, 38, 39, 40), (22, 23, 24, 25), (18, 24, 30, 36), (19, 25, 31, 37), (17, 25, 33, 41), (0, 7, 14, 21), (3, 9, 15, 21), (12, 18, 24, 30), (7, 8, 9, 10), (17, 18, 19, 20), (13, 19, 25, 31), (2, 9, 16, 23), (2, 3, 4, 5), (17, 24, 31, 38), (9, 17, 25, 33), (12, 19, 26, 33), (1, 8, 15, 22), (1, 9, 17, 25), (7, 14, 21, 28), (11, 18, 25, 32), (14, 15, 16, 17), (4, 10, 16, 22), (10, 11, 12, 13), (31, 32, 33, 34), (35, 36, 37, 38), (0, 1, 2, 3), (36, 37, 38, 39), (9, 16, 23, 30), (30, 31, 32, 33), (3, 11, 19, 27), (20, 26, 32, 38), (6, 13, 20, 27), (15, 16, 17, 18), (21, 22, 23, 24), (6, 12, 18, 24), (11, 17, 23, 29), (16, 17, 18, 19), (17, 23, 29, 35), (7, 15, 23, 31), (10, 18, 26, 34), (20, 27, 34, 41), (16, 23, 30, 37), (2, 10, 18, 26), (15, 22, 29, 36), (10, 17, 24, 31), (5, 12, 19, 26), (23, 24, 25, 26), (14, 22, 30, 38), (15, 23, 31, 39), (38, 39, 40, 41)}
FPS = pygame.time.Clock()

# counter = 1
# while True:
#     x = tuple(a + counter for a in (0, 7, 14, 21))
#     if 42 in x:
#         break
#     WINS.add(x)
#     counter += 1

# counter = 0
# while True:
#     x = tuple(a + counter for a in range(4))
#     if 42 in x:
#         break
#     if any(a // 7 != x[0] // 7 for a in x):
#         counter += 1
#         continue
#     WINS.add(x)
#     counter += 1

# for a in range(3):
#     for b in range(4):
#         addition = (a * 7) + b
#         WINS.add(tuple(y + addition for y in (0, 8, 16, 24)))
#         WINS.add(tuple(y + addition for y in (3, 9, 15, 21)))

def transparent_blit(source, opacity):
    x, y = source.rect.topleft
    temp = pygame.Surface((source.rect.w, source.rect.h)).convert()
    temp.blit(DISPLAY, (-x, -y))
    temp.blit(source.image, (0, 0))
    temp.set_alpha(opacity)        
    DISPLAY.blit(temp, source.rect)

def alt(clr):
    return "Y" if clr == "R" else "R"

def main():
    clicking = [False, False]
    state = [None] * 42
    visible_state = []
    heights = [0, 0, 0, 0, 0, 0, 0]
    turn = "R"
    done = False
    win_x = []
    while True:
        BOARD.draw()
        for img in visible_state + win_x:
            img.draw()
        del clicking[0]
        clicking.append(pygame.mouse.get_pressed()[0])
        pos = pygame.mouse.get_pos()
        if all(pos) and not done:
            for idx, w in enumerate(WIDTHS):
                if w <= pos[0] <= w + 59 and heights[idx] != 6:
                    location = idx + (heights[idx] * 7)
                    if clicking == [False, True]:
                        visible_state.append(CircleOrX(turn, location))
                        state[location] = turn
                        heights[idx] = heights[idx] + 1
                        for win in WINS:
                            if all(state[x] == turn for x in win):
                                done = True
                                win_x = [CircleOrX("X", x) for x in win]
                                print(f"{'Red' if turn == 'R' else 'Yellow'} wins!")
                                break
                        else: # FOR ELSE YAY
                            turn = alt(turn)
                            if all(a == 6 for a in heights):
                                done = True
                                print("Draw!")
                    else:
                        transparent_blit(CircleOrX(turn, location), 127)
                    break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
        FPS.tick(30)

if __name__ == "__main__":
    main()