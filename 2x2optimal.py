# 2x2 rubik's cube solver in the least moves possible

import time
from random import randint
import os

def R(pos, ori):
    new_ori = [None] * 8
    new_pos = [None] * 8
    for idx, piece in enumerate(pos):
        new_pos[Rpos[idx]] = piece
    for idx, orientation in enumerate(ori):
        new_ori[Rpos[idx]] = (orientation + Rori[Rpos[idx]]) % 3
    return [new_pos, new_ori]


def Rp(pos, ori):
    new_ori = [None] * 8
    new_pos = [None] * 8
    for idx, piece in enumerate(pos):
        new_pos[Rppos[idx]] = piece
    for idx, orientation in enumerate(ori):
        new_ori[Rppos[idx]] = (orientation + Rpori[Rppos[idx]]) % 3
    return [new_pos, new_ori]


def R2(pos, ori):
    new_ori = [None] * 8
    new_pos = [None] * 8
    for idx, piece in enumerate(pos):
        new_pos[R2pos[idx]] = piece
    for idx, orientation in enumerate(ori):
        new_ori[R2pos[idx]] = (orientation + R2ori[R2pos[idx]]) % 3
    return [new_pos, new_ori]


def F(pos, ori):
    new_ori = [None] * 8
    new_pos = [None] * 8
    for idx, piece in enumerate(pos):
        new_pos[Fpos[idx]] = piece
    for idx, orientation in enumerate(ori):
        new_ori[Fpos[idx]] = (orientation + Fori[Fpos[idx]]) % 3
    return [new_pos, new_ori]


def Fp(pos, ori):
    new_ori = [None] * 8
    new_pos = [None] * 8
    for idx, piece in enumerate(pos):
        new_pos[Fppos[idx]] = piece
    for idx, orientation in enumerate(ori):
        new_ori[Fppos[idx]] = (orientation + Fpori[Fppos[idx]]) % 3
    return [new_pos, new_ori]


def F2(pos, ori):
    new_ori = [None] * 8
    new_pos = [None] * 8
    for idx, piece in enumerate(pos):
        new_pos[F2pos[idx]] = piece
    for idx, orientation in enumerate(ori):
        new_ori[F2pos[idx]] = (orientation + F2ori[F2pos[idx]]) % 3
    return [new_pos, new_ori]


def U(pos, ori):
    new_ori = [None] * 8
    new_pos = [None] * 8
    for idx, piece in enumerate(pos):
        new_pos[Upos[idx]] = piece
    for idx, orientation in enumerate(ori):
        new_ori[Upos[idx]] = (orientation + Uori[Upos[idx]]) % 3
    return [new_pos, new_ori]


def Up(pos, ori):
    new_ori = [None] * 8
    new_pos = [None] * 8
    for idx, piece in enumerate(pos):
        new_pos[Uppos[idx]] = piece
    for idx, orientation in enumerate(ori):
        new_ori[Uppos[idx]] = (orientation + Upori[Uppos[idx]]) % 3
    return [new_pos, new_ori]


def U2(pos, ori):
    new_ori = [None] * 8
    new_pos = [None] * 8
    for idx, piece in enumerate(pos):
        new_pos[U2pos[idx]] = piece
    for idx, orientation in enumerate(ori):
        new_ori[U2pos[idx]] = (orientation + U2ori[U2pos[idx]]) % 3
    return [new_pos, new_ori]


def iden_move(last_move, wanted_move):
    r_iden = ["R", "S", "T"]
    f_iden = ["F", "G", "H"]
    u_iden = ["U", "V", "W"]
    if wanted_move in r_iden:
        return last_move in r_iden
    elif wanted_move in f_iden:
        return last_move in f_iden
    elif wanted_move in u_iden:
        return last_move in u_iden
    else:
        print("Invalid wanted move")


def find_match(state, st_or_sv):
    global match_among_lists
    if st_or_sv == "st":
        if state in dictsolved:
            match_among_lists = True
    elif st_or_sv == "sv":
        if state in dictstart:
            match_among_lists = True
    else:
        return "Invalid list"


def look_from_start():
    for movenum in range(9):
        thing_to_add = move_funcs[movenum](
            start[start_index - 1][0], start[start_index - 1][1]
        )
        tup_thing = (tuple(thing_to_add[0]), tuple(thing_to_add[1]))
        if start_index != 1:
            if (
                not iden_move(
                    (moves_start[start_index - 1])[
                        len(moves_start[start_index - 1]) - 1
                    ],
                    valid_moves[movenum],
                )
                and not tup_thing in dictstart
            ):
                dictstart[tup_thing] = (
                    moves_start[start_index - 1] + valid_moves[movenum]
                )
                start.append(thing_to_add)
                moves_start.append(moves_start[start_index - 1] + valid_moves[movenum])
                find_match(tup_thing, "st")
        else:
            dictstart[tup_thing] = valid_moves[movenum]
            start.append(thing_to_add)
            moves_start.append(valid_moves[movenum])
            find_match(tup_thing, "st")


