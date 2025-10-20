import copy
import time
import random
import os

def convert(moves):
    new = []
    for move in moves:
        new.append(conversion_from_vm[valid_moves.index(move)])
    return new
def round_ms(time):
    return round(time * 1000)
def invert(moves, list_used, reg_list_used):
    new = []
    for move in moves[::-1]:
        new.append(list_used[reg_list_used.index(move)])
    return new

def perform_move(move, state):
    pos = state[0]
    ori = state[1]
    new_pos = [0, 1, 2, 3, 4, 5]
    new_ori = copy.deepcopy(ori)
    valid_index = valid_moves.index(move)
    list_move = list_moves[valid_index]
    ind = index_val[valid_index]
    new_ori[ind[0]] = (new_ori[ind[0]] + ind[1]) % 3
    for idx, piece_num in enumerate(pos):
        new_pos[list_move[idx]] = piece_num
    return [new_pos, new_ori]

def iden_move(last_move, wanted_move):
    l_iden = ["L", "M"]
    r_iden = ["R", "S"]
    f_iden = ["F", "G"]
    b_iden = ["B", "C"]
    if wanted_move in r_iden:
        return last_move in r_iden
    if wanted_move in f_iden:
        return last_move in f_iden
    if wanted_move in l_iden:
        return last_move in l_iden
    if wanted_move in b_iden:
        return last_move in b_iden
    raise ValueError("Illegal move in iden_move arg 2")

def find_match(state, st_or_sv):
    if st_or_sv == "st":
        if state in solved:
           return True
        else:
            return False
    if st_or_sv == "sv":
        if state in start:
            return True
        else:
            return False
    raise ValueError("Thing other than 'st' or 'sv' put into find_match arg 2")

def look_from_start(start_id):
    global match_among_lists
    for movenum in range(8):
        new_state = perform_move(valid_moves[movenum], start[start_id])
        if start_id != 0:
            if not iden_move((moves_start[start_id])[len(moves_start[start_id]) - 1], valid_moves[movenum]):
                start.append(new_state)
                match_among_lists = find_match(new_state, "st")
                moves_start.append(moves_start[start_id] + valid_moves[movenum])
                if match_among_lists:
                    break
        else:
            start.append(new_state)
            match_among_lists = find_match(new_state, "st")
            moves_start.append(valid_moves[movenum])
            if match_among_lists:
                break

def look_from_solved(solved_id):
    global match_among_lists
    for movenum in range(8):
        new_state = perform_move(valid_moves[movenum], solved[solved_id])
        if solved_id != 0:
            if not iden_move((moves_solved[solved_id])[len(moves_solved[solved_id]) - 1], valid_moves[movenum]):
                solved.append(new_state)
                match_among_lists = find_match(new_state, "sv")
                moves_solved.append(moves_solved[solved_id] + valid_moves[movenum])
                if match_among_lists:
                    break
        else:
            solved.append(new_state)
            match_among_lists = find_match(new_state, "sv")
            moves_solved.append(valid_moves[movenum])
            if match_among_lists:
                break

def find_moves(contained_list, index_main):
    if contained_list == start:
        opp_list = solved
        move_list = moves_start
        opp_move = moves_solved
    else:
        opp_list = start
        move_list = moves_solved
        opp_move = moves_start
    index_opp = opp_list.index(contained_list[index_main])
    moves = []
    for char in move_list[index_main]:
        moves.append(char)
    for char in opp_move[index_opp][::-1]:
        moves.append(inversion_from_vm[valid_moves.index(char)])
    if contained_list == solved:
        moves = invert(moves, inversion_from_vm, valid_moves)
    moves = convert(moves)
    return moves

def main():
    global start_time
    global match_among_lists
    generation = 0
    depth = 0
    prev_lim = 0
    while not match_among_lists:
        list_in = start
        generation += 1
        depth += 1
        limit = len(start)
        start_index = prev_lim
        while start_index < limit and not match_among_lists:
            look_from_start(start_index)
            start_index += 1
        if not match_among_lists:
            depth += 1
            list_in = solved
            start_index = prev_lim
            while start_index < limit and not match_among_lists:
                look_from_solved(start_index)
                start_index += 1
        prev_lim = limit
        if match_among_lists:
            return find_moves(list_in, len(list_in) - 1)



