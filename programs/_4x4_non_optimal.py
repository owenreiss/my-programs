# my algorithm for solving a 4x4 rubik's cube

import sys
import random
from time import perf_counter

import visual3x3 as vis3x3
import _3x3_non_optimal as main3x3

# first successful solve on this state! ((6, 7, 1, 5, 2, 4, 3, 0), (2, 2, 2, 2, 2, 1, 1, 0), (5, 0, 4, 4, 1, 2, 3, 1, 0, 3, 2, 4, 3, 5, 0, 5, 0, 3, 1, 5, 1, 4, 2, 2), (21, 22, 20, 4, 9, 0, 5, 12, 18, 6, 16, 1, 14, 11, 2, 10, 8, 23, 3, 13, 7, 19, 15, 17))
# wings as seen on 2nd from right, top, and front starting with top clr then front clr
# x = 3x3 edge number; y = 4x4 wing number; z = int(not keysticker_on_top) y = 2x + z
# positions with white top green front

# wg = 0
# gw = 1
# wo = 2
# ow = 3
# wb = 4
# bw = 5
# wr = 6
# rw = 7
# go = 8
# og = 9
# gr = 10
# rg = 11
# bo = 12
# ob = 13
# br = 14
# rb = 15
# yg = 16
# gy = 17
# yo = 18
# oy = 19
# yb = 20
# by = 21
# yr = 22
# ry = 23

#order of centers: FUBDLR/GWBYOR; centers go clockwise starting from DL
# G = 0 = 0
# W = x' = 1
# B = y2 = 2
# Y = x = 3
# O = y' = 4
# R = y = 5

from _4x4_constants import * # Constants

def perform_move(move, state):
    move_info = ALL_VALID_MOVES[move]
    new_state = [list(x) for x in state]
    for fidx, (sect_move, sect_given) in enumerate(zip(move_info, state)):
        if fidx == 0:
            for idx, oth_corner in enumerate(sect_move):
                new_state[fidx][idx] = sect_given[oth_corner]
                new_state[1][idx] = (state[1][oth_corner] + move_info[1][idx]) % 3 if state[1][oth_corner] != "" else ""
        elif fidx == 2:
            for idx, cent_idx in enumerate(sect_move):
                new_state[2][idx] = sect_given[cent_idx]
        elif fidx == 3:
            for idx, move_wing in enumerate(sect_move):
                new_state[3][idx] = sect_given[move_wing]
    return tuple(tuple(x) for x in new_state)

def perform_full_rotation(arg_rotation, state):
    rotation = [arg_rotation[0], arg_rotation[-1]]
    if rotation[1] == rotation[0]:
        rotation[1] = 1
    else:
        rotation[1] = END_CHARACTERS.index(rotation[1]) + 1
    new_state = state
    the_dict = {"z": ("b", "Fw", "B'"), "x": ("l", "Rw", "L'"), "y": ("d", "Uw", "4'")}
    for _ in range(rotation[1]):
        for move in the_dict[rotation[0]]:
            new_state = perform_move(move, new_state)
    return new_state

def perform_center_rotation(rotation, state):
    start = state
    new = list(start) 
    move = ROTATION_MOVES[rotation]
    for idx, num in enumerate(move):
        new[idx] = start[num]
    return tuple(new)

def gen_rndm_state():
    state = [list(x) for x in SOLVED]
    moves = []
    ending_moves = [], []
    while len(Simplify(moves).simplify()) < 20:
        moves.append(random.choice(OUTER_MOVES))
        state = perform_move(moves[-1], state)
    moves = Simplify(moves).simplify()
    while len(Simplify(ending_moves[0]).simplify()) < 19 or len(Simplify(ending_moves[1]).simplify()) < 14:
        if len(Simplify(ending_moves[0]).simplify()) < 19:
            ending_moves[0].append(random.choice(WIDE_MOVES))
        else:
            ending_moves[1].append(random.choice(OUTER_MOVES))
    ending_moves = list(Simplify(ending_moves[0] + ending_moves[1]).simplify())
    random.shuffle(ending_moves)
    ending_moves = Simplify(ending_moves).simplify()
    moves = Simplify(moves + tuple(ending_moves)).simplify()
    for move in ending_moves:
        state = perform_move(move, state)
    return tuple(tuple(x) for x in state), tuple(moves)