def look_from_solved():
    for movenum in range(9):
        thing_to_add = move_funcs[movenum](
            solved[start_index - 1][0], solved[start_index - 1][1]
        )
        tup_thing = (tuple(thing_to_add[0]), tuple(thing_to_add[1]))
        if start_index != 1:
            if (
                not iden_move(
                    (moves_solved[start_index - 1])[
                        len(moves_solved[start_index - 1]) - 1
                    ],
                    valid_moves[movenum],
                )
                and not tup_thing in dictsolved
            ):
                dictsolved[tup_thing] = (
                    moves_solved[start_index - 1] + valid_moves[movenum]
                )
                solved.append(thing_to_add)
                moves_solved.append(
                    moves_solved[start_index - 1] + valid_moves[movenum]
                )
                find_match(tup_thing, "sv")
        else:
            dictsolved[tup_thing] = valid_moves[movenum]
            solved.append(thing_to_add)
            moves_solved.append(valid_moves[movenum])
            find_match(tup_thing, "sv")


def find_moves(contained_list):
    global list_inverted_moves
    if contained_list == start:
        opp_list = solved
        move_list = moves_start
        opp_move = moves_solved
    else:
        opp_list = start
        move_list = moves_solved
        opp_move = moves_start
    min_idx = len(contained_list) - 9
    for idx, state in enumerate(contained_list[min_idx : min_idx + 9]):
        if state in opp_list:
            index_main = idx + min_idx
            index_opp = opp_list.index(state)
            break
    movesiv = []
    moves = []
    for char in move_list[index_main]:
        moves.append(char)
    inverted_moves = opp_move[index_opp]
    count = len(inverted_moves) - 1
    while count >= 0:
        moves.append(inversion_from_vm[valid_moves.index(inverted_moves[count])])
        count -= 1
    if contained_list == solved:
        for move in moves[::-1]:
            movesiv.append(inversion_from_vm[valid_moves.index(move)])
        moves = movesiv
    list_inverted_moves = invert(moves)
    moves = convert(moves)
    list_inverted_moves = convert(list_inverted_moves)
    return moves


def invert(moves):
    new = []
    for move in moves[::-1]:
        new.append(inversion_from_vm[valid_moves.index(move)])
    return new


def convert(moves):
    new = []
    for move in moves:
        new.append(conversion_from_vm[valid_moves.index(move)])
    return new


def main():
    depth = 0
    global generation
    global start_index
    global list_inverted_moves
    global start_time
    prev_lim = 1
    while not match_among_lists:
        list_in = start
        generation += 1
        depth += 1
        limit = len(moves_solved) + 1
        start_index = prev_lim
        while start_index < limit and not match_among_lists:
            look_from_start()
            start_index += 1
        if not match_among_lists:
            depth += 1
            list_in = solved
            start_index = prev_lim
            while start_index < limit and not match_among_lists:
                look_from_solved()
                start_index += 1
        if match_among_lists:
            return find_moves(list_in)
        prev_lim = limit


# ALL MOVES ARE INVERTED
Rppos = [0, 1, 3, 7, 4, 5, 2, 6]
Rpori = [0, 0, 2, 1, 0, 0, 1, 2]
Rpos = [0, 1, 6, 2, 4, 5, 7, 3]
Rori = [0, 0, 2, 1, 0, 0, 1, 2]
R2pos = [0, 1, 7, 6, 4, 5, 3, 2]
R2ori = [0, 0, 0, 0, 0, 0, 0, 0]

Fppos = [4, 1, 2, 0, 7, 5, 6, 3]
Fpori = [1, 0, 0, 2, 2, 0, 0, 1]
Fpos = [3, 1, 2, 7, 0, 5, 6, 4]
Fori = [1, 0, 0, 2, 2, 0, 0, 1]
F2pos = [7, 1, 2, 4, 3, 5, 6, 0]
F2ori = [0, 0, 0, 0, 0, 0, 0, 0]

Uppos = [3, 0, 1, 2, 4, 5, 6, 7]
Upori = [0, 0, 0, 0, 0, 0, 0, 0]
Upos = [1, 2, 3, 0, 4, 5, 6, 7]
Uori = [0, 0, 0, 0, 0, 0, 0, 0]
U2pos = [2, 3, 0, 1, 4, 5, 6, 7]
U2ori = [0, 0, 0, 0, 0, 0, 0, 0]

