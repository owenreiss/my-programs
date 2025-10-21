# optimal pyraminx solver

import time

#solved = yellow front blue bottom

#tip pieces and center piecs recorded by amnt of clockwise turns\n
#to be solved in order: top, left, right, back

#edge positions:
#first color on edge is key sticker
#0 = top left, yr, key stick front
#1 = top right, yg, key stick front
#2 = top back, gr, key stick right
#3 = bottom front, yb, key stick front
#4 = bottom right, bg, key stick down
#5 = bottom left,  br, key stick down
#sticket priorities: y, b, g, r

#idx0 = tips
#idx1 = centers
#idx2 = edge poses
#idx3 = edge oris
#example = ((1, 1, 0, 0), (0, 1, 1, 2), (0, 1, 2, 4, 5, 3), (0, 1, 1, 1, 0, 1))

def print_depth_msg(depth, timee):
    print(f"{depth} moves searched after {round(timee * 1000, 3)} miliseconds")
    
def perform_move(move, state):
    move_list = MOVE_LIST[VALID_MOVES.index(move)]
    tips, centers, edge_poses, edge_oris = [], [], [None] * 6, [None] * 6
    for idx, num in enumerate(move_list[0]):
        tips.append((state[0][idx] + num) % 3)
        centers.append((state[1][idx] + num) % 3)
    for num in range(6):
        edge_poses[num] = state[2][move_list[1][num]]
    for idx, ori in enumerate(move_list[2]):
        edge_oris[idx] = (state[3][move_list[1][idx]] + ori) % 2
    return (tuple(tips), tuple(centers), tuple(edge_poses), tuple(edge_oris))

def simple_move(move, state):
    move_list = MOVE_LIST[VALID_MOVES.index(move)]
    centers, edge_poses, edge_oris = [[], [None] * 6, [None] * 6]
    for idx, num in enumerate(move_list[0]):
        centers.append((state[0][idx] + num) % 3)
    for num in range(6):
        edge_poses[num] = state[1][move_list[1][num]]
    for idx, ori in enumerate(move_list[2]):
        edge_oris[idx] = (state[2][move_list[1][idx]] + ori) % 2
    return (tuple(centers), tuple(edge_poses), tuple(edge_oris))

def convert(moves):
    new_moves = []
    for move in moves:
        new_moves.append(CONVERTED_MOVES[VALID_MOVES.index(move)])
    return new_moves

def iden_move(first, second):
    r_iden = {"R", "S"}
    l_iden = {"L", "M"}
    u_iden = {"U", "V"}
    biden = {"B", "C"}
    if first in r_iden:
        return second in r_iden
    elif first in l_iden:
        return second in l_iden
    elif first in u_iden:
        return second in u_iden
    elif first in biden:
        return second in biden
    else:
        raise ValueError("Illegal first move in function: iden_move")

def invert(moves):
    new_moves = []
    for move in moves[::-1]:
        new_moves.append(INVERTED_MOVES[VALID_MOVES.index(move)])
    return new_moves

def from_start(idx):
    for num in range(8):
        addable = simple_move(VALID_MOVES[num], start[idx][-3:])
        if iden_move(VALID_MOVES[num], dict_start[start[idx]][-1]) or addable in dict_start:
            continue
        addable_list.append(addable)
        dict_start[addable] = dict_start[start[idx]] + VALID_MOVES[num]
        start.append(addable)
        match = find_match(addable, True)
        if match:
            return match, addable
    return False, "yo"

def from_solved(idx):
    for num in range(8):
        addable = simple_move(VALID_MOVES[num], solved[idx][-3:])
        if iden_move(VALID_MOVES[num], dict_solved[solved[idx]][-1]) or addable in dict_solved:
            continue
        dict_solved[addable] = dict_solved[solved[idx]] + VALID_MOVES[num]
        solved.append(addable)
        match = find_match(addable, False)
        if match:
            return match, addable
    return False, "yo"

def find_match(state, start):
    if start:
        return state in dict_solved
    else:
        return state in dict_start

def find_moves(dict_in, match_state):
    on_start = (dict_in == dict_start)
    if on_start:
        dict_opp = dict_solved
    else:
        dict_opp = dict_start
    fn_moves = []
    moves_beg = dict_in[match_state][1:]
    moves_end = dict_opp[match_state][1:]
    for move in moves_beg:
        fn_moves.append(move)
    for move in invert(moves_end):
        fn_moves.append(move)
    if not on_start:
        fn_moves = "".join(invert(fn_moves))
    return fn_moves