def reduce_state(given, end, return_type=tuple):
    """Only works with whole centers"""
    returnable = [list(x) for x in given]
    for corner in end[0]:
        if corner != "":
            returnable[0][given[0].index(corner)] = str(corner)
    for piece, orientation in zip(end[0], end[1]):
        if orientation != "":
            returnable[1][given[1].index(piece)] = str(orientation)
    for center in end[2]:
        if center != "": # must be the whole center
            returnable[2][returnable[2].index(center)] = str(center)
    for edge in end[3]:
        if edge != "":
            returnable[3][given[3].index(edge)] = str(edge)
    for fidx, tup in enumerate(returnable):
        for idx, obj in enumerate(tup):
            returnable[fidx][idx] = int(obj) if isinstance(obj, str) else ""
    return return_type(return_type(x) for x in returnable)

def invert(moves, return_type=tuple):
    new_moves = []
    for move in moves:
        if move.endswith("2"):
            new_moves.append(move)
        elif move.endswith("'"):
            new_moves.append(move[:-1])
        else:
            new_moves.append(move + "'")
    return return_type(reversed(new_moves))

def simplify_rotations(rotations):
    state = tuple(range(6))
    solved = state
    end_rotations = []
    for rotation in rotations:
        state = perform_center_rotation(rotation, state)
    for rotation in ROTATION_MOVES: # keys
        after_state = perform_center_rotation(rotation, solved)
        if after_state[0] == state[0]: # if not ""
            end_rotations.append(rotation)
            phase1 = after_state
            break
    if state == after_state:
        returnable = tuple(x for x in end_rotations if x)
    for rotation in ("z", "z2", "z'"):
        after_state = perform_center_rotation(rotation, phase1)
        if after_state == state:
            returnable = tuple(x for x in (end_rotations + [rotation]) if x)
    if returnable == ("x2", "z2"):
        return ("y2",) # one exception where this function doesn't work
    if len(returnable) < len(rotations):
        return returnable
    return tuple(x for x in rotations if x)