valid_moves = ["R", "S", "T", "F", "G", "H", "U", "V", "W"]
move_funcs = [R, Rp, R2, F, Fp, F2, U, Up, U2]
start_index = 0
inversion_from_vm = ["S", "R", "T", "G", "F", "H", "V", "U", "W"]
conversion_from_vm = ["R", "R'", "R2", "F", "F'", "F2", "U", "U'", "U2"]
generation = 0
match_among_lists = False
solved = [[[0, 1, 2, 3, 4, 5, 6, 7], [0, 0, 0, 0, 0, 0, 0, 0]]]
start = [[[6, 2, 3, 4, 7, 5, 1, 0], [2, 1, 1, 1, 2, 0, 0, 2]]]  # 11 move optimal


def questioning():
    print()
    print("0 = white green orange")
    print("1 = white orange blue")
    print("2 = white blue red")
    print("3 = white red green")
    print("4 = yellow orange green")
    print("5 = yellow blue orange (control)")
    print("6 = yellow red blue")
    print("7 = yellow green red")
    print()
    print(
        "The yellow blue orange corner must be in the back bottom left with yellow facing down".upper()
    )
    print()
    input_positions = []
    asked_questions_pos = [
        "What piece is in the front top left?: ",
        "What piece is in the back top left?: ",
        "What piece is in the back top right?: ",
        "What piece is in the front top right?: ",
        "What piece is in the front bottom left?: ",
        "What piece is in the back bottom left?: ",
        "What piece is in the back bottom right?: ",
        "What piece is in the front bottom right?: ",
    ]
    asked_questions_ori = [
        "How many clockwise corner twists are needed on the front top left to have yellow or white facing up?: ",
        "How many clockwise corner twists are needed on the back top left to have yellow or white facing up?: ",
        "How many clockwise corner twists are needed on the back top right to have yellow or white facing up?: ",
        "How many clockwise corner twists are needed on the front top right to have yellow or white facing up?: ",
        "How many clockwise corner twists are needed on the front bottom left to have yellow or white facing down?: ",
        "How many clockwise corner twists are needed on the back bottom left to have yellow or white facing down?: ",
        "How many clockwise corner twists are needed on the back bottom right to have yellow or white facing down?: ",
        "How many clockwise corner twists are needed on the front bottom right to have yellow or white facing down?: ",
    ]
    for num in range(8):
        valid_input = False
        while not valid_input:
            previous_input = int(input(asked_questions_pos[num]))
            if not previous_input in input_positions:
                if previous_input in range(8):
                    if (previous_input == 5 and num == 5) or (
                        previous_input != 5 and num != 5
                    ):
                        input_positions.append(previous_input)
                        valid_input = True
                    else:
                        print()
                        print(
                            "Yellow blue orange corner must be in back bottom left with yellow facing down! Restart if misplaced."
                        )
                        print()
                else:
                    print()
                    print("Number not between 0 and 7")
                    print()
            else:
                print()
                print("Can't have two of the same piece!")
                print()

    print()
    print("0 = White or yellow already facing up or down")
    print(
        "1 = One clockwise corner twist needed to make white or yellow facing up or down"
    )
    print(
        "2 = Two clockwise corner twists needed to make white or yellow facing up or down"
    )
    print()
    input_orientations = []
    for num in range(8):
        valid_input = False
        while not valid_input:
            previous_input = int(input(asked_questions_ori[num]))
            if previous_input in range(3):
                if num != 5 or previous_input == 0:
                    input_orientations.append(previous_input)
                    valid_input = True
                    if num == 7 and not (sum(input_orientations) % 3 == 0):
                        valid_input = False
                        mod_sum = sum(input_orientations) % 3
                        while not valid_input:
                            print()
                            print(input_orientations)
                            previous_input = int(
                                input(
                                    "The sum of all orientations must be divisible by three. Check your inputs and see if there is a mistake. When you find it, enter the mistaken index (starting from 0!): "
                                )
                            )
                            if not previous_input in range(8):
                                print()
                                print("Input not between 0 and 7 (start from 0!)")
                                print()
                            elif previous_input != 5:
                                input_orientations[previous_input] = (
                                    3 - mod_sum + input_orientations[previous_input]
                                ) % 3
                                valid_input = True
                            else:
                                print()
                                print("Yellow blue orange MUST have yellow facing down")

                else:
                    print()
                    print(
                        "Yellow blue orange must have yellow facing down! Restart if misplaced."
                    )
                    print()
            else:
                print()
                print("Orientation must be between 0 and 2")
                print()
    return [input_positions, input_orientations], (
        tuple(input_positions),
        tuple(input_orientations),
    )


