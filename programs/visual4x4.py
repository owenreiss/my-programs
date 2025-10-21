# visual inputting for my 4x4 rubik's cube solver

import _4x4_non_optimal as main4x4
import pygame
import sys
import os

os.chdir("/Users/owenreiss/Desktop/Coding/python/cube_images")
pygame.init()

class Square(pygame.sprite.Sprite):
    def __init__(self, color, idx):
        super().__init__()
        self.color = color
        self.idx = idx
        self.image = pygame.image.load(color + ".png")
        self.image = pygame.transform.scale(self.image, (46, 46))
        self.rect = self.image.get_rect()
        self.rect.topleft = tuple(COORDINATES[LOCATIONS[idx][x]] for x in range(2))

    def draw(self):
        DISPLAY.blit(self.image, self.rect)

class Text(pygame.sprite.Sprite):
    def __init__(self, text, coordinates, size=40, color=(0,)*3):
        super().__init__()
        font = pygame.font.Font("freesansbold.ttf", size)
        self.image = font.render(text, True, color)
        self.text = text
        self.size = size
        self.rect = self.image.get_rect()
        self.rect.center = coordinates

    def draw(self):
        DISPLAY.blit(self.image, self.rect)

DISPLAY_SIZE = (812, 608)
DISPLAY = pygame.display.set_mode(DISPLAY_SIZE)
FPS = pygame.time.Clock()
BASE_CUBE_IMG = pygame.image.load("4x4_img.png")
BASE_CUBE_IMG = pygame.transform.scale(BASE_CUBE_IMG, DISPLAY_SIZE)
BASE_CUBE_RECT = BASE_CUBE_IMG.get_rect()
BASE_CUBE_RECT.topleft = (0, 0)
CENTER_INDECES = ((41,), (37,), (38,), (42,), (9,), (5,), (6,), (10,), (73,), (69,), (70,), (74,), (85,), (86,), (89,), (25,), (21,), (22,), (26,), (57,), (53,), (54,), (58,))
WING_INDECES = ((14, 34), (13, 33), (8, 18), (4, 17), (1, 66), (2, 65), (7, 50), (11, 49), (40, 27), (36, 23), (39, 52), (43, 56), (71, 20), (75, 24), (72, 59), (68, 55), (81, 45), (82, 46), (88, 29), (84, 30), (93, 77), (92, 78), (87, 61), (90, 62))
CORNER_INDECES = ((12, 32, 19), (0, 16, 67), (3, 64, 51), (15, 48, 35), (80, 31, 44), (91, 79, 28), (94, 63, 76), (83, 47, 60))
COORDINATES = (2, 52, 102, 152, 206, 256, 306, 356, 410, 460, 510, 560, 614, 664, 714, 764)
LOCATIONS = ((4, 0), (0, 4), (4, 4), (8, 4), (12, 4), (4, 8))
temp = []
for loc in LOCATIONS:
    for idx in range(16):
        temp.append((loc[0] + (idx % 4), loc[1] + (idx // 4)))
del temp[89] # constant yellow square
LOCATIONS = tuple(temp)
COLORS = "WOGRBY"
KEYS = ((pygame.K_w, "W"), (pygame.K_o, "O"), (pygame.K_g, "G"), (pygame.K_r, "R"), (pygame.K_b, "B"), (pygame.K_y, "Y"))

def convert_str_to_state(str_input):
    state = [[], [], []]
    for fidx, tup in enumerate((CORNER_INDECES, WING_INDECES, CENTER_INDECES)):
        for idx in tup:
            state[fidx].append("".join(str_input[x] for x in idx))
    state[2].insert(12, "Y")
    return state

def main():
    clicks = [False, False]
    keydown = [False, False]
    state = ""
    squares = []
    backspace = False
    editing = True
    solved = False
    msg = None
    while True:
        del clicks[0]
        clicks.append(pygame.mouse.get_pressed()[0])
        DISPLAY.fill((128,) * 3)
        DISPLAY.blit(BASE_CUBE_IMG, BASE_CUBE_RECT)
        if not msg is None:
            msg.draw()
            if msg.text == "Check terminal" and not solved:
                main4x4.main(real_state)
                solved = True
        for idx, square in enumerate(squares):
            if isinstance(square, Square):
                square.draw()
            if editing and not backspace:
                if clicks == [False, True] and square.rect.collidepoint(*pygame.mouse.get_pos()):
                    backspace = True
                    backspace_idx = idx
                    state = state[:idx] + "N" + state[idx + 1:]
                    squares[idx] = None
        single_keydown = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                single_keydown = True
                keydown_event = event
        del keydown[0]
        keydown.append(single_keydown)
        if keydown == [False, True] and editing and (len(state) != 95 or backspace):
            if backspace:
                backspace = False
                for key_pygame, key_str in KEYS:
                    if keydown_event.key == key_pygame:
                        state = state[:backspace_idx] + key_str + state[backspace_idx + 1:]
                        squares[backspace_idx] = Square(key_str, backspace_idx)
                        break   
            else:
                for key_pygame, key_str in KEYS:
                    if keydown_event.key == key_pygame:
                        state += key_str
                        squares.append(Square(key_str, len(squares)))
                        break
                if keydown_event.key == pygame.K_BACKSPACE and len(state):
                    state = state[:-1]
                    del squares[-1]
        if keydown == [False, True] and editing and len(state) == 95 and not backspace:
            if keydown_event.key == pygame.K_RETURN:
                real_state = convert_str_to_state(state)
                real_state = main4x4.query_state(real_state, True)
                if isinstance(real_state, str):
                    msg = Text(real_state, (610, 102))
                else:
                    editing = False
                    solved = False
                    msg = Text("Check terminal", (610, 102))
                    msg.draw()
        pygame.display.update()
        FPS.tick(30)

main()