def main():
    orig_time = time.time()
    depth = 0
    prev_lim = 0
    match = False
    while not match:
        depth += 1
        list_in = dict_start
        #print_depth_msg(depth, time.time() - orig_time)
        limit = len(start)
        srch_idx = prev_lim
        while srch_idx < limit and not match:
            match, item_on = from_start(srch_idx)
            srch_idx += 1
        if not match:
            depth += 1
            #print_depth_msg(depth, time.time() - orig_time)
            list_in = dict_solved
            srch_idx = prev_lim
            while srch_idx < limit and not match:
                match, item_on = from_solved(srch_idx)
                srch_idx += 1
        if match:
            first_moves = find_moves(list_in, item_on)
        prev_lim = limit
    new_state = start[0]
    for move in first_moves:
        new_state = perform_move(move, new_state)
    fn_moves = convert(first_moves) 
    last_tips = new_state[0]
    tip_moves = []
    tip_algs = [["", "u", "u'"], ["", "l", "l'"], ["", "r", "r'"], ["", "b", "b'"]]
    iv_tips = [["", "u'", "u"], ["", "l'", "l"], ["", "r'", "r"], ["", "b'", "b"]]
    iv_tips_moves = []
    iv_moves = convert(invert(first_moves))
    for idx, tip in enumerate(last_tips):
        tip_moves.append(tip_algs[idx][tip])
        iv_tips_moves.append(iv_tips[idx][tip])
    for move in tip_moves:
        if move != "":
            fn_moves.append(move)
    for move in iv_tips_moves:
        if move != "":
            iv_moves.append(move)
    return " ".join(fn_moves), " ".join(iv_moves), int(round((time.time() - orig_time) * 1000)), start[0]




addable_list = []
SOLVED_STATE = ((0, 0, 0, 0), (0, 0, 0, 0), tuple(range(6)), (0, 0, 0, 0, 0, 0))
solved = [SOLVED_STATE]
start = [((1, 1, 0, 0), (0, 1, 1, 2), (0, 1, 2, 4, 5, 3), (0, 1, 1, 1, 0, 1))]
dict_solved = {solved[0] : " "}
dict_start = {start[0] : " "}
U = ((2, 0, 0, 0), (1, 2, 0, 3, 4, 5), (1, 0, 1, 0, 0, 0))
UP = ((1, 0, 0, 0), (2, 0, 1, 3, 4, 5), (1, 1, 0, 0, 0, 0))
R = ((0, 0, 2, 0), (0, 3, 2, 4, 1, 5), (0, 1, 0, 0, 1, 0))
RP = ((0, 0, 1, 0), (0, 4, 2, 1, 3, 5), (0, 1, 0, 1, 0, 0))
L = ((0, 2, 0, 0), (5, 1, 2, 0, 4, 3), (1, 0, 0, 1, 0, 0))
LP = ((0, 1, 0, 0), (3, 1, 2, 5, 4, 0), (1, 0, 0, 0, 0, 1))
B = ((0, 0, 0, 2), (0, 1, 4, 3, 5, 2), (0, 0, 0, 0, 1, 1))
BP = ((0, 0, 0, 1), (0, 1, 5, 3, 2, 4), (0, 0, 1, 0, 0, 1))
VALID_MOVES = "UVRSLMBC"
INVERTED_MOVES = "VUSRMLCB"
CONVERTED_MOVES = ["U", "U'", "R", "R'", "L", "L'", "B", "B'"]
MOVE_LIST = (U, UP, R, RP, L, LP, B, BP)

class God():
    def __init__(self):
        print("0 moves searched in 0.0 seconds")
        self.set_states = {((0, 0, 0, 0), tuple(range(6)), (0, 0, 0, 0, 0, 0))}
        self.list_states = [((0, 0, 0, 0), tuple(range(6)), (0, 0, 0, 0, 0, 0))]

    def do_moves(self, idx):
        to_print, length = False, None
        for num in range(8):
            addable = simple_move(VALID_MOVES[num], self.list_states[idx])
            if addable in self.set_states:
                continue
            self.set_states.add(addable)
            self.list_states.append(addable)
            if len(self.list_states) % 10000 == 0:
                to_print, length = True, len(self.list_states)
        return to_print, length

    def main(self):
        orig_time = time.time()
        prev_lim = 0
        combos = 933120
        depth = 0
        while len(self.list_states) < combos:
            srch_idx = prev_lim
            limit = len(self.list_states)
            while srch_idx < limit and len(self.list_states) < combos:
                to_print, length = self.do_moves(srch_idx)
                srch_idx += 1
                if to_print:
                    print("States searched:", length, end="\r")
            depth += 1
            print(f"{depth} moves searched in {round(time.time() - orig_time, 3)} seconds")
            print("States searched:", len(self.list_states) - (len(self.list_states) % 10000), end="\r")
        print(f"God's number is {depth} in {round(time.time() - orig_time, 3)} seconds")

def main():
    moves, iv_moves, time_ms, srt_state = main()
    print()
    print(f"Solution: {moves}")
    print(f"Inverted solution: {iv_moves}")
    print(f"Time taken: {time_ms} miliseconds")
    print(f"Start state: {srt_state}")
    print()

def god():
    God().main()  

if input("God or regular (god) (reg): ").lower() == "god":
    god()
else:
    main()
