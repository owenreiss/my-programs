# rubik's cube solver with visual inputting. Includes my algorithm and a more efficient algorithm

import pygame
import sys
import os
from random import randint
from time import perf_counter

import twophase.solver as sv

import _visual3x3_info as info
import _3x3_non_optimal as main3x3

os.chdir("/Users/owenreiss/Desktop/Coding/python/cube_images")

SIZE_OF_SQUARE = 62
pygame.init()

class Square(pygame.sprite.Sprite):
    "Assigned a color and coordinates to be at. Represents a single sticker on a Rubik's cube."
    def __init__(self, color, coordinates, *, size=SIZE_OF_SQUARE, border_margin=10):
        super().__init__() # supa init
        self.color = color # super init - Julian
        self.image = pygame.image.load(color + ".png")
        self.image = pygame.transform.scale(self.image, (size,) * 2)
        self.rect = self.image.get_rect()
        self.rect.topleft = tuple(x - 1 for x in coordinates) # original coordinates were a bit off; the minus 1 makes it look better
        self.border_img = pygame.image.load("black.png")
        self.border_img = pygame.transform.scale(self.border_img, (size + (border_margin * 2),) * 2)
        self.border_rct = self.border_img.get_rect()
        self.border_rct.topleft = tuple(x - border_margin - 1 for x in coordinates)
        self.orig_coords = coordinates

    def __repr__(self):
        if self.orig_coords in SLOT_COORDINATES: # if coordinates self is at are at a valid slot
            return f"Square object of color {self.color} at index {SLOT_COORDINATES.index(self.orig_coords)}"
        elif self.color != "N":
            return f"Square object of color {self.color} acting as a selecter"
        else:
            return f"Square object of null acting as a selecter"

    def draw(self):
        "Draw self, no border."
        DISPLAY.blit(self.image, self.rect)
    
    def with_border_draw(self):
        "Draw self, with border."
        DISPLAY.blit(self.border_img, self.border_rct)
        self.draw()

#class break

def write_to(state, *, filename="prev_3x3_use.txt"):
    "writes color state to default file: prev_3x3_use.txt"
    with open(f"/Users/owenreiss/Desktop/Coding/python/programs/{filename}", "w") as handle:
        for clr in state:
            handle.write(clr + "\n")
    return f'Successfully wrote state to "{filename}" in "/Users/owenreiss/Desktop/Coding/python/programs/"'

