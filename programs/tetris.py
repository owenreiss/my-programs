# visual tetris game

import pygam
import sys
import random
import os
import copy

pygame.init()
os.chdir("/Users/owenreiss/Desktop/Coding/python/tetris_pictures")

class Pixel(pygame.sprite.Sprite):
    def __init__(self, color, cell):
        super().__init__()
        self.color = color
        self.cell = cell
        self.image = pygame.image.load(f"{'a' if GREY_BLOCKS else color}.png")
        self.image = pygame.transform.scale(self.image, (PIXEL_LENGTH,) * 2)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = ((cell % 10) * PIXEL_LENGTH, ((HEIGHT + 3) * PIXEL_LENGTH) - (cell // 10) * PIXEL_LENGTH)

    def __repr__(self):
        return f"Pixel with color {self.color} in cell {self.cell}"

    def draw(self):
        DISPLAY.blit(self.image, self.rect)

class Text(pygame.sprite.Sprite):
    def __init__(self, text, coordinates):
        super().__init__()
        font = pygame.font.Font("freesansbold.ttf", FONT_SIZE)
        self.image = font.render(text, True, (255, 0, 0))
        self.text = text
        self.rect = self.image.get_rect()
        self.rect.center = coordinates

    def __repr__(self):
        return f'Text object saying "{self.text}"'

    def draw(self):
        DISPLAY.blit(self.image, self.rect)

ALL_PIXELS = {}
FONT_SIZE = 58
COLORS = "abgiopry" #bgiopry
SHAPE = {"b": {1, 2, 5, 6}, "g": {2, 6, 10, 14}, "i": {0, 1, 5, 6}, "o": {2, 6, 9, 10}, "p": {1, 5, 9, 10}, "r": {2, 5, 6, 7}, "y": {2, 3, 5, 6}}
ROTATION = {
    "b": {x: ({y: 0 for y in range(4)}, (0, 0)) for x in range(4)},
    "g": {0: ({0: 8, 1: 0, 2: -11, 3: -19}, (2, 1)), 1: ({0: 21, 1: 0, 2: 9, 3: -12}, (0, 0)), 2: ({0: 19, 1: 11, 2: 0, 3: -8}, (1, 2)), 3: ({0: 12, 1: -9, 2: 0, 3: -21}, (0, 0))},
    "i": {0: ({0: 0, 1: 0, 2: 2, 3: -20}, (0, 0)), 1: ({0: 0, 1: 0, 2: -2, 3: -20}, (1, 0)), 2: ({0: 20, 1: -2, 2: 0, 3: 0}, (0, 0)), 3: ({0: 20, 1: 2, 2: 0, 3:0}, (0, 1))},
    "o": {0: ({0: 20, 1: 9, 2: 0, 3: -9}, (0, 1)), 1: ({0: -9, 1: 0, 2: 9, 3: 2}, (0, 0)), 2: ({0: 9, 1: 0, 2: -9, 3: -20}, (1, 0)), 3: ({0: -2, 1: -9, 2: 0, 3: 9}, (0, 0))},
    "p": {0: ({0: -1, 1: 10, 2: 0, 3: -11}, (1, 0)), 1: ({0: 1, 1: 10, 2: 0, 3: 9}, (0, 0)), 2: ({0: 11, 1: 0, 2: -10, 3: 1}, (0, 1)), 3: ({0: -9, 1: 0, 2: -10, 3: -1}, (0, 0))},
    "r": {0: ({0: -9, 1: 0, 2: 0, 3: 0}, (0, 0)), 1: ({0: 0, 1: 0, 2: 0, 3: -11}, (1, 0)), 2: ({0: 0, 1: 0, 2: 0, 3: 9}, (0, 0)), 3: ({0: 11, 1: 0, 2: 0, 3: 0}, (0, 1))},
    "y": {0: ({0: 2, 1: 0, 2: 0, 3: -20}, (0, 0)), 1: ({0: -2, 1: 0, 2: 0, 3: -20}, (1, 0)), 2: ({0: 20, 1: 0, 2: 0, 3: -2}, (0, 0)), 3: ({0: 20, 1: 0, 2: 0, 3: 2}, (0, 1))}
    }
HEIGHT = 15
GREY_BLOCKS = False
TOP_SQUARE = (HEIGHT * 10 + 53, HEIGHT * 10 + 54, HEIGHT * 10 + 55, HEIGHT * 10 + 56, HEIGHT * 10 + 43, HEIGHT * 10 + 44, HEIGHT * 10 + 45, HEIGHT * 10 + 46, HEIGHT * 10 + 33, HEIGHT * 10 + 34, HEIGHT * 10 + 35, HEIGHT * 10 + 36, HEIGHT * 10 + 23, HEIGHT * 10 + 24, HEIGHT * 10 + 25, HEIGHT * 10 + 26)
FRAME_RATE = 120
PIXEL_LENGTH = 40
DROP_DELAY = FRAME_RATE // 3
MOVEMENT_DELAY = FRAME_RATE // 12
ROTATION_DELAY = (FRAME_RATE * 3) // 4
FUTURE_LENGTH = 0
if FUTURE_LENGTH:
    DISPLAY = pygame.display.set_mode((16 * PIXEL_LENGTH, (HEIGHT + 3) * PIXEL_LENGTH))
else:
    DISPLAY = pygame.display.set_mode((10 * PIXEL_LENGTH, (HEIGHT + 3) * PIXEL_LENGTH))
FPS = pygame.time.Clock()
for color in COLORS:
    for cell in range((HEIGHT + 7) * 10):
        ALL_PIXELS[(color, cell)] = Pixel(color, cell)
recording = []

def cells_after_tetris(cells):
    full_rows = []
    for x in range(0, HEIGHT * 10, 10):
        if all((not cell is None for cell in cells[x: x + 10])):
            full_rows.append(x // 10)
    new_cells = cells
    for row in reversed(full_rows):
        for x in range(row, HEIGHT + 1):
            new_cells[x * 10:(x * 10) + 10] = new_cells[(x * 10) + 10: (x * 10) + 20]
    return new_cells

def cells_after_rotation(cells, color, rotation):
    sorted_cells = sorted(cells)
    info = ROTATION[color][rotation][0]
    return [x + info[idx] for idx, x in enumerate(sorted_cells)]

def legal_rotate(cells, active_cells, color, rotation):
    edge_space = ROTATION[color][rotation][1]
    last_digits = [int(str(cell)[-1]) for cell in active_cells]
    on_edge = any((digit - edge_space[0] < 0 or digit + edge_space[1] >= 10 for digit in last_digits))
    new_active_cells = cells_after_rotation(active_cells, color, rotation)
    inactive_cells = copy.deepcopy(cells)
    for cell in active_cells:
        inactive_cells[cell] = None
    return all((inactive_cells[cell] is None for cell in new_active_cells)) and not on_edge and all((cell >= 0 for cell in new_active_cells))

def main():
    frame = 1
    make_piece = True
    cells = [None] * (10 * (HEIGHT + 7))
    game_over = False
    rotation = 0
    game_over_text = Text("Game Over", (PIXEL_LENGTH * 5, ((HEIGHT + 3) * PIXEL_LENGTH) // 2))
    rotating = False
    none_pressed = True
    exit_drop = False
    while True:
        DISPLAY.fill((0,) * 3)
        pygame.draw.rect(DISPLAY, (255, 0, 0), pygame.Rect((0, (3 * PIXEL_LENGTH) - 1, (10 * PIXEL_LENGTH), 1)))
        if make_piece and not game_over:
            make_piece = False
            cells = cells_after_tetris(cells)
            rotation = 0
            if any((not cell is None for cell in cells[HEIGHT * 10:])):
                game_over = True
                active_cells = []
                for x in range(81, 89):
                    cells[x] = None
                for x in range(91, 99):
                    cells[x] = None
            else:
                color = random.choice(COLORS[1:])
                shape = SHAPE[color]
                active_cells = []
                for cell in shape:
                    cells[TOP_SQUARE[cell]] = color
                    active_cells.append(TOP_SQUARE[cell])
        for idx, cell in enumerate(cells):
            if not cell is None:
                ALL_PIXELS[(cell, idx)].draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # if event.type == pygame.KEYDOWN:
            #     keyframe = frame
            # if event.type == pygame.KEYUP:
            #     keystroke = False
            #     keyevents = []
        if frame != 1:
            none_pressed = not any(keys_pressed.values())
        keys_pressed = pygame.key.get_pressed()
        keys_pressed = {"W": keys_pressed[119], "A": keys_pressed[97], "S": keys_pressed[115], "D": keys_pressed[100], "X": keys_pressed[32]}
        if not keys_pressed["X"]:
            pressing_space = False
        if not keys_pressed["W"]:
            rotating = False
        if True in keys_pressed.values():
            if none_pressed:
                keyframe = frame
            if (frame - keyframe) % MOVEMENT_DELAY == 0:
                if keys_pressed["W"] and not rotating:
                    rotating = True
                    rotating_frame = frame
                if keys_pressed["W"] and (frame - rotating_frame > ROTATION_DELAY or frame == rotating_frame):
                    if legal_rotate(cells, active_cells, color, rotation):
                        for cell in active_cells:
                            cells[cell] = None
                        active_cells = cells_after_rotation(active_cells, color, rotation)
                        for cell in active_cells:
                            cells[cell] = color
                        rotation += 1
                        rotation %= 4
                if keys_pressed["A"]:
                    if all((str(x)[-1] != "0" for x in active_cells)) and all((cells[x - 1] is None or x - 1 in active_cells for x in active_cells)):
                        for cell in active_cells:
                            cells[cell] = None
                        active_cells = [x - 1 for x in active_cells]
                        for cell in active_cells:
                            cells[cell] = color
                if keys_pressed["S"]:
                    for cell in active_cells:
                        if (not cells[cell - 10] is None and cell - 10 not in active_cells) or cell < 10:
                            make_piece = True
                    if not make_piece:
                        for idx, cell in enumerate(active_cells):
                            cells[cell] = None
                            active_cells[idx] = active_cells[idx] - 10
                        for cell in active_cells:
                            if not cells[cell - 10] is None or cell < 10:
                                make_piece = True
                        for cell in active_cells:
                            cells[cell] = color
                if keys_pressed["D"]:
                    if all((str(x)[-1] != "9" for x in active_cells)) and all((cells[x + 1] is None or x + 1 in active_cells for x in active_cells)):
                        for cell in active_cells:
                            cells[cell] = None
                        active_cells = [x + 1 for x in active_cells]
                        for cell in active_cells:
                            cells[cell] = color
                if keys_pressed["X"] and not pressing_space:
                    pressing_space = True
                    while True:
                        for cell in active_cells:
                            if (not cells[cell - 10] is None and cell - 10 not in active_cells) or cell < 10:
                                exit_drop = True
                                break
                        if exit_drop:
                            exit_drop = False
                            break
                        for idx, cell in enumerate(active_cells):
                            cells[cell] = None
                            active_cells[idx] = active_cells[idx] - 10
                        for cell in active_cells:
                            cells[cell] = color
                    make_piece = True
        if frame % DROP_DELAY == 0 and not make_piece:
            for cell in active_cells:
                if (not cells[cell - 10] is None and cell - 10 not in active_cells) or cell < 10:
                    make_piece = True
            if not make_piece:
                for idx, cell in enumerate(active_cells):
                    cells[cell] = None
                    active_cells[idx] = active_cells[idx] - 10
                for cell in active_cells:
                    cells[cell] = color
        if game_over:
            game_over_text.draw()
        pygame.display.update()
        FPS.tick(FRAME_RATE)
        frame += 1

main()