#ALL MOVES INVERTED
#Moves verified
L = [1, 4, 2, 3, 0, 5]
Lp = [4, 0, 2, 3, 1, 5]
R = [3, 1, 2, 5, 4, 0]
Rp = [5, 1, 2, 0, 4, 3]
F = [0, 5, 1, 3, 4, 2]
Fp = [0, 2, 5, 3, 4, 1]
B = [0, 1, 3, 4, 2, 5]
Bp = [0, 1, 4, 2, 3, 5]

valid_moves = ["L", "M", "R", "S", "F", "G", "B", "C"]
inversion_from_vm = ["M", "L", "S", "R", "G", "F", "C", "B"]
conversion_from_vm = ["L", "L'", "R", "R'", "F", "F'", "B", "B'"]
inversion_from_valid_notation = ["L'", "L", "R'", "R", "F'", "F", "B'", "B"]
list_moves = [L, Lp, R, Rp, F, Fp, B, Bp]
index_val = [[0, 2], [0, 1], [1, 2], [1, 1], [2, 2], [2, 1], [3, 2], [3, 1]]
start = [[[4, 5, 1, 0, 3, 2], [1, 1, 0, 1]]]
solved = [[[0, 1, 2, 3, 4, 5], [0, 0, 0, 0]]]
start = []
moves_start = [""]
moves_solved = [""]
match_among_lists = False
questions_ori = ["front top left (white green orange)", "back top right (white blue red)", "front bottom right (yellow green orange)", "back bottom left (yellow blue orange)"]
questions_pos = ["top", "front", "left", "right"]
start_time = time.time()

#white top green front
#hold with white green orange in front top left and yellow green red in front bottom right

#1st part: positions of centers
#0 = top, white
#1 = front, green
#2 = bottom, yellow
#3 = back, blue
#4 = left, orange
#5 = right, red

#2nd part: orientations of corners in cw twists for y or w to face up or down
#idx0 = front top left, white green orange
#idx1 = back top right, white blue red
#idx2 = front bottom right, yellow green red
#idx3 = back bottom left, yellow blue orange

def print_final():
    solution = main()
    inverted = invert(solution, inversion_from_valid_notation, conversion_from_vm)
    print()
    print("Solution: ", " ".join(solution))
    print("Inverted solution: ", " ".join(inverted))
    print()
    print("Amount of moves: ", len(solution))
    print("Start state:", str(start[0]))
    print("Time taken: %s miliseconds" % (str(round_ms(time.time() - start_time))))

def main():
    global start
    global start_time
    given_ori = []
    known_pieces = []
    print()
    print("0 = white or yellow facing up or down")
    print("1 = one clockwise turn needed to make white or yellow face up or down")
    print("2 = two clockwise turns needed to make white or yellow face up or down")
    print("PLACE WHITE GREEN ORANGE CORNER IN FRONT TOP LEFT AND PLACE YELLOW GREEN RED IN FRONT BOTTOM RIGHT")
    print()
    for num in range(4):
        valid_input = False
        while not valid_input:
            given = input("How many clockwise turns needed on " + questions_ori[num] + "?: ")
            try:
                given = int(given)
            except ValueError:
                print('"%s" unable to be converted to type: int' % (given))
            else:
                if given in range(3):
                    valid_input = True
                    given_ori.append(given)
                else:
                    print("NUMBER NOT BETWEEN 0 AND 2")
    print()
    print("0 = white")
    print("1 = green")
    print("2 = yellow")
    print("3 = blue")
    print("4 = orange")
    print("5 = red")
    print()
    for num in range(4):
        valid_input = False
        while not valid_input:
            given = input("What center piece is on " + questions_pos[num] + "?: ")
            try:
                given = int(given)
            except ValueError:
                print('"%s" unable to be converted to type: int' % (given))
            else:
                if given in range(6) and not given in known_pieces:
                    valid_input = True
                    known_pieces.append(given)
                elif given not in range(6):
                    print("NUMBER NOT BETWEEN 0 AND 5")
                else:
                    print("CAN'T HAVE TWO OF THE SAME PIECE")
    start = [[find_remaining_pos(known_pieces), given_ori]]
    start_time = time.time()
    print_final()


def find_remaining_pos(known_pieces):
    if len(known_pieces) != 4:
        raise ValueError("find_remaining_pos  length of known pieces not equal to 4. Unable to continue")
    not_in_known = []
    for num in range(6):
        if num not in known_pieces:
            not_in_known.append(num)
    swaps_list = has_even_swaps(known_pieces, not_in_known)
    return swaps_list[swaps_list[2]]