def ask_last_use():
    "gets last complete session info and prompts if user wants to reuse it"
    fnt = pygame.font.Font("freesansbold.ttf", 30)
    if not is_valid_last_use():
        txt1 = fnt.render("Hmm... It looks like the file that holds", True, (0,) * 3)
        txt2 = fnt.render("the previous user's scramble has been interfered", True, (0,) * 3)
        txt3 = fnt.render("with. Click me to solve your cube!", True, (0,) * 3)
        txt1_rct = txt1.get_rect()
        txt2_rct = txt2.get_rect()
        txt3_rct = txt3.get_rect()
        txt1_rct.center = (DISPLAY_SIZE[0] // 2, 60)
        txt2_rct.center = (DISPLAY_SIZE[0] // 2, 100)
        txt3_rct.center = (DISPLAY_SIZE[0] // 2, 140)
        dct = {txt1: txt1_rct, txt2: txt2_rct, txt3: txt3_rct}
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            DISPLAY.fill((127,) * 3)
            for img, rct in dct.items():
                DISPLAY.blit(img, rct)
            if pygame.mouse.get_pressed()[0]:
                x, y = pygame.mouse.get_pos()
                for rct in dct.values():
                    if rct.collidepoint(x, y):
                        return [None] * 48, [None] * 48

            pygame.display.update()
            FPS.tick(30)

    maintxt = fnt.render("Do you want to use the previous state?", True, (0,) * 3)
    maintxt_rect = maintxt.get_rect()
    maintxt_rect.center = ((DISPLAY_SIZE[0] // 2) + 1, 60)
    yestxt = fnt.render("Yes", True, (0, 255, 0))
    yestxt_rect = yestxt.get_rect()
    yestxt_rect.center = (DISPLAY_SIZE[0] // 4, 150)
    notxt = fnt.render("No", True, (255, 0, 0))
    notxt_rect = notxt.get_rect()
    notxt_rect.center = ((DISPLAY_SIZE[0] * 3) // 4, 150)
    dict_all = {maintxt : maintxt_rect, yestxt : yestxt_rect, notxt : notxt_rect}
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        DISPLAY.fill((127,) * 3)
        for img, rct in dict_all.items():
            DISPLAY.blit(img, rct)
        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            for idx, rct in enumerate(list(dict_all.values())[1:]):
                if rct.collidepoint(x, y) and not idx: # int 0 is false, int 1 is true
                    return get_last_use()
                elif rct.collidepoint(x, y): # if being clicked and not clicking on yes
                    return [None] * 48, [None] * 48

        pygame.display.update()
        FPS.tick(30)

def is_valid_last_use(filename="prev_3x3_use.txt"):
    """Returns if state from last use is valid. If false, idx 1 is 0 if error 
    in contents; idx 1 is 1 if contents are good but cube parity is not."""
    orig_dir = os.getcwd()
    os.chdir("/Users/owenreiss/Desktop/Coding/python/programs/")
    with open(filename, "r") as handle:
        contents = handle.read()
        contents = contents.split("\n")
        contents = contents[:-1]
    os.chdir(orig_dir)
    valid_cntnts = {"W", "G", "O", "B", "R", "Y"}
    if len(contents) != 48:
        return False
    if not all([x in valid_cntnts for x in contents]):
        return False
    return no_error(contents)[0]
    
    
def no_error(colors):
    "Returns a valid state if no error found. If error, idx 0 will be False."
    if None in set(colors):
        return False, ("missing", "colors")
    corners = tuple(
        colors[x] + colors[y] + colors[z] for x, y, z in CORNER_INDEXES
    )
    edges = tuple(
        colors[x] + colors[y] for x, y in EDGE_INDEXES
    )

    names = {"W" : "white ", "O" : "orange ", "G" : "green ", "B" : "blue ", "R" : "red ", "Y" : "yellow "}
    whole_clrs = tuple(len([x for x in colors if x == CLR]) for CLR in names)
    for idx, num in enumerate(whole_clrs):
        if num > 8:
            return False, ("too much", list(names.values())[idx][:-1])
    ori_edges, state_corners, state_edges, ori_corners = [], [], [], []
    for corner in corners:
        intprt = main3x3.corner_interpret(corner)
        if intprt:
            state_corners.append(intprt[0])
            ori_corners.append(intprt[1])
        else:
            returnable = tuple(names[x] for x in corner)
            return False, returnable + ("corner does", "not exist")
    for edge in edges:
        intprt = main3x3.edge_interpret(edge)
        if intprt:
            state_edges.append(intprt[0])
            ori_edges.append(intprt[1])
        else:
            returnable = tuple(names[x] for x in edge)
            return False, returnable + ("edge doesn't", "exist")
    tup_all = (state_edges, state_corners, ori_edges, ori_corners)
    for pce_type, lst, ltrs_state in zip(("edge", "corner"), tup_all[:2], (edges, corners)):
        set_all = set()
        for idx, piece in enumerate(lst):
            if piece not in set_all:
                set_all.add(piece)
            else:
                rt = tuple([names[x] for x in ltrs_state[idx]])
                return False, ("Duplicate",) + rt + (pce_type,)
    is_legal, reason = main3x3.is_valid_state(tup_all, True)
    msgs = (("an edge is", "flipped"), ("a corner", "is twisted"), ("two pieces", "are swapped"))
    if not is_legal:
        return False, msgs[reason]
    return True, tuple(tuple(x) for x in tup_all)

def get_last_use(filename="prev_3x3_use.txt"):
    "interprets used file and returns color state and instances"
    with open(f"/Users/owenreiss/Desktop/Coding/python/programs/{filename}", "r") as handle:
        clrs = [x[0] for x in handle.readlines()]
    insts = [Square(x, y) for (x, y) in zip(clrs, SLOT_COORDINATES)]
    return clrs, insts

def get_idx(position):
    "gets idx in color_state where user clicked."
    x, y = position
    for idx, ((top, left), (bottom, right)) in enumerate(zip(SLOT_COORDINATES, tuple((a + SIZE_OF_SQUARE, b + SIZE_OF_SQUARE) for a, b in SLOT_COORDINATES))):
        if x >= top and x <= bottom and y <= right and y >= left:
            return idx
    return

def fill_clrs_func(arg_insts, checking=True):
    "returns a filled state; if can't fill, index 0 is False"
    FULL_CLRS = {"W", "O", "B", "G", "R", "Y"}
    clrs = {"W", "O", "B", "G", "R", "Y"}
    whole_clrs_dct = {"W" : "white", "O" : "orange", "B" : "blue", "G" : "green", "R" : "red", "Y" : "yellow"}
    clr_count = {x : 0 for x in clrs}
    eight_of_clr = set()
    for inst in arg_insts:
        if inst != None:
            clr_count[inst.color] += 1
            clrs -= {inst.color}
    for clr, amnt in clr_count.items():
        if amnt >= 8:
            eight_of_clr.add(clr)
    if len(clrs) > 1:
        return False, ("more than", "one color", "not on cube")
    if len(eight_of_clr) == 6:
        if checking:
            return False, # don"t want to show user fill if everything is already filled
        else:
            return arg_insts,
    if len(eight_of_clr) == 5:
        for clr in FULL_CLRS:
            if clr not in eight_of_clr:
                clrs = {clr}
                break
    for clr, amnt in clr_count.items():
        if amnt != 8 and clrs != {clr}:
            return False, ("can't fill with", "invalid", whole_clrs_dct[clr], "amount")
    unused = list(clrs)[0]
    insts = arg_insts # same object
    for idx, inst in enumerate(insts):
        if inst == None:
            if checking:
                return True,
            else:
                insts[idx] = Square(unused, SLOT_COORDINATES[idx])
    return insts,

def prompt_end_state():
    fnt = pygame.font.Font("freesansbold.ttf", 30)
    msg = fnt.render("What end state do you want to get to?", True, (0,) * 3)
    msg_rct = msg.get_rect()
    msg_rct.center = (DISPLAY_SIZE[0] // 2, 100)
    msg1 = fnt.render("Solved", True, (0, 255, 0))
    msg1_rct = msg1.get_rect()
    msg1_rct.center = (DISPLAY_SIZE[0] // 3, 200)
    msg2 = fnt.render("Other", True, (255, 0, 0))
    msg2_rct = msg2.get_rect()
    msg2_rct.center = (DISPLAY_SIZE[0] * 2 // 3, 200)
    msgs_dct = {msg: msg_rct, msg1: msg1_rct, msg2: msg2_rct}
    while True:
        DISPLAY.fill((127,) * 3)
        for msg, rct in msgs_dct.items():
            DISPLAY.blit(msg, rct)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            for rct in msgs_dct.values():
                if rct.collidepoint(x, y):
                    if rct == msg1_rct:
                        show_solving()
                        return (tuple(range(12)), tuple(range(8)), (0,) * 12, (0,) * 8), None, None
                    elif rct == msg2_rct:
                        return prompt_loop(([None] * 48, [None] * 48), False)
        pygame.display.update()
        FPS.tick(30)

def make_error(reason):
    "creates a dict with error images and rects"
    fnt = pygame.font.Font("freesansbold.ttf", 30)
    error_dict = {}
    for idx, statement in enumerate(("Error:",) + reason):
        txt = fnt.render(statement, True, (255, 0, 0))
        rct = txt.get_rect()
        if idx >= 1:
            xtra = 28
        else:
            xtra = 0
        rct.topleft = (10, 5 + (idx * 28) + xtra)
        error_dict[txt] = rct
    return error_dict

def show_solving():
    DISPLAY.fill((127,) * 3)
    fnt = pygame.font.Font("freesansbold.ttf", 30)
    msg1 = fnt.render("Solving...", True, (0,) * 3)
    msg_rct1 = msg1.get_rect()
    msg_rct1.center = (DISPLAY_SIZE[0] // 2, (DISPLAY_SIZE[1] // 2) - (DISPLAY_SIZE[1] // 18))
    DISPLAY.blit(msg1, msg_rct1)
    pygame.display.update()
    FPS.tick(30)

def prompt_loop(whole, write=True):
    "Return colors before instances."
    color_state, shown_instances = whole
    selected = "W"
    #order of colors represented as left to right starting from top NOT INCLUDING CENTERS
    #order of faces is U, L, F, R, B, D

    fnt = pygame.font.Font("freesansbold.ttf", 30)
    msg = fnt.render("Select a center or color", True, (0,) * 3)
    msg_rct = msg.get_rect()
    msg_rct.topleft = (406, 25)
    msg1 = fnt.render("in the bottom right", True, (0,) * 3)
    msg_rct1 = msg1.get_rect()
    msg_rct1.topleft = (406, 55)
    msg2 = fnt.render("Apply colors and press", True, (0,) * 3)
    msg_rct2 = msg2.get_rect()
    msg_rct2.topleft = (406, 105)
    msg3 = fnt.render("enter when done", True, (0,) * 3)
    msg_rct3 = msg3.get_rect()
    msg_rct3.topleft = (406, 135)
    fill_clrs = fnt.render("Fill colors", True, (0,) * 3)
    rct_fill_clrs = fill_clrs.get_rect()
    rct_fill_clrs.topleft = (0, 400)
    msg_dict = {msg : msg_rct, msg1 : msg_rct1, msg2 : msg_rct2, msg3 : msg_rct3}
    error_dict = {}
    clicking = True
    clicking_from_last_use = True
    pygame.display.set_caption("Rubik's Cube Solver")

    while True:
        DISPLAY.fill((127,) * 3)
        DISPLAY.blit(BASE_CUBE_IMG, BASE_CUBE_RECT)
        valid_fill = VALID_FILL_LMBDA(shown_instances)
        if valid_fill:
            DISPLAY.blit(fill_clrs, rct_fill_clrs)
        for image, rect in msg_dict.items():
            DISPLAY.blit(image, rect)
        for image, rect in error_dict.items():
            DISPLAY.blit(image, rect)
        for instance in shown_instances:
            if instance != None: # blits all square instances
                DISPLAY.blit(instance.image, instance.rect)
        all_events = pygame.event.get()
        for event in all_events: # quits if time
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        for inst in SELECTER_INSTANCES: # makes color selectors
            if inst.color == selected:
                inst.with_border_draw()
            else:
                inst.draw()
        if pygame.mouse.get_pressed()[0]: # takes care of adding colors to the cube
            x, y = pygame.mouse.get_pos()
            for sel_inst, cent_inst in zip(SELECTER_INSTANCES, CENTER_INSTANCES):
                if (sel_inst.rect.collidepoint(x, y) or (cent_inst.rect.collidepoint(x, y) and not clicking)) and not clicking_from_last_use:
                    selected = sel_inst.color
            if SELECTER_INSTANCES[6].rect.collidepoint(x, y) and not clicking_from_last_use: # if clicking on null selecter
                selected = "N"
            idx_clicked = get_idx(pygame.mouse.get_pos())
            if idx_clicked != None and selected != "N" and not clicking_from_last_use: # if user is clicking on a valid square
                color_state[idx_clicked] = selected
                shown_instances[idx_clicked] = Square(selected, SLOT_COORDINATES[idx_clicked])
            elif idx_clicked != None and not clicking_from_last_use:
                color_state[idx_clicked] = None
                shown_instances[idx_clicked] = None
            if rct_fill_clrs.collidepoint(x, y) and valid_fill:
                filled = fill_clrs_func(shown_instances, False)
                if filled[0]:
                    shown_instances = filled[0]
                    color_state = [sq.color for sq in shown_instances]
                    error_dict = {}
                else:
                    error_dict = make_error(filled[1])
            clicking = True
        else:
            clicking_from_last_use = False
            clicking = False
        for event in all_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    state = no_error(color_state)
                    if state[0]:
                        msg = write_to(color_state) if write else None
                        if not write:
                            show_solving()
                        return state[1], msg, shown_instances
                    else:
                        error_dict = make_error(state[1])

        pygame.display.update()
        FPS.tick(30)

def convert_kociemba_str(string: str):
    new_str = [list(x) for x in string.split()[:-1]]
    change_dict = {"1": "", "2": "2", "3": "'"}
    for idx in range(len(new_str)):
        new_str[idx][1] = change_dict[new_str[idx][1]]
    return ["".join(x) for x in new_str]


def print_kociemba(numberic_state, max_moves=18, timeout="def arg", _4x4_mode=False):
    facelet_state = convert_numeric_state_to_cubestring(numberic_state)
    if timeout == "def arg":
        timeout = randint(1000, 2000) / 1000
    cubestring = list(facelet_state)
    match_dct = {"W": "U", "O": "L", "G": "F", "R": "R", "B": "B", "Y": "D"}
    for idx, val in zip((4, 13, 22, 31, 40, 49), match_dct.keys()):
        cubestring.insert(idx, val)
    for idx, clr in enumerate(cubestring):
        cubestring[idx] = match_dct[clr]
    cubestring = cubestring[:9] + cubestring[27:36] + cubestring[18:27] + cubestring[45:54] + cubestring[9:18] + cubestring[36:45]
    orig_time = perf_counter()
    moves = convert_kociemba_str(sv.solve("".join(cubestring), max_moves, timeout))
    end_time = perf_counter()
    time_taken = round(end_time - orig_time, 3)
    inverted_moves = main3x3.invert(moves)
    if not _4x4_mode:
        print(f"\nSolution: {' '.join(moves)}\n")
        print(f"INVERTED solution: {' '.join(inverted_moves)}\n")
        print(f"Amount of moves: {len(moves)}")
        print(f"Time taken: {time_taken} seconds\n")
        return
    return moves
    
def convert_numeric_state_to_cubestring(state):
    cubestring = [None] * 48
    edges, corners, eori, cori = state
    for idx, (piece, ori) in enumerate(zip(corners, cori)):
        for num in range(3):
            cubestring[CORNER_INDEXES[idx][num]] = info.c_clrs[piece][(ori+num)%3]
    for idx, (piece, ori) in enumerate(zip(edges, eori)):
        for num in range(2):
            cubestring[EDGE_INDEXES[idx][num]] = info.e_clrs[piece][(ori+num)%2]
    return cubestring


def main(kociemba=True):
    "whole program"
    fnt = pygame.font.Font("freesansbold.ttf", 30)
    first_state, file_msg, first_colors, = prompt_loop(ask_last_use())
    end_state, delete_me, second_colors = prompt_end_state()
    end_st_is_solved = end_state == (tuple(range(12)), tuple(range(8)), (0,) * 12, (0,) * 8)
    current_instances = first_colors if end_st_is_solved else second_colors
    del delete_me
    both_instances = (first_colors, second_colors)
    first_state = [list(lst) for lst in first_state]
    for fidx, lst in enumerate(end_state[:2]):
        for idx in range(len(lst)):
            first_state[fidx][idx] = lst.index(first_state[fidx][idx])
    for idx, piece in enumerate(first_state[0]):
        first_state[2][idx] = int(first_state[2][idx] != end_state[2][piece]) # int False is 0, int True is 1
    for idx, piece in enumerate(first_state[1]):
        first_state[3][idx] = (first_state[3][idx] - end_state[3][piece]) % 3
    if not kociemba:
        main3x3.compute_and_print(first_state, False)
    else:
        print_kociemba(first_state)
    am_returning = True
    print("RETURN TO EXIT")
    msg = fnt.render("Solution is in terminal", True, (0,) * 3)
    msg_rect = msg.get_rect()
    msg1 = fnt.render("Return to exit", True, (0,) * 3)
    msg_rect1 = msg1.get_rect()
    if end_st_is_solved:
        msg_rect.topleft = (406, 95)
        msg_rect1.topleft = (406, 125)
    else:
        msg_rect.topleft = (406, 20)
        msg_rect1.topleft = (406, 50)
    msg2 = fnt.render("Click to switch from start", True, (0,) * 3)
    msg_rect2 = msg2.get_rect()
    msg_rect2.topleft = (406, 110)
    msg3 = fnt.render("to end state and back", True, (0,) * 3)
    msg_rect3 = msg3.get_rect()
    msg_rect3.topleft = (406, 140)
    st_end = ("Start", "End")
    idx_on = both_instances.index(current_instances) # 0 start, 1 end
    msg4 = fnt.render(st_end[idx_on] + " state", True, (0,) * 3)
    msg_rect4 = msg4.get_rect()
    msg_rect4.center = (96, 111)
    msg5 = fnt.render("Looking at:", True, (0,) * 3)
    msg_rect5 = msg5.get_rect()
    msg_rect5.center = (96, 81)
    msgs_dct = {msg: msg_rect, msg1: msg_rect1, msg2: msg_rect2, msg3: msg_rect3, msg4: msg_rect4, msg5: msg_rect5}
    forbidden_if_solved = {msg2, msg3, msg4, msg5}
    am_returning = True
    while True:
        for event in pygame.event.get(): # quits if time
            if event.type == pygame.QUIT:
                print()
                pygame.quit()
                sys.exit()
            if event.type != pygame.KEYDOWN:
                am_returning = False
            elif event.key != pygame.K_RETURN:
                am_returning = False
            elif not am_returning:
                print()
                pygame.quit()
                sys.exit()
        DISPLAY.fill((127,) * 3)
        DISPLAY.blit(BASE_CUBE_IMG, BASE_CUBE_RECT)
        for img, rct in msgs_dct.items():
            if img not in forbidden_if_solved or not end_st_is_solved:
                DISPLAY.blit(img, rct)
        for instance in current_instances:
            DISPLAY.blit(instance.image, instance.rect)
        if not pygame.mouse.get_pressed()[0]:
            am_clicking = False 
        if pygame.mouse.get_pressed()[0] and not end_st_is_solved and not am_clicking:
            am_clicking = True
            idx_on = (idx_on + 1) % 2
            current_instances = both_instances[idx_on]
            msg4 = fnt.render(st_end[idx_on] + " state", True, (0,) * 3)
            msg_rect4 = msg4.get_rect()
            msg_rect4.center = (96, 111)
            msgs_dct = {msg: msg_rect, msg1: msg_rect1, msg2: msg_rect2, msg3: msg_rect3, msg4: msg_rect4, msg5: msg_rect5}
            forbidden_if_solved = {msg2, msg3, msg4, msg5}
        pygame.display.update()
        FPS.tick(30)

# globals defined here
DISPLAY_SIZE = (796, 597)
DISPLAY = pygame.display.set_mode(DISPLAY_SIZE)
FPS = pygame.time.Clock()
BASE_CUBE_IMG = pygame.image.load("base_cube.png")
BASE_CUBE_IMG = pygame.transform.scale(BASE_CUBE_IMG, DISPLAY_SIZE)
BASE_CUBE_RECT = BASE_CUBE_IMG.get_rect()
BASE_CUBE_RECT.topleft = (0,) * 2
COLORS = "WGBROYN" # N is null
SLOT_COORDINATES = info.ALL_COORDS
SELECTER_SIZE = 50
SELECTER_COORDINATES = ((426, 444), (552, 444), (682, 444), (426, 517), (552, 517), (682, 517), (75, 475))
CORNER_INDEXES = info.CORNER_INDEXES
EDGE_INDEXES = info.EDGE_INDEXES
CENTER_COORDS = ((269 - 1, 69), (269 - 1,) * 2, (667 - 1, 269 - 1), (469 - 2, 269 - 1), (69, 269 - 1), (269 - 1, 469 - 2))
VALID_FILL_LMBDA = lambda arg_insts: bool(fill_clrs_func(arg_insts)[0])

SELECTER_INSTANCES = tuple(
    [Square(color, coordinate, size=SELECTER_SIZE)
    for color, coordinate in zip(COLORS, SELECTER_COORDINATES)]
)

CENTER_INSTANCES = tuple(
    Square(color, coordinate) for (color, coordinate) in zip(COLORS, CENTER_COORDS)
) #center instances are not drawn, but they exist to see if a center is being clicked on

if __name__ == "__main__":
    main() # give False if Owen's solving method is wanted; if nothing given will use Kociemba's Algotithm