def convert_4x4_to_3x3(state):
    corners = tuple(tuple(x) for x in state[:2])
    edges = ([], [])
    for idx, wing in enumerate(state[3][::2]):
        idx *= 2
        paired_wing = state[3][idx + 1]
        edges[0].append(wing // 2)
        edges[1].append(int(wing > paired_wing))
    edges = tuple(tuple(x) for x in edges)
    return (edges[0],) + (corners[0],) + (edges[1],) + (corners[1],)

def convert_d(moves, only_phase2=False):
    rotations = 0
    if not only_phase2:
        phase1 = []
        for move in moves:
            if move == "D":
                rotations = (rotations + 3) % 4
                phase1.append("D")
            elif move == "D2":
                rotations = (rotations + 2) % 4
                phase1.append(move)
            elif move == "D'":
                rotations = (rotations + 1) % 4
                phase1.append(move)
            elif move == "U":
                phase1.append("U")
            elif "U" in move:
                phase1.append("U" + move[1:])
            elif len(move) == 1:
                phase1.append(ROTATION_DICT["y"][0][(ROTATION_DICT["y"][0].index(move) + rotations) % 4])
            else:
                phase1.append(ROTATION_DICT["y"][0][(ROTATION_DICT["y"][0].index(move[0]) + rotations) % 4] + move[1:])
    else:
        phase1 = list(moves)
    phase2 = []
    phase2_rotations = ["y" + END_CHARACTERS[rotations - 1]] if rotations else []
    move_rotation = {"L": "x", "B": "z", "D": "y"}
    opp_dict = {"L": "R", "B": "F", "D": "U"}
    for idx in range(len(phase1)):
        move = phase1[idx]
        if "Lw" in move or "Bw" in move or "Dw" in move:
            if len(move) == 2:
                phase2.append(opp_dict[move[0]] + "w")
                phase2_rotations.append(move_rotation[move[0]])
                phase1 = single_rotate(phase1, ROTATION_DICT[phase2_rotations[-1]])
            elif move[-1] == "'":
                phase2.append(opp_dict[move[0]] + "w'")
                phase2_rotations.append(move_rotation[move[0]] + "'")
                phase1 = single_rotate(phase1, ROTATION_DICT[phase2_rotations[-1]])
            else:
                phase2.append(opp_dict[move[0]] + "w2")
                phase2_rotations.append(move_rotation[move[0]] + "2")
                phase1 = single_rotate(phase1, ROTATION_DICT[phase2_rotations[-1][0]])
                phase1 = single_rotate(phase1, ROTATION_DICT[phase2_rotations[-1][0]]) # can't do double rotations, did 2 single rotations
        else:
            phase2.append(move)
    phase2_rotations = invert(phase2_rotations)
    return phase2, simplify_rotations(phase2_rotations)

def rotate(moves, rotations, convert_4s=False):
    new_moves = list(moves)
    for idx, move in enumerate(new_moves):
        if "4" in move:
            new_moves[idx] = "D" + ("" if move == "4" else move[1:])
    single_rotations = []
    for rotation in rotations:
        if rotation in ROTATION_DICT:
            single_rotations.append(ROTATION_DICT[rotation])
        else:
            single_rotations.append(ROTATION_DICT[rotation[0]])
            single_rotations.append(ROTATION_DICT[rotation[0]])
    for rotation in single_rotations:
        new_moves = single_rotate(new_moves, rotation)
    return tuple((x if "D" not in x else ("4" if x == "D" else "4" + x[1:])) for x in new_moves) if convert_4s else tuple(new_moves)

def single_rotate(moves, rot_tup: tuple[str, str], return_type=tuple):
    new_moves = []
    rot_str, unused = rot_tup
    for move in moves:
        if move[0] in unused:
            new_moves.append(move)
        elif len(move) == 1:
            new_moves.append(rot_str[(rot_str.index(move) + 1) % 4])
        else:
            new_moves.append(rot_str[(rot_str.index(move[0]) + 1) % 4] + move[1:])
    return return_type(new_moves)

def better_gpe(state):
    """Return 3x3 edge locations"""
    pairs = []
    for idx, wing in enumerate(state[3][:-1:2], 1):
        idx = idx * 2 - 1
        if (wing + 1 == state[3][idx] and wing % 2 == 0) or (state[3][idx] + 1 == wing and wing % 2 == 1):
            pairs.append(idx // 2)
    return tuple(pairs)

def rotate_wings(state, rotations, doing_3x3):
    wings = tuple(state[0 if doing_3x3 else 3])
    rot_to_move = {"z": ("F", "B'"), "y": ("U", ("4'" if not doing_3x3 else "D'")), "x": ("R", "L'")}
    for rotation in [x for x in rotations if x != ""]:
        mag = 1 if len(rotation) == 1 else END_CHARACTERS.index(rotation[-1]) + 1
        rotation = rotation[0]
        for _ in range(mag):
            if doing_3x3:
                wings = main3x3.perform_move(main3x3.unconvert((rot_to_move[rotation][0],))[0], main3x3.perform_move(main3x3.unconvert((rot_to_move[rotation][1],))[0], (wings,) + main3x3.TUP_SOLVED[1:]))[0]
            else:
                wings = perform_move(rot_to_move[rotation][0], perform_move(rot_to_move[rotation][1], SOLVED[:3] + (wings,)))[3]
            new_wings = list(wings)
            for idx, info in enumerate(WING_ROTATION[rotation]):
                if idx == 1 and doing_3x3:
                    continue
                if doing_3x3:
                    info = tuple(x // 2 for x in info)
                for _idx, num in enumerate(info):
                    new_wings[num] = wings[info[_idx - 3]]
            wings = new_wings
    return tuple(new_wings)

def rotation_list(input_moves, return_type=tuple):
    """Convert moves with rotations to moves then rotations"""
    rotations = []
    for move in input_moves:
        if any([x in move for x in "xyz"]):
            rotations.append(move)
    rotations = simplify_rotations(rotations)
    rotation_collection = [[]]
    moves = list(input_moves)
    for move in moves:
        if any([x in move for x in "xyz"]):
            rotation_collection[-1].append(move)
        elif rotation_collection[-1]:
            rotation_collection.append([])
    rotation_collection = tuple(invert(x) for x in rotation_collection)
    counter = 0
    just_saw = False
    for idx, move in enumerate(moves):
        if any([x in move for x in "xyz"]) and not just_saw:
            moves[idx] = rotation_collection[counter]
            just_saw = True
            counter += 1
        elif any([x in move for x in "xyz"]):
            moves[idx] = None
        else:
            just_saw = False
    temp = moves
    moves = []
    for thing in temp:
        if isinstance(thing, str):
            moves.append(thing)
        elif not (thing is None):
            moves += list(reversed(thing))
    while True:
        if not [x for x in moves if any([y in x for y in "xyz"])]: # if no rotations left
            break
        length = len(moves)
        for idx, move in enumerate(reversed(moves)):
            if any([x in move for x in "xyz"]):
                moves[length-idx-1:] = rotate(moves[length-idx:], (move,))
                break
    moves, converted_rotations = convert_d(moves, True)
    rotations = simplify_rotations(converted_rotations + rotations)
    return return_type((return_type(moves), return_type(rotations)))

def pair_edges(state):
    moves = []
    buff_repl = (5, 4)
    slice_edges = (5,4,6,7)
    local_state = state
    while True:
        paired = better_gpe(local_state)
        need_pairing = tuple((set(range(12)) - set(paired)) - set(slice_edges))
        if not need_pairing:
            break
        if 4 in paired:
            new_wing_state = SOLVED[:3] + (rotate_wings(local_state, ("y'",), False),)
            replacement = tuple((set(range(12)) - set(better_gpe(new_wing_state))) - set(slice_edges))[0]
            moves += rotate(EDGE_REPLACEMENT[replacement][0], ("y",), True)
            for move in rotate(EDGE_REPLACEMENT[replacement][0], ("y",), True):
                local_state = perform_move(move, local_state)
            continue
        refer_wings = local_state[3][buff_repl[1]*2:(buff_repl[1]*2)+2]
        opp_wing_twins = tuple((x - 1 if x % 2 == 1 else x + 1) for x in refer_wings)
        hidden_wing_twins = []
        for edge in slice_edges[2:]:
            edge = (edge * 2, (edge * 2) + 1)
            for wing in [local_state[3][x] for x in edge]:
                if wing in opp_wing_twins:
                    hidden_wing_twins.append((wing, edge[0]//2))
        if len(hidden_wing_twins) == 2:
            solved_location = hidden_wing_twins[0][1]
            repl_location = need_pairing[0]
            needed_rotations = simplify_rotations(tuple(x for x in BUFFER_ROTATIONS[0][solved_location] + BUFFER_ROTATIONS[1]["E"] if x != ""))
            repl_location = rotate_wings(main3x3.TUP_SOLVED, needed_rotations, True).index(repl_location)
            moves += list(rotate(EDGE_REPLACEMENT[repl_location][0], invert(needed_rotations), True))
            for move in rotate(EDGE_REPLACEMENT[repl_location][0], invert(needed_rotations), True):
                local_state = perform_move(move, local_state)
            continue
        will_solve_wing = tuple(set(opp_wing_twins) - set([x[0] for x in hidden_wing_twins]))[0]
        will_solve_location = local_state[3].index(will_solve_wing) // 2
        local_state = [local_state, local_state]
        for move in EDGE_REPLACEMENT[will_solve_location][0]:
            local_state[1] = perform_move(move, local_state[1])
        wing_mod = local_state[1][3].index(will_solve_wing) % 2
        if wing_mod == refer_wings.index(will_solve_wing + (-1 if will_solve_wing % 2 else 1)):
            moves += list(EDGE_REPLACEMENT[will_solve_location][0])
            local_state = local_state[1]
        else:
            wing_mod = (wing_mod + 1) % 2
            moves += list(EDGE_REPLACEMENT[will_solve_location][1])
            local_state = local_state[0]
            for move in EDGE_REPLACEMENT[will_solve_location][1]:
                local_state = perform_move(move, local_state)
        moves.append("Uw" + ("'" if wing_mod else ""))
        local_state = perform_move(moves[-1], local_state)
        if moves[-1] == "Uw":
            moves.append("y'")
            local_state = list(local_state)
            local_state[3] = rotate_wings(local_state, ("y'",), False)
            local_state = tuple(local_state)
    placeholders = []
    rotation_locations = []
    for idx, move in enumerate(moves):
        if "Uw" in move:
            placeholders.append((idx, False if "'" in move else True))
            moves[idx] = "F"
        if "y" in move:
            rotation_locations.append(idx)
    rotation = 0
    for move in moves:
        if move == "y":
            rotation += 1
        elif "y" in move:
            rotation += END_CHARACTERS.index(move[-1]) + 1
    rotation %= 4
    if rotation != 0:
        rotation = "y" + END_CHARACTERS[rotation - 1]
    moves = rotation_list(moves, list)[0]
    for holder in placeholders:
        ys_passed = 0
        for rot_loc in rotation_locations:
            if holder[0] > rot_loc:
                ys_passed += 1
            else:
                break
        moves[holder[0] - ys_passed] = "Uw" + ("" if holder[1] else "'")
    if local_state[2] != SOLVED[2]:
        for move in ("Uw", "Uw2", "Uw'"):
            if perform_move(move, local_state)[2] == SOLVED[2]:
                moves.append(move)
                local_state = perform_move(move, local_state)
    moves = list(Simplify([("D" if move == "4" else "D" + move[1]) if "4" in move else move for move in moves]).simplify())
    if rotation:
        local_state = list(local_state)
        local_state[3] = rotate_wings(local_state, invert((rotation,)), False)
        local_state = tuple(local_state)
    last_2_edges_alg = ("Uw'", "F'", "R", "U'", "F", "R'", "Uw")
    flip_alg = EDGE_REPLACEMENT[5][1]
    while True:
        paired = tuple(x for x in better_gpe(local_state) if x in {4,5,6,7})
        not_paired = tuple({4,5,6,7} - set(paired))
        setup = []
        if not not_paired:
            break
        if set(not_paired) == {7, 6}:
            setup = ["R2", "L2"]
            will_pair_with = local_state[3][14] - (1 if local_state[3][14] % 2 else -1)
            correct_ori = local_state[3].index(will_pair_with) % 2
        elif 4 in not_paired:
            will_pair_with = local_state[3][8] - (1 if local_state[3][8] % 2 else -1)
            location = local_state[3].index(will_pair_with) // 2
            correct_ori = local_state[3].index(will_pair_with) % 2
            setup = list(LAST_2_EDGE_MOVES[0][location])
        else:
            will_pair_with = local_state[3][10] - (1 if local_state[3][10] % 2 else -1)
            location = local_state[3].index(will_pair_with) // 2
            correct_ori = local_state[3].index(will_pair_with) % 2
            setup = list(LAST_2_EDGE_MOVES[1][location])
        if not correct_ori:
            setup += list(flip_alg)
        for move in setup:
            local_state = perform_move(move, local_state)
        for move in last_2_edges_alg:
            local_state = perform_move(move, local_state)
        moves += setup + list(last_2_edges_alg)
    local_state = state
    for move in moves:
        if move == "D":
            move = "4"
        elif "D" in move:
            move = "4" + move[1]
        local_state = perform_move(move, local_state)
    return tuple(moves), local_state

def brute_force(start, end, usable_moves=VALID_MOVES, want_end_state=True):
    reduced = reduce_state(start, end)
    dict_start = {reduced: (None,)}
    list_start = [(reduced,)]
    dict_end = {end: (None,)}
    list_end = [(end,)]
    done = False
    depth = 1
    while True:
        for state in list_start[-1]:
            if state in dict_end:
                done = True
                common_state = state
                break
        if done:
            break
        list_start.append([])
        depth += 1
        for state in list_start[-2]:
            for move in [x for x in usable_moves if x not in DICT_INTERSECTING_MOVES[dict_start[state][-1]]]:
                new_state = perform_move(move, state)
                if new_state in dict_start:
                    continue
                dict_start[new_state] = dict_start[state] + (move,)
                list_start[-1].append(new_state)
        for state in list_start[-1]:
            if state in dict_end:
                done = True
                common_state = state
                break
        if done:
            break
        list_end.append([])
        depth += 1
        for state in list_end[-2]:
            for move in [x for x in usable_moves if x not in DICT_INTERSECTING_MOVES[dict_end[state][-1]]]:
                new_state = perform_move(move, state)
                if new_state in dict_end:
                    continue
                dict_end[new_state] = dict_end[state] + (move,)
                list_end[-1].append(new_state)
    moves = dict_start[common_state][1:] + invert(dict_end[common_state][1:])
    if not want_end_state:
        return moves
    end_state = start
    for move in moves:
        end_state = perform_move(move, end_state)
    return moves, end_state

class Simplify:

    parallels = {"L": {"R", "Rw"}, "F": {"Fw", "B"}, "R": {"Rw", "L"}, "B": {"F", "Fw"},
                 "U": {"Uw", "D"}, "D": {"Uw", "U"},"Fw": {"B", "F"}, "Rw": {"R", "L"}, "Uw": {"U", "D"}}
    
    def __init__(self, moves):
        self.moves = moves

    def simplify(self):
        return Simplify(self.phase1()).phase2()

    def convert_moves(self, start, converted_moves=None) -> list:
        if start:
            new_moves = []
            for move in self.moves:
                if ("w" in move and len(move) == 2) or len(move) == 1:
                    new_moves.append((move, 1))
                else:
                    new_moves.append((move[:-1], 2 if move[-1] == "2" else 3))
            return new_moves
        return [x + END_CHARACTERS[y - 1] for x, y in converted_moves]

    def phase2(self, arg_new_moves="default arg"):
        new_moves = self.convert_moves(True) if arg_new_moves == "default arg" else Simplify(arg_new_moves).convert_moves(True)
        if not new_moves:
            return ()
        groups = [[new_moves[0]]]
        done_all = True
        for move in new_moves[1:]:
            if groups[-1][-1][0] in Simplify.parallels[move[0]]: # could be self.parallels but variable belongs to class
                groups[-1].append(move)
            else:
                groups[-1] = tuple(groups[-1])
                groups.append([move])
        groups[-1] = tuple(groups[-1])
        simplified_groups = []
        for group in groups:
            if len(group) < 3:
                simplified_groups.append(group)
                continue
            if len(group) == 3 and group[0][0] != group[1][0] != group[2][0] and group[0][0] != group[2][0]: # if first 3 elements are different and len == 3
                simplified_groups.append(group)
                continue
            done_all = False
            subgroups = [[group[0]]]
            for move in group[1:]:
                for idx, subgroup in enumerate(subgroups):
                    if move[0] == subgroup[0][0]:
                        break
                else:
                    subgroups.append([move])
                    continue
                subgroups[idx].append(move)
            for subgroup in subgroups:
                subgroup = Simplify(subgroup).phase1(True)
            simplified_groups.append(tuple(sum(subgroups, [])))
        if done_all:
            return tuple(Simplify.convert_moves(None, False, sum([x for x in simplified_groups if x != ()], ()))) # Final return statement
        new_moves = tuple(Simplify(Simplify.convert_moves(None, False, sum([x for x in simplified_groups if x != ()], ()))).phase1())
        return Simplify.phase2(None, new_moves)
    
    def phase1(self, converted=False):
        new_moves = self.moves if converted else self.convert_moves(True)
        idx = 0
        while True:
            if len(new_moves) <= idx + 1:
                break
            for move in new_moves[idx:-1]:
                if move[0] == new_moves[idx + 1][0]:
                    new_moves[idx + 1] = (move[0], (move[1] + new_moves[idx + 1][1]) % 4)
                    del new_moves[idx]
                    break
                else:
                    idx += 1
            if new_moves[idx][1] == 0: # indeces drop by 1
                del new_moves[idx]
                idx -= 1 if idx else 0
        return Simplify.convert_moves(None, False, new_moves)

def get_centers(state, test_mode):
    if not test_mode:
        print("Centers 0/4 done", end="\r")
    orig_time = perf_counter()
    num_0 = brute_force(state, END_STATES[0])
    if not test_mode:
        print("Centers 1/4 done", end="\r")
    num_1 = brute_force(num_0[1], END_STATES[1])
    if not test_mode:
        print("Centers 2/4 done", end="\r")
    num_2 = brute_force(num_1[1], END_STATES[2])
    if not test_mode:
        print("Centers 3/4 done", end="\r")
    num_3 = brute_force(num_2[1], END_STATES[3])
    end_time = perf_counter()
    simplified = Simplify(sum((x[0] for x in (num_0, num_1, num_2, num_3)), ())).simplify()
    simplified, rotations = convert_d(simplified)
    if not test_mode:
        print(f"Centers complete in {round(end_time - orig_time, 3)} seconds in {len(simplified)} moves")
    return tuple(simplified), rotations, num_3[1]

def avg(arg):
    return sum(arg) / len(arg)

def test(limit_or_state):
    if isinstance(limit_or_state, (tuple, list)):
        try:
            global_moves, after_rots = main(limit_or_state, True)
        except BaseException as e:
            if type(e) != KeyboardInterrupt:
                print(f"Unable to complete, exception was raised: {e}")
        new_state = limit_or_state
        for move in global_moves:
            if move == "D":
                new_state = perform_move("4", new_state)
            elif "D" in move:
                new_state = perform_move("4" + move[1], new_state)
            else:
                new_state = perform_move(move, new_state)
        for rotation in after_rots:
            new_state = perform_full_rotation(rotation, new_state)
        return new_state
    counter = 0
    dont_work = []
    times = []
    moves_list = []
    rotations = []
    skip = False
    while True:
        string_input = 'Type "E" to exit or "V" to view failed states: '
        if not skip:
            test_state, moves = gen_rndm_state()
        else:
            skip = False
        orig_time = perf_counter()
        try:
            global_moves, after_rots = main(test_state, True)
        except BaseException as e:
            if type(e) != KeyboardInterrupt:
                dont_work.append((test_state, moves, e))
                counter += 1
                print(f"{len(dont_work)}/{counter} states have failed to solve. Raise KeyboardInterrupt to view failed states or exit program. Avg move count: {round(avg(moves_list), 3)}; Avg rotations: {round(avg(rotations), 3)}; Avg computing time: {round(avg(times), 3)} seconds")
                continue
            else:
                while True:
                    given = input(string_input).lower()
                    if given == "e":
                        sys.exit()
                    if given == "v":
                        print(dont_work)
                        break
                    else:
                        string_input = f'Sorry, "{given}" is not a valid input. Please type "E" to exit or "V" to view failed states: '
                skip = True
                continue
        end_time = perf_counter()
        times.append(round(end_time - orig_time, 3))
        moves_list.append(len(global_moves))
        rotations.append(len(after_rots))
        new_state = test_state
        for move in global_moves:
            if move == "D":
                new_state = perform_move("4", new_state)
            elif "D" in move:
                new_state = perform_move("4" + move[1], new_state)
            else:
                new_state = perform_move(move, new_state)
        for rotation in after_rots:
            new_state = perform_full_rotation(rotation, new_state)
        counter += 1
        if new_state != SOLVED:
            dont_work.append((test_state, moves))
        print(f"{len(dont_work)}/{counter} states have failed to solve. Raise KeyboardInterrupt to view failed states or exit program. Avg move count: {round(avg(moves_list), 3)}; Avg rotations: {round(avg(rotations), 3)}; Avg computing time: {round(avg(times), 3)} seconds")
        if (not limit_or_state is None) and counter >= limit_or_state:
            break
    return dont_work

def query_state(asking_or_state=True, return_state=False):
    corner_oris = []
    corner_poses = []
    counter = 0
    if not asking_or_state is True:
        state = asking_or_state
        asking = False
    else:
        asking = True
    while counter < (8 if return_state else 7):
        if asking:
            given = input(f"Corner {counter + 1} colors: ").upper()
        else:
            given = state[0][counter]
        if len(given) != 3:
            if asking:
                print("Invalid input")
            if return_state:
                return 0
            continue
        arrangements = given, given[1:] + given[0], given[2] + given[:2]
        if not any((x in CORNER_COLORS for x in arrangements)):
            if asking:
                print("Invalid input")
            if return_state:
                return "Corner doesn't exist"
            continue
        if any((any(arrangement in CORNER_COLORS[y] for y in corner_poses) for arrangement in arrangements)):
            if asking:
                print("Corner already given")
            if return_state:
                return "Duplicate corners"
            continue
        corner_poses.append(CORNER_COLORS.index(arrangements[[x in CORNER_COLORS for x in arrangements].index(True)]))
        corner_oris.append((0, 2, 1)[given.index("W" if "W" in given else "Y")])
        counter += 1
    if return_state:
        if sum(corner_oris) % 3:
            return "Twisted corner"
    else:
        corner_poses.append([x for x in range(8) if x not in corner_poses][0])
        corner_oris.append((3 - sum(corner_oris)) % 3)
    counter = 0
    wings = []
    flipped = tuple(range(1, 24, 2))
    while counter < (24 if return_state else 23):
        if asking:
            given = input(f"Wing {counter + 1} colors: ").upper()
        else:
            given = state[1][counter]
        if (len(given) != 2 or given not in WING_COLORS):
            if asking:
                print("Invalid input")
            if return_state:
                return "Edge doesn't exist"
            continue
        if counter in flipped:
            given = given[::-1]
        if WING_COLORS.index(given) in wings:
            if asking:
                print("Wing already given")
            if return_state:
                return "Duplicate edge"
            continue
        wings.append(WING_COLORS.index(given))
        counter += 1
    if not return_state:
        wings.append([x for x in range(24) if x not in wings][0])
    counter = 0
    centers = []
    center_dict = {x:0 for x in CENTER_COLORS}
    while True:
        if asking:
            given = input(f"Center {counter + 1} color: ").upper()
        else:
            given = state[2][counter]
        if (given not in CENTER_COLORS or len(given) != 1):
            if asking:
                print("Invalid input")
            if return_state:
                return "XXX"
            continue
        if center_dict[given] == 4:
            if asking:
                print(f"Too many {COLOR_NAMES[given].lower()} centers")
            if return_state:
                return "Invalid centers"
            continue
        centers.append(CENTER_COLORS.index(given))
        center_dict[given] = center_dict[given] + 1
        counter += 1
        if len([x for x in center_dict if center_dict[x] == 4]) == 5 and not return_state:
            excluded = CENTER_COLORS.index([x for x in center_dict if center_dict[x] != 4][0])
            while len(centers) < 24:
                centers.append(excluded)
            print()
            main(tuple(tuple(x) for x in (corner_poses, corner_oris, centers, wings)))
            return
        if return_state and len(centers) == 24:
            return tuple(tuple(x) for x in (corner_poses, corner_oris, centers, wings))

def main(state, test_mode=False):
    center_moves, center_rotations, end_state = get_centers(state, test_mode)
    center_rotations = tuple(x for x in center_rotations if x)
    edge_moves, end_state = pair_edges(end_state)
    _3x3_state = convert_4x4_to_3x3(end_state)
    parity_info = main3x3.is_valid_state(_3x3_state, False, True)
    parity_moves = PARITIES[parity_info[0] * 2 + parity_info[1]]
    _3x3_state = end_state
    for move in parity_moves:
        _3x3_state = perform_move(move, _3x3_state)
    _3x3_state = convert_4x4_to_3x3(_3x3_state)
    orig_time = perf_counter()
    if not test_mode:
        print(f"Edges complete in {len(edge_moves)} moves")
        print(PARITY_MESSAGES[parity_moves])
        print("Solving 3x3 stage...", end="\r")
    _3x3_moves = vis3x3.print_kociemba(_3x3_state, _4x4_mode=True)
    end_time = perf_counter()
    if not test_mode:
        print(f"Solved 3x3 stage in {round(end_time - orig_time, 3)} seconds in {len(_3x3_moves)} moves\n")
    moves = center_moves + center_rotations + edge_moves + parity_moves + tuple(_3x3_moves)
    moves, after_rotations = rotation_list(moves)
    simplified = Simplify(moves).simplify()
    if not test_mode:
        print(" ".join(simplified) + " " + " ".join(after_rotations))
        print(str(len(simplified)) + " moves")
    return simplified, after_rotations

if __name__ == '__main__':
    test(None)