def has_even_swaps(known, not_in):
    swaps = 0
    test_state = [known[0], known[1], not_in[0], not_in[1], known[2], known[3]]
    while test_state != [0, 1, 2, 3, 4, 5]:
        for idx, thing in enumerate(test_state):
            if thing != idx:
                swapped_item = test_state[thing]
                test_state[idx] = swapped_item
                test_state[thing] = thing
                swaps += 1
                break
    return [[known[0], known[1], not_in[0], not_in[1], known[2], known[3]], [known[0], known[1], not_in[1], not_in[0], known[2], known[3]], swaps % 2]


class God():
    def __init__(self):
        self.start_time = time.time()
        self.combos = 29160
        self.states_searched = {((0, 1, 2, 3, 4, 5), (0, 0, 0, 0)) : ""}
        self.list_states = [[[0, 1, 2, 3, 4, 5], [0, 0, 0, 0]]]
        self.prev_lim = 0
        self.depth = 0
        self.movelist = [""]
        self.modern_limit = 1
        self.search_index = 0
        self.id_stopped_at = [1]
    
    def moves_sv(self, idx_in_solved):
        to_print, length = False, None
        for movenum in range(8):
            new_state = perform_move(valid_moves[movenum], self.list_states[idx_in_solved])
            tup_state = (tuple(new_state[0]), tuple(new_state[1]))
            if not tup_state in self.states_searched:
                self.states_searched[tup_state] = self.movelist[idx_in_solved] + valid_moves[movenum]
                self.list_states.append(new_state)
                self.movelist.append(self.movelist[idx_in_solved] + valid_moves[movenum])
            if len(self.list_states) % 1000 == 0:
                to_print, length = True, len(self.list_states)
        return to_print, length
            

    def main_god(self):
        while len(self.list_states) < self.combos:
            self.depth += 1
            self.modern_limit = len(self.list_states)
            self.search_index = self.prev_lim
            print("Depth: %d  Amount of states: %s in %d seconds" % (self.depth, len(self.list_states), round((time.time() - self.start_time) * 100) / 100))
            print("States searched:", len(self.list_states) - (len(self.list_states) % 1000), "/ 29,160", end="\r")
            while self.search_index < self.modern_limit:
                to_print, length = self.moves_sv(self.search_index)
                self.search_index += 1
                if to_print:
                    print("States searched:", length, "/ 29,160", end="\r")
            self.prev_lim = self.modern_limit
            self.id_stopped_at.append(len(self.list_states))
        rand_num = random.randint(self.id_stopped_at[len(self.id_stopped_at) - 2], 29155)
        tup_states = []
        for state in self.list_states[rand_num:rand_num + 5]:
            tup_states.append((tuple(state[0]), tuple(state[1])))
        moves_five = []
        for state in tup_states:
            moves_five.append(self.states_searched[state])
        list_moves_x = [[], [], [], [], []]
        for fidx, moves in enumerate(moves_five):
            for move in moves:
                list_moves_x[fidx].append(move)
        moves_five = list_moves_x
        for fidx, moves in enumerate(moves_five):
            moves_five[fidx] = convert(moves_five[fidx])
        os.chdir("/Users/owenreiss/Desktop/python/_file_ops")
        ivy_stats = open("ivy_states", "w")
        for idx, item in enumerate(self.states_searched.items()):
            state, moves = item
            if idx in self.id_stopped_at:
                ivy_stats.write("\n")
                ivy_stats.write(f"All states above take less than {self.id_stopped_at.index(idx) + 1} moves\n")
                ivy_stats.write("\n")
            ivy_stats.write(f"{state}  Solution: {' '.join(invert(moves, inversion_from_valid_notation, valid_moves))}  Inv solution: {' '.join(convert(moves))}\n")
        ivy_stats.close()
        return [self.id_stopped_at, self.depth, round(time.time() - self.start_time, 3), self.list_states[rand_num:rand_num + 5], moves_five]

def find_states_god(lengths):
    lengths.insert(0, 0)
    new_lens = []
    for num in range(0, len(lengths) - 1):
        new_lens.append(lengths[num + 1] - lengths[num])
    return new_lens

def find_god():
    sol_god = God().main_god()
    print("Distributions:", find_states_god(sol_god[0]))
    print()
    print("God's number is %d in %s seconds" % (sol_god[1], sol_god[2]))
    print()
    print("5 random 8 move states:")
    for idx, state in enumerate(sol_god[3]):
        print(str(state) + "  " + "Inverted solution: " + " ".join(sol_god[4][idx]))
    print()

if input("God mode or regular mode? (god) (reg): ").lower() == "god":
    find_god()
else:
    main()