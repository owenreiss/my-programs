# optimal skewb solver


#First working state! ((0, 2, 3, 1), (1, 1, 0, 1, 1, 1, 0, 0), (2, 0, 3, 5, 4, 1))
#Solution: R L' F R' F' L' B

#fixed corners are wgo, wbr, ygr, ybo
#movable corners:
#0 = top left back, wob
#1 = top right front, wrg
#2 = bottom left front, yog
#3 = bottom right back, yrb

#hold with wgo in ful and ygr bfr. Twists along fixed corners

import time
import random

L = ((2, 0, 1, 3), (2, 1, 0, 1, 1, 0, 0, 0), (4, 0, 2, 3, 1, 5))
LP = ((1, 2, 0, 3), (1, 2, 0, 2, 2, 0, 0, 0), (1, 4, 2, 3, 0, 5))
R = ((1, 3, 2, 0), (0, 1, 2, 1, 0, 0, 1, 0), (5, 1, 2, 0, 4, 3))
RP = ((3, 0, 2, 1), (0, 2, 1, 2, 0, 0, 2, 0), (3, 1, 2, 5, 4, 0))
F = ((0, 2, 3, 1), (0, 0, 0, 1, 1, 0, 1, 2), (0, 2, 5, 3, 4, 1))
FP = ((0, 3, 1, 2), (0, 0, 0, 2, 2, 0, 2, 1), (0, 5, 1, 3, 4, 2))
B = ((3, 1, 0, 2), (0, 1, 0, 0, 1, 2, 1, 0), (0, 1, 4, 2, 3, 5))
BP = ((2, 1, 3, 0), (0, 2, 0, 0, 2, 1, 2, 0), (0, 1, 3, 4, 2, 5))
VALID_MOVES = {"L" : L, "L'" : LP, "R" : R, "R'" : RP, "F" : F, "F'" : FP, "B" : B, "B'" : BP}
VM_LIST = tuple(VALID_MOVES.keys())
INVERTED = {"L" : "L'", "L'" : "L", "R" : "R'", "R'" : "R", "F" : "F'", "F'" : "F", "B" : "B'", "B'" : "B"}
SOLVED_STATE = (tuple(range(4)), (0,) * 8, tuple(range(6)))

def invert(moves):
    new = []
    for move in moves[::-1]:
        new.append(INVERTED[move])
    return tuple(new)

