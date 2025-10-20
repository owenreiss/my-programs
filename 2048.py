import pygame
import sys

from os import chdir
from random import randint, choice

pygame.init()
chdir("/Users/owenreiss/Desktop/Coding/python/2048")

class Sprite(pygame.sprite.Sprite):
    def __init__(self, power=None, location=-1):
        super().__init__()
        self.image = pygame.image.load("grid.png" if power is None else f"tile_{power}.png")
        if location != -1:
            self.image = pygame.transform.smoothscale(self.image, (105, 105))
        self.location = location
        self.rect = self.image.get_rect()
        if location == -1:
            self.rect.topleft = 0, 0
        else:
            self.rect.topleft = X[location % 4], Y[location // 4]

    def draw(self):
        DISPLAY.blit(self.image, self.rect)

class Text(pygame.sprite.Sprite):
    def __init__(self, text, coordinates):
        super().__init__()
        font = pygame.font.Font("freesansbold.ttf", 80)
        self.image = font.render(text, True, (255, 0, 0))
        self.text = text
        self.rect = self.image.get_rect()
        self.rect.center = coordinates

    def draw(self):
        DISPLAY.blit(self.image, self.rect)

DISPLAY = pygame.display.set_mode((499, 500))
FPS = pygame.time.Clock()
GRID = Sprite()
ROTATION_POSITIONS = tuple(i + j * 4 for i in reversed(range(4)) for j in range(4))
X = 14, 135, 257, 378
Y = 15, 137, 258, 379
JUST_CLICKED = [False, True]
GAME_OVER_TEXT = Text("Game over", (250, 250))

def get_sprites(grid):
    sprites = [] # list comp
    for index, val in enumerate(grid):
        if val is not None:
            sprites.append(Sprite(val, index))
    return sprites

def update():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
    FPS.tick(30)

def rotate_clockwise(grid):
    new_grid = [None] * 16
    for pos, val in zip(ROTATION_POSITIONS, grid):
        new_grid[pos] = val
    return new_grid

def shift_row_right(row):
    new_row = row.copy()
    for i, block in enumerate(new_row[2::-1]): # from [0, 1, 2, 3] gives [2, 1, 0]
        place_index = 2 - i
        while place_index < 3 and new_row[place_index + 1] is None:
            place_index += 1
        new_row[2 - i] = None
        new_row[place_index] = block
    return new_row

def merge_row(row):
    "must call after shift_right"
    new_row = row.copy()
    merges = [i for i in range(3) if row[i] == row[i + 1] is not None]
    if len(merges) > 1:
        del merges[len(merges) % 2]
    for merge in merges:
        new_row[merge] = None
        new_row[merge + 1] += 1
    return new_row

def move_row_right(row):
    return shift_row_right(merge_row(shift_row_right(row)))

def move(grid, direction: int) -> bool:
    "right is 0, up is 1, left is 2, down is 3"
    new_grid = grid
    for _ in range(direction):
        new_grid = rotate_clockwise(new_grid)
    new_grid = sum((move_row_right(new_grid[i:i+4]) for i in range(0, 16, 4)), [])
    for _ in range(-direction % 4):
        new_grid = rotate_clockwise(new_grid)
    return new_grid

def get_empty_cells(grid):
    return [i for i, val in enumerate(grid) if val is None]


def main():
    grid = [None] * 16
    sprites = []
    empty_cells = list(range(16))
    keys = ([False, False], [False, False], [False, False], [False, False])
    lost = False
    key_indexes = 7, 26, 4, 22 # 26 w, 4 a, 22 s, 7 d
    for i in range(2):
        cell = choice(empty_cells)
        num = 2 if randint(1, 10) == 1 else 1
        grid[cell] = num
        if i == 0:
            del empty_cells[cell]
    sprites = get_sprites(grid)
    while True:
        GRID.draw()
        for sprite in sprites:
            sprite.draw()
        if lost:
            GAME_OVER_TEXT.draw()
            update()
            continue
        did_move_this_frame = False
        keys_pressed = list(pygame.key.get_pressed())
        for index, (key_info, key_index) in enumerate(zip(keys, key_indexes)):
            del key_info[0]
            key_info.append(keys_pressed[key_index])
            if key_info == JUST_CLICKED and not did_move_this_frame:
                did_move_this_frame = True
                new_grid = move(grid, index)
        if did_move_this_frame and new_grid != grid:
            grid = new_grid
            del new_grid
            grid[choice(get_empty_cells(grid))] = 2 if randint(1, 10) == 1 else 1
            sprites = get_sprites(grid)
            lost = all(grid == move(grid, i) for i in range(4))
        update()

main()