def write_to(states_searched, lens):
    os.chdir("/Users/owenreiss/Desktop/python/_file_ops")
    set_lens = set(lens)
    _2x2 = open("2x2_states", "w")
    print("started writing")
    n_orig_time = time.time()
    for idx, item in enumerate(states_searched.items()):
        state, moves_f_solved = item
        converted_f_solved = convert(moves_f_solved)
        if idx in set_lens:
            _2x2.write("\n")
            _2x2.write(f"All states above take less than {lens.index(idx) + 1} moves\n")
            _2x2.write("\n")
        _2x2.write(
            f"{state}  Solution: {' '.join(convert(invert(moves_f_solved)))}  Inverted solution: {' '.join(converted_f_solved)}\n"
        )
    _2x2.close()
    print(f"ended writing in {round((time.time() - n_orig_time) * 1000) / 1000} secs")
    return round((time.time() - n_orig_time) * 1000) / 1000


def god():
    write_md = (
        input(
            "write to 2x2_states in /Users/owenreiss/Desktop/python/_file_ops (write) (no)?: "
        ).lower()
        == "write"
    )
    print()
    print(f"writing: {write_md}")
    print()
    orig_time = time.time()
    print("1 state takes 0 moves after 0 secs + 0 secs from previous")
    lens = [1]
    gen_god = 0
    st_id_god = 0
    limit_god = 0
    prev_lim = 0
    states_searched = {(tuple(range(8)), (0, 0, 0, 0, 0, 0, 0, 0)): ""}
    moves = [""]
    states = [[list(range(8)), [0] * 8]]
    combos = 3674160
    while len(states_searched) < combos:
        prev_time = time.time()
        gen_god += 1
        limit_god = len(states_searched)
        st_id_god = prev_lim
        while st_id_god < limit_god and len(states_searched) != combos:
            to_print = False
            for movenum in range(9):
                new_state = move_funcs[movenum](
                    states[st_id_god][0], states[st_id_god][1]
                )
                tup_state = (tuple(new_state[0]), tuple(new_state[1]))
                if not tup_state in states_searched:
                    states_searched[tup_state] = moves[st_id_god] + valid_moves[movenum]
                    moves.append(moves[st_id_god] + valid_moves[movenum])
                    states.append(new_state)
                if len(states) % 10000 == 0:
                    to_print, length = True, len(states)
            st_id_god += 1
            if to_print:
                print(
                    "States searched:",
                    length,
                    "/ 3,674,160",
                    end="\r",
                )
        lens.append(len(states_searched))
        print(
            "%s states take %s moves after %s secs + %s secs from previous"
            % (
                lens[gen_god] - lens[gen_god - 1],
                gen_god,
                round((time.time() - orig_time) * 1000) / 1000,
                round((time.time() - prev_time) * 1000) / 1000,
            )
        )
        print(
            "States searched:",
            len(states_searched) - (len(states_searched) % 10000),
            end="\r",
        )
        prev_lim = limit_god
    if write_md:
        time_taken = write_to(states_searched, lens)
        printable = "God's number is %s in %s seconds (not counting writing time)" % (
            (gen_god, round((time.time() - orig_time - time_taken) * 1000) / 1000)
        )
    else:
        printable = "God's number is %s in %s seconds" % (
            (gen_god, round((time.time() - orig_time) * 1000) / 1000)
        )
    rand_num = randint(lens[len(lens) - 2], lens[len(lens) - 1] - 8)
    print()
    for eight in range(8):
        print(states[rand_num + eight])
    print("Above are eight random 11 move states")
    print()
    print(printable)
    print()


if input("God or regular?: ").lower() != "god":
    returnable = questioning()
    start = [returnable[0]]
    dictstart = {returnable[1]: ""}
    dictsolved = {((0, 1, 2, 3, 4, 5, 6, 7), (0, 0, 0, 0, 0, 0, 0, 0)): ""}
    moves_solved = [""]
    moves_start = [""]
    start_time = time.time()
    list_inverted_moves = []
    if start == solved:
        print()
        print("Solution: ")
        print("Inverted solution: ")
        print()
        print("Amount of moves: 0")
        print("Start state: %s" % (str(start[0])))
        print("Time taken: 0 miliseconds")
        print()
    else:
        solution = main()
        print()
        print("Solution: %s" % (" ".join(solution)))
        print("Inverted solution: %s" % (" ".join(list_inverted_moves)))
        print()
        print("Amount of moves: %d" % (len(solution)))
        print("Start state: %s" % (str(start[0])))
        print("Time taken: %s miliseconds" % (str(round(time.time() - start_time, 3) * 1000)))
        print()
else:
    god()