def perform_move(move, state):
    #returns a tuple of three tuples with new state
    cpos, cori, ct_pos = state
    new_cpos, new_ori, new_ctpos = [None] * 4, [None] * 8, [None] * 6
    move_cpos, move_cori, move_ctpos = VALID_MOVES[move]
    full_cpos = []
    for num in range(8):
        if (num % 2 == 0 and num <= 3) or (num % 2 == 1 and num >= 4):
            full_cpos.append(num)
        elif move_cpos[num // 2] <= 1:
            full_cpos.append(move_cpos[num // 2] * 2 + 1)
        else:
            full_cpos.append(move_cpos[num // 2] * 2)
    for idx, piece in enumerate(move_cpos):
        new_cpos[idx] = cpos[piece]
    for idx, piece in enumerate(full_cpos):
        new_ori[idx] = (cori[piece] + move_cori[idx]) % 3
    for idx, piece in enumerate(move_ctpos):
        new_ctpos[idx] = ct_pos[piece]
    return tuple(new_cpos), tuple(new_ori), tuple(new_ctpos)

class BruteForcer():
    def __init__(self, state):
        self.state = state
        self.start = {state : ()}
        self.solved = {SOLVED_STATE : ()}
        self.list_start = [state]
        self.list_solved = [SOLVED_STATE]

    def find_match(self, state, chk_sv):
        if chk_sv:
            return state in self.solved
        else:
            return state in self.start

    def st_search(self, idx):
        for num in range(8):
            addable = perform_move(VM_LIST[num], self.list_start[idx])
            if idx != 0:
                if addable in self.start:
                    continue
                lister = list(self.start[self.list_start[idx]])
                lister.append(VM_LIST[num])
                lister = tuple(lister)
                self.start[addable] = lister
            else:
                self.start[addable] = (VM_LIST[num],)
            self.list_start.append(addable)
            match = self.find_match(addable, True)
            if match:
                return True, addable
        return False, None

    def sv_search(self, idx):
        for num in range(8):
            addable = perform_move(VM_LIST[num], self.list_solved[idx])
            if idx != 0:
                if addable in self.solved:
                    continue
                lister = list(self.solved[self.list_solved[idx]])
                lister.append(VM_LIST[num])
                lister = tuple(lister)
                self.solved[addable] = lister
            else:
                self.solved[addable] = (VM_LIST[num],)
            self.list_solved.append(addable)
            match = self.find_match(addable, False)
            if match:
                return True, addable
        return False, None

    def find_moves(self, dict_in, state, start):
        moves_st = dict_in[state]
        if start:
            moves_sv = invert(self.solved[state])
        else:
            moves_sv = invert(self.start[state])
        all = (moves_st, moves_sv)
        final = []
        for tup in all:
            for move in tup:
                final.append(move)
        if start:
            return tuple(final)
        else:
            return invert(final)

    def main(self):
        prev_lim = 0
        orig_time = time.time()
        depth = 0
        match = False
        while True:
            depth += 1
            dict_in = self.start
            limit = len(self.start)
            srch_idx = prev_lim
            while srch_idx < limit and not match:
                match, item_on = self.st_search(srch_idx)
                srch_idx += 1
            if not match:
                depth += 1
                dict_in = self.solved
                srch_idx = prev_lim
                while srch_idx < limit and not match:
                    match, item_on = self.sv_search(srch_idx)
                    srch_idx += 1
            if match:
                moves = self.find_moves(dict_in, item_on, dict_in == self.start)
                return moves, invert(moves), int((time.time() - orig_time) * 1000), depth, self.state
            prev_lim = limit


class God():
    def __init__(self):
        self.states = {SOLVED_STATE : 0}
        self.list_states = [SOLVED_STATE]
        self.dists = [1]
        self.cur_dist = 0
    
    def search(self, idx):
        to_print = False
        length = None
        for num in range(8):
            addable = perform_move(VM_LIST[num], self.list_states[idx])
            if addable in self.states:
                continue
            self.list_states.append(addable)
            self.states[addable] = self.states[self.list_states[idx]] + 1
            self.cur_dist += 1
            if len(self.list_states) % 10000 == 0:
                to_print = True
                length = len(self.list_states)
        return to_print, length

    def main(self):
        prev_lim = 0
        orig_time = time.time()
        depth = 0
        combos = 3149280
        while len(self.states) < combos:
            self.cur_dist = 0
            depth += 1
            print("Depth", depth, "in", round(time.time() - orig_time, 2), "seconds with", len(self.list_states), "states searched")
            print("States searched:", len(self.list_states) - (len(self.list_states) % 10000), "/ 3,149,280", end="\r")
            limit = len(self.states)
            srch_idx = prev_lim
            while srch_idx < limit and len(self.states) < combos:
                to_print, length = self.search(srch_idx)
                srch_idx += 1
                if to_print:
                    print("States searched:", length, "/ 3,149,280", end="\r")
            prev_lim = limit
            self.dists.append(self.cur_dist)
        print("States searched: 3,149,140 / 3,149,140")
        print()
        rand = random.choices(self.list_states[len(self.list_states) - self.dists[-1]:], k=5)
        for state in rand:
            print(state)
        print("Above are five random 11 move states")
        print("God's number is", depth, "in", round(time.time() - orig_time, 2), "seconds")
        print()
        print("Distributions of moves")
        print(self.dists)
        return

def main(state):
    solution, iv_solution, ms_taken, amnt_of_moves, orig_state = BruteForcer(state).main()
    print()
    print("Solution:", " ".join(solution))
    print("=" * (len("INVERTED solution:" + " ".join(iv_solution)) + 1))
    print("INVERTED solution:", " ".join(iv_solution))
    print("Time taken:", ms_taken, "miliseconds")
    print("Amount of moves:", amnt_of_moves)
    print("Start state:", orig_state)
    print()
    return

def god():
    God().main()

if input("God or regular (god/reg): ").lower() == "god":
    god()
else:
    main(((2, 0, 1, 3), (1, 2, 1, 1, 1, 2, 2, 1), (2, 0, 5, 3, 1, 4)))
