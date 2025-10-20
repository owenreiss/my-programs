#First functional scramble ever!!! ((3, 2, 7, 11, 6, 4, 10, 0, 8, 1, 9, 5), (1, 3, 4, 0, 2, 5, 7, 6), (1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1), (1, 2, 1, 0, 0, 0, 1, 1))
#Old alg solve: R' D' R' D2 R D2 F U' R B2 L' B' L R2 F' U F U R' U2 R U' R' U2 R' U R2 U R' U' R U' R' U2 R U R2 B2 R F R' B2 R F' R U R L' U2 D2 R L' D R2 L2 U' F2 B2 U'
#New alg solve: F' U F2 L D B U2 R' U R2 B R' B2 R' F R2 F' R F R F' R' U R2 U' R2 U' R2 U2 R U2 F2 U' F2 D R2 B2 U B2 D' R2 U'

#white top green front
#corner stats same as 2x2
#edge positions
#first color is key sticker
#0 = front top, white green
#1 = left top, white orange
#2 = back top, white blue
#3 = right top, white red
#4 = front left, green orange
#5 = front right, green red
#6 = back left, blue orange
#7 = back right, blue red
#8 = front bottom, yellow green
#9 = left bottom, yellow orange
#10 = back bottom, yellow blue
#11 = right bottom, yellow red
#edge ori
#0-3 = key sticker, up
#4-5 = key sticker front
#6-7 = key sticker back
#8-11 = key sticker bottom
#idx 0 of state = edge pos
#idx 1 of state = corner pos
#idx 2 of state = edge oris
#idx 3 of state = corner oris

import time
import copy
import random

#globals defined here
_12_ZEROS = [0] * 12
_8_ZEROS = [0] * 8
F_EDGES = [1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0]
B_EDGES = [0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0]
SOLVED_STATE_DONT_CHANGE = [list(range(12)), list(range(8)), _12_ZEROS, _8_ZEROS]
TUP_SOLVED = (tuple(range(12)), tuple(range(8)), tuple(_12_ZEROS), tuple(_8_ZEROS))
SOLVED = [SOLVED_STATE_DONT_CHANGE]

#Information for all moves. INVERTED

FP = [[4, 1, 2, 3, 8, 0, 6, 7, 5, 9, 10, 11], [4, 1, 2, 0, 7, 5, 6, 3], F_EDGES, [1, 0, 0, 2, 2, 0, 0, 1]]
F = [[5, 1, 2, 3, 0, 8, 6, 7, 4, 9, 10, 11], [3, 1, 2, 7, 0, 5, 6, 4], F_EDGES, [1, 0, 0, 2, 2, 0, 0, 1]]
F2 = [[8, 1, 2, 3, 5, 4, 6, 7, 0, 9, 10, 11], [7, 1, 2, 4, 3, 5, 6, 0], _12_ZEROS, _8_ZEROS]
RP = [[0, 1, 2, 5, 4, 11, 6, 3, 8, 9, 10, 7], [0, 1, 3, 7, 4, 5, 2, 6], _12_ZEROS, [0, 0, 2, 1, 0, 0, 1, 2]]
R = [[0, 1, 2, 7, 4, 3, 6, 11, 8, 9, 10, 5], [0, 1, 6, 2, 4, 5, 7, 3], _12_ZEROS, [0, 0, 2, 1, 0, 0, 1, 2]]
R2 = [[0, 1, 2, 11, 4, 7, 6, 5, 8, 9, 10, 3], [0, 1, 7, 6, 4, 5, 3, 2], _12_ZEROS, _8_ZEROS]
UP = [[3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11], [3, 0, 1, 2, 4, 5, 6, 7], _12_ZEROS, _8_ZEROS]
U = [[1, 2, 3, 0, 4, 5, 6, 7, 8, 9, 10, 11], [1, 2, 3, 0, 4, 5, 6, 7], _12_ZEROS, _8_ZEROS]
U2 = [[2, 3, 0, 1, 4, 5, 6, 7, 8, 9, 10, 11], [2, 3, 0, 1, 4, 5, 6, 7], _12_ZEROS, _8_ZEROS]
BP = [[0, 1, 7, 3, 4, 5, 2, 10, 8, 9, 6, 11], [0, 2, 6, 3, 4, 1, 5, 7], B_EDGES, [0, 2, 1, 0, 0, 1, 2, 0]]
B = [[0, 1, 6, 3, 4, 5, 10, 2, 8, 9, 7, 11], [0, 5, 1, 3, 4, 6, 2, 7], B_EDGES, [0, 2, 1, 0, 0, 1, 2, 0]]
B2 = [[0, 1, 10, 3, 4, 5, 7, 6, 8, 9, 2, 11], [0, 6, 5, 3, 4, 2, 1, 7], _12_ZEROS, _8_ZEROS]
LP = [[0, 6, 2, 3, 1, 5, 9, 7, 8, 4, 10, 11], [1, 5, 2, 3, 0, 4, 6, 7], _12_ZEROS, [2, 1, 0, 0, 1, 2, 0, 0]]
L = [[0, 4, 2, 3, 9, 5, 1, 7, 8, 6, 10 ,11], [4, 0, 2, 3, 5, 1, 6, 7], _12_ZEROS, [2, 1, 0, 0, 1, 2, 0, 0]]
L2 = [[0, 9, 2, 3, 6, 5, 4, 7, 8, 1, 10, 11], [5, 4, 2, 3, 1, 0, 6, 7], _12_ZEROS, _8_ZEROS]
DP = [[0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 8], [0, 1, 2, 3, 5, 6, 7, 4], _12_ZEROS, _8_ZEROS]
D = [[0, 1, 2, 3, 4, 5, 6, 7, 11, 8, 9, 10], [0, 1, 2, 3, 7, 4, 5, 6], _12_ZEROS, _8_ZEROS]
D2 = [[0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 8, 9], [0, 1, 2, 3, 6, 7, 4, 5], _12_ZEROS, _8_ZEROS]
VALID_MOVES = ["F", "G", "H", "R", "S", "T", "U", "V", "W", "B", "C", "D", "L", "M", "N", "1", "2", "3"]
VALID_MOVE_INDEXES = {x: y for x, y in zip(VALID_MOVES, range(18))} # zip expires at shortest argument
INVERSION_VM = ["G", "F", "H", "S", "R", "T", "V", "U", "W", "C", "B", "D", "M", "L", "N", "2", "1", "3"]
CONVERSION_VM = ["F", "F'", "F2", "R", "R'", "R2", "U", "U'", "U2", "B", "B'", "B2", "L", "L'", "L2", "D", "D'", "D2"]
INVERSION_CONVERSION = ["F'", "F", "F2", "R'", "R", "R2", "U'", "U", "U2", "B'", "B", "B2", "L'", "L", "L2", "D'", "D", "D2"]
LIST_MOVES = [F, FP, F2, R, RP, R2, U, UP, U2, B, BP, B2, L, LP, L2, D, DP, D2]
LIST_MOVES_INVERSION = [FP, F, F2, RP, R, R2, UP, U, U2, BP, B, B2, LP, L, L2, DP, D, D2]
SOLVED_1 = [[["", "", "", "", 4, "", "", "",  "", "", "", ""], ["", "", "", "", 4, "", "", ""], ["", "", "", "", 0, "", "", "", "", "", "", ""], ["", "", "", "", 0, "", "", ""]], [["", "", "", "", 4, "", "", "", 8, 9, "", ""], ["", "", "", "", 4, "", "", ""], ["", "", "", "", 0, "", "", "", 0, 0, "", ""], ["", "", "", "", 0, "", "", ""]]]
SOLVED_2 = [[["", "", "", "", 4, "", 6, "", 8, 9, "", ""], ["", "", "", "", 4, 5, "", ""], ["", "", "", "", 0, "", 0, "", 0, 0, "", ""], ["", "", "", "", 0, 0, "", ""]], [["", "", "", "", 4, "", 6, "", 8, 9, 10, ""], ["", "", "", "", 4, 5, "", ""], ["", "", "", "", 0, "", 0, "", 0, 0, 0, ""], ["", "", "", "", 0, 0, "", ""]]]
SOLVED_3 = [[["", "", "", "", 4, "", 6, "", 8, 9, 10, ""], ["", "", "", "", 4, 5, "", ""], _12_ZEROS, ["", "", "", "", 0, 0, "", ""]]]
SOLVED_4 = [[["", "", "", "", 4, 5, 6, 7, 8, 9, 10, 11], ["", "", "", "", 4, 5, 6, 7], _12_ZEROS, ["", "", "", "", 0, 0, 0, 0]]]
TUP_ALGS_OLL = (("R", "U", "S", "U", "R", "W", "S"), ("S", "V", "R", "V", "S", "W", "R"), ("R", "U", "S", "U", "R", "V", "S", "U", "R", "W", "S"), ("R", "W", "T", "V", "T", "V", "T", "W", "R"), ("T", "1", "S", "W", "R", "2", "S", "W", "S"), ("M", "C", "L", "G", "M", "B", "L", "F"), ("G", "M", "C", "L", "F", "M", "B", "L"))
ALGS_OLL = {(0, 1, 1, 1): TUP_ALGS_OLL[0], (2, 0, 2, 2): TUP_ALGS_OLL[1], (1, 2, 1, 2): TUP_ALGS_OLL[2], (1, 2, 2, 1): TUP_ALGS_OLL[3], (2, 0, 0, 1): TUP_ALGS_OLL[4], (1, 0, 0, 2): TUP_ALGS_OLL[5], (0, 1, 0, 2): TUP_ALGS_OLL[6], (0,) * 4: ()}
ALGS_PLL = {(tuple(range(4)), (0, 3, 1, 2)): "TDRFSDRGR", (tuple(range(4)), (0, 2, 3, 1)): "SFSDRGSDT", (tuple(range(4)), (1, 0, 3, 2)): "RLFMBLGSMFRCSG", ((2, 3, 0, 1), (3, 2, 1, 0)): "RLFMBLGSMFRCSG", ((3, 2, 1, 0), (2, 0, 1, 3)): "RMDM1SDLVTLHT", ((2, 0, 1, 3), (1, 3, 2, 0)): "DTNUNVN1N2TD", ((0, 2, 3, 1), (2, 0, 1, 3)): "THUT2T1DVHDT",
((1, 2, 0, 3), (2, 0, 1, 3)): "HTNVNUN2N1TH", ((3, 0, 2, 1), (1, 3, 2, 0)): "TDVT1T2HUHDT", ((2, 3, 0, 1), tuple(range(4))): "THDN2THDN", ((1, 2, 3, 0), (3, 0, 1, 2)): "THDN2THDN", (tuple(range(4)), (2, 3, 0, 1)): "THDN2THDN", ((3, 0, 1, 2), (1, 2, 3, 0)): "THDN2THDN", ((0, 1, 3, 2), (0, 1, 3, 2)): "T1R2RHMULH", ((3, 1, 2, 0), (0, 1, 3, 2)): "T2S1SDLVMD",
((0, 3, 2, 1), (2, 1, 0, 3)): "RVTD2LHM1DTUS", ((1, 0, 3, 2), (3, 2, 1, 0)): "RVTD2LHM1DTUS", ((2, 1, 0, 3), (0, 3, 2, 1)): "RVTD2LHM1DTUS", ((3, 2, 1, 0), (1, 0, 3, 2)): "RVTD2LHM1DTUS", ((0, 3, 2, 1), (0, 3, 2, 1)): "RVTHVRHSUHTUS", ((1, 0, 3, 2), (1, 0, 3, 2)): "RVTHVRHSUHTUS", ((2, 1, 0, 3), (2, 1, 0, 3)): "RVTHVRHSUHTUS",
((3, 2, 1, 0), (3, 2, 1, 0)): "RVTHVRHSUHTUS", ((3, 0, 2, 1), (2, 0, 1, 3)): "RWSUBMCRBLCUS", ((0, 2, 3, 1), (1, 3, 2, 0)): "RUC3FMG3DVSUC", ((1, 0, 3, 2), (2, 0, 1, 3)): "HVH1TDUD2T", ((1, 3, 2, 0), tuple(range(4))): "HULSHRMUH", ((3, 0, 2, 1), tuple(range(4))): "HVLSHRMVH", ((0, 1, 3, 2), (0, 3, 2, 1)): "TVDUDR2R1SURVR", ((0, 2, 1, 3), (0, 3, 2, 1)): "TVTVTUFUGTFVG",
((1, 0, 3, 2), tuple(range(4))): "RMW3RM1TNVHD", ((3, 2, 1, 0), (2, 3, 0, 1)): "RMW3RM1TNVHD", (tuple(range(4)), tuple(range(4))): "", ((1, 2, 0, 3), (3, 1, 0, 2)): "LVRWMUSGCWFB"}

def perform_move(move, state):
    """Returns a state as a tuple after a move"""
    edge_pos = state[0]
    corner_pos = state[1]
    edge_ori = state[2]
    corner_ori = state[3]
    move_index = VALID_MOVE_INDEXES[move]
    move_list = LIST_MOVES[move_index]
    iv_mv_list = LIST_MOVES_INVERSION[move_index]
    new_epos = [None] * 12
    new_cpos = [None] * 8
    new_eori = [None] * 12
    new_cori = [None] * 8
    for idx, epos in enumerate(edge_pos):
        new_epos[move_list[0][idx]] = epos
    for idx, cpos in enumerate(corner_pos):
        new_cpos[move_list[1][idx]] = cpos
    for idx, ori_idx in enumerate(iv_mv_list[0]):
        if edge_ori[ori_idx] != "":
            new_eori[idx] = (iv_mv_list[2][idx] + edge_ori[ori_idx]) % 2
        else:
            new_eori[idx] = ""
    for idx, cori_idx in enumerate(iv_mv_list[1]):
        if corner_ori[cori_idx] != "":
            new_cori[idx] = (iv_mv_list[3][idx] + corner_ori[cori_idx]) % 3
        else:
            new_cori[idx] = ""
    return (tuple(new_epos), tuple(new_cpos), tuple(new_eori), tuple(new_cori))

def gen_rndm_state():
    unused = list(range(12)), list(range(8))
    state = [], [], [], []
    while len(state[0]) < 12:
        new_piece = random.choice(unused[0])
        state[0].append(new_piece)
        del unused[0][unused[0].index(new_piece)] # piece and index are identical
        if len(state[0]) == 12:
            state[2].append(sum(state[2]) % 2)
        else:
            state[2].append(random.randint(0, 1))
    while len(state[1]) < 8:
        new_piece = random.choice(unused[1])
        state[1].append(new_piece)
        del unused[1][unused[1].index(new_piece)]
        if len(state[1]) == 8:
            state[3].append((0 - sum(state[3])) % 3)
        else:
            state[3].append(random.randint(0, 2))
    if is_valid_state(state, False)[0]:
        return tuple(tuple(x) for x in state)
    return tuple(tuple(x) for x in [[state[0][1], state[0][0]] + state[0][2:]] + list(state[1:4]))

def solve_from_moves(moves, uncv=True, only_get_state=False):
    state = copy.deepcopy(SOLVED_STATE_DONT_CHANGE)
    new_mvs = unconvert(moves) if uncv else moves
    for move in new_mvs:
        state = perform_move(move, state)
    if only_get_state:
        return state
    compute_and_print(state)

def is_valid_state(new_state, chck_tmt, _4x4=False):
    """Checks for valid orientations and permutation of pieces; always returns a boolean"""
    orig_time = time.time()
    epos, cpos, eori, cori = copy.deepcopy(new_state)
    parities = []
    if not _4x4:
        if sum(eori) % 2 != 0:
            return False, 0
        if sum(cori) % 3 != 0:
            return False, 1
    else:
        parities.append(sum(eori) % 2)
    swaps = 0
    new_epos = list(epos)
    #this part swaps pieces. If even swaps, valid state. If not, invalid!
    while new_epos != list(range(12)):
        timeout = time.time() - orig_time > 0.5
        if timeout and chck_tmt:
            raise TimeoutError("took too long to assess given state while checking edge swaps")
        for idx, piece in enumerate(new_epos):
            if piece != idx:
                swapable = new_epos[piece]
                new_epos[idx] = swapable
                new_epos[piece] = piece
                swaps += 1
                break
    new_cpos = list(cpos)
    while new_cpos != list(range(8)):
        timeout = time.time() - orig_time > 0.5
        if timeout and chck_tmt:
            raise TimeoutError("took too long to assess given state while checking corner swaps")
        for idx, piece in enumerate(new_cpos):
            if piece != idx:
                swapable = new_cpos[piece]
                new_cpos[idx] = swapable
                new_cpos[piece] = piece
                swaps += 1
                break
    return parities + [swaps % 2] if _4x4 else (swaps % 2 == 0, 2)
    

def iden_move(wanted_move, last_move):
    """Doesn't allow for F to be performed after F2"""
    r_iden = frozenset({"R", "S", "T"})
    f_iden = frozenset({"F", "G", "H"})
    u_iden = frozenset({"U", "V", 'W'})
    l_iden = frozenset({"L", "M", "N"})
    d_iden = frozenset({"1", "2", "3"})
    biden = frozenset({"B", "C", "D"})
    all = [r_iden, f_iden, u_iden, l_iden, d_iden, biden]
    for idx, frznset in enumerate(all):
        if last_move in frznset:
            return wanted_move in all[idx]
    raise ValueError("move not found in function iden_move")

def unconvert(moves):
    """Converts moves from readable to single character; used in upper_bnd_3x3"""
    new = []
    for move in moves:
        new.append(VALID_MOVES[CONVERSION_VM.index(move)])
    return new

def convert(moves):
    """Converts single character moves to readable moves (e.g. G to F')"""
    new_moves = []
    for move in moves:
        new_moves.append(CONVERSION_VM[VALID_MOVES.index(move)])
    return new_moves

def invert(moves):
    """Returns an inverted list of moves"""
    new_moves = []
    for move in reversed(moves):
        new_moves.append(INVERSION_CONVERSION[CONVERSION_VM.index(move)])
    return new_moves

def oth_invert(moves):
    new_moves = []
    for move in reversed(moves):
        new_moves.append(INVERSION_VM[VALID_MOVES.index(move)])
    return new_moves

def max_simplified_first(list_input):
    """First stage check to see if moves are simplified. Won't allow R' and R2 to be adjacent"""
    for idx, lister in enumerate(list_input[:len(list_input) - 1]):
        if lister[0] == list_input[idx + 1][0]:
            return False
    for item in list_input:
        mag = item[1]
        if mag == 0:
            return False
    return True

def max_simplified_second(list_input, opppes):
    """Doesn't allow for F, B, F2 bc B layer doesn't interfere at all with F, so this is the same as F', B"""
    opps = opppes
    whole_opps = [opps[0][0], opps[0][1], opps[1][0], opps[1][1], opps[2][0], opps[2][1]]
    for idx, lister in enumerate(list_input[:len(list_input) - 2]):
        for index, listre in enumerate(whole_opps):
            if lister[0] in listre:
                opp_list = opps[index // 2][(index + 1) % 2]
                break
        else:
            raise ValueError("Illegal move root in max_simplified_second")
        if lister[0] == list_input[idx + 2][0] and list_input[idx + 1][0] in opp_list:
            return False
    return True

def simplify_second(list_input, opes):
    """Simplifies F, B, F2 to F', B"""
    opps = opes
    new_input = list_input
    len_m_2 = len(list_input) - 2
    idx = 0
    while idx < len_m_2:
        lister = new_input[:len_m_2][idx]
        for oth_idx, listi in enumerate(opps):
            for indx, indi in enumerate(listi):
                if lister[0] in indi:
                    opp_list = opps[oth_idx][(indx + 1) % 2]
        if lister[0] == new_input[idx + 2][0] and new_input[idx + 1][0] in opp_list:
            new_input[idx] = [lister[0], (lister[1] + new_input[idx + 2][1]) % 4]
            del new_input[idx + 2]
        idx += 1
        len_m_2 = len(list_input) - 2
    return new_input

def simplify(moves):
    """Main simplifier, returns a list of moves free of things like L', L2 and U, D, U2"""
    given = moves
    finished = False
    new_moves = []
    mag = 0
    root = ""
    r_iden = ["R", "T", "S"]
    f_iden = ["F", "H", "G"]
    u_iden = ["U", "W", 'V']
    l_iden = ["L", "N", "M"]
    d_iden = ["1", "3", "2"]
    biden = ["B", "D", "C"]
    all = [r_iden, f_iden, u_iden, l_iden, d_iden, biden]
    opps = [[f_iden, biden], [r_iden, l_iden], [u_iden, d_iden]]
    for mover in given:
        for idx, lister in enumerate(all):
            if mover in lister:
                num_in = idx
                break
        root = all[num_in][0]
        mag = all[num_in].index(mover) + 1
        new_moves.append([root, mag])
    while not finished:
        idx = 0
        while idx < len(new_moves) - 1:
            if new_moves[idx][0] == new_moves[idx + 1][0]:
                new_moves[idx][1] = (new_moves[idx][1] + new_moves[idx + 1][1]) % 4
                del new_moves[idx + 1]
            idx += 1
        idx = 0
        length = len(new_moves)
        while idx < length:
            if new_moves[idx][1] == 0:
                del new_moves[idx]
                idx -= 1
            idx += 1
            length = len(new_moves)
        new_moves = simplify_second(new_moves, opps)
        if max_simplified_first(new_moves) and max_simplified_second(new_moves, opps):
            finished = True
    final_moves = []
    for lister in new_moves:
        for listre in all:
            if lister[0] in listre:
                list_in = listre
                break
        else:
            raise ValueError("Illegal move root in func: simplify")
        final_moves.append(list_in[lister[1] - 1])
    return final_moves

class BruteForcer():
    """Given a start state, end state, and moves allowed to do, this class is capabale of generating 
    an optimal solution. Possibly won't work when a piece has permutation but no orientation."""
    def __init__(self, state, what_to_get_to, vm):
        """Sets all instance variables"""
        self.wtgt = what_to_get_to
        new = [list(state[0]), list(state[1]), list(state[2]), list(state[3])]
        self.vm = vm
        for fidx, lister in enumerate(state[:2]):
            for idx, char in enumerate(lister):
                if not char in what_to_get_to[fidx]:
                    new[fidx][idx] = ""
        for fidx, lister in enumerate(state[2:4]):
            for idx, char in enumerate(lister):
                if new[fidx][idx] == "" and self.wtgt[2] != [0] * 12:
                    new[fidx + 2][idx] = ""
                elif fidx == 1 and new[fidx][idx] == "":
                    new[3][idx] = ""
        self.orig = state
        tup0 = tuple(new[0])
        tup1 = tuple(new[1])
        tup2 = tuple(new[2])
        tup3 = tuple(new[3])
        tup4 = tuple(what_to_get_to[0])
        tup5 = tuple(what_to_get_to[1])
        tup6 = tuple(what_to_get_to[2])
        tup7 = tuple(what_to_get_to[3])
        self.start = [(tup0, tup1, tup2, tup3)]
        self.solved = [(tup4, tup5, tup6, tup7)]
        self.m_start = [""]
        self.m_solved = [""]
        self.dict_start = {(tup0, tup1, tup2, tup3):""}
        self.dict_solved = {self.solved[0]: ""}
        self.match = False

    def find_match(self, state, st_or_sv):
        """Returns a boolean that represents a match of states between front search and back search"""
        if st_or_sv == "st":
            return state in self.dict_solved, state
        else:
            return state in self.dict_start, state

    def find_moves(self, dict_in, last_key, opp_key):
        """Determines moves needed to solve a stage given the matching states and primary dictionary"""
        if dict_in == self.dict_start:
            opp_dict = self.dict_solved
        elif dict_in == self.dict_solved:
            opp_dict = self.dict_start
        else:
            raise ValueError("not self.start and not self.solved put into find_moves in class Step1")
        moves_start = dict_in[last_key]
        moves_end = opp_dict[opp_key]
        moves_list = []
        for char in moves_start:
            moves_list.append(char)
        for char in reversed(moves_end):
            moves_list.append(INVERSION_VM[VALID_MOVES.index(char)])
        if dict_in == self.dict_solved:
            moves_iv = []
            for move in reversed(moves_list):
                moves_iv.append(INVERSION_VM[VALID_MOVES.index(move)])
            moves_list = moves_iv
        return moves_list

    def main(self):
        """Main method of class BruteForcer. Returns moves to solution, and the resulting state."""
        prev_lim = 0
        while not self.match:
            st_idx = prev_lim
            limit = len(self.start)
            list_in = self.dict_start
            while st_idx < limit and not self.match:
                lfs = self.look_from_start_1(st_idx)
                last_key = lfs[0]
                found_on_main = lfs[1]
                st_idx += 1
            if not self.match:
                list_in = self.dict_solved
                st_idx = prev_lim
                while st_idx < limit and not self.match:
                    lfsv = self.look_from_solved_1(st_idx)
                    last_key = lfsv[0]
                    found_on_main = lfsv[1]
                    st_idx += 1
            if self.match:
                state_after_moves = self.orig
                moves_to_solve = self.find_moves(list_in, last_key, found_on_main)
                for move in moves_to_solve:
                    state_after_moves = perform_move(move, state_after_moves)
                return moves_to_solve, state_after_moves
            prev_lim = limit

    def look_from_start_1(self, idx):
        """Does moves and appends new states to start dicts and lists"""
        for movenum in range(len(self.vm)):
            if idx != 0:
                if not iden_move((self.m_start[idx])[-1], self.vm[movenum]):
                    new_state = perform_move(self.vm[movenum], self.start[idx])
                    if new_state in self.dict_start:
                        continue
                    self.dict_start[new_state] = self.m_start[idx] + self.vm[movenum]
                    self.start.append(new_state)
                    self.m_start.append(self.m_start[idx] + self.vm[movenum])
                    self.match, found_on = self.find_match(new_state, "st")
                    if self.match:
                        return new_state, found_on
            else:
                new_state = perform_move(self.vm[movenum], self.start[0])
                self.start.append(new_state)
                self.m_start.append(self.vm[movenum])
                self.dict_start[new_state] = self.vm[movenum]
                self.match, found_on = self.find_match(new_state, "st") 
                if self.match:
                    return new_state, found_on
        return "yea", "nay" # I can be anything with len 2. Rename me!

    def look_from_solved_1(self, idx):
        """Same with look_from_start_1 func, but appends/adds to solved dicts and lists"""
        for movenum in range(len(self.vm)):
            if idx != 0:
                if not iden_move((self.m_solved[idx])[-1], self.vm[movenum]):
                    new_state = perform_move(self.vm[movenum], self.solved[idx])
                    if new_state in self.dict_solved:
                        continue
                    self.dict_solved[new_state] = self.m_solved[idx] + self.vm[movenum]
                    self.solved.append(new_state)
                    self.m_solved.append(self.m_solved[idx] + self.vm[movenum])
                    self.match, found_on = self.find_match(new_state, "sv")
                    if self.match:
                        return new_state, found_on
            else:
                new_state = perform_move(self.vm[movenum], self.solved[0])
                self.solved.append(new_state)
                self.m_solved.append(self.vm[movenum])
                self.dict_solved[new_state] = self.vm[movenum]
                self.match, found_on = self.find_match(new_state, "sv") 
                if self.match:
                    return new_state, found_on
        return "yeh", "nay" #I can be anything with len 2. Rename me!

#class break

class LastLayer():
    """class LastLayer needs a state, and either oll or pll to return moves
    and the resulting state. When on PLL, resulting state is not needed."""

    def __init__(self, state, oll_or_pll):
        """Generates instance variables"""
        self.state = state
        if oll_or_pll == "oll":
            self.oll = True
            self.dict_algs = ALGS_OLL
        else:
            self.oll = False
            self.dict_algs = ALGS_PLL

    def alter(self, state):
        """Used for PLL when searching for a pre-auf. Returns a length 4 list of states."""
        edges, corners = state
        returnables = []
        for num in range(4):
            returnables.append((((edges[0] + num) % 4, (edges[1] + num) % 4, (edges[2] + num) % 4, (edges[3] + num) % 4), ((corners[0] + num) % 4, (corners[1] + num) % 4, (corners[2] + num) % 4, (corners[3] + num) % 4)))
        return returnables
    
    def pre_auf(self, thing, oll):
        """Determines move needed to align top face to properly execute an algorithm."""
        if oll:
            if thing in self.dict_algs:
                return False, "yea nay" # rename the second element!
            elif (thing[3], thing[0], thing[1], thing[2]) in self.dict_algs:
                return True, "U"
            elif (thing[2], thing[3], thing[0], thing[1]) in self.dict_algs:
                return True, "W"
            elif (thing[1], thing[2], thing[3], thing[0]) in self.dict_algs:
                return True, "V"
            else:
                raise ValueError("Not valid orientation in pre_auf in class LastLayer")
        else:
            edges, corners = thing
            checkables = [thing, ((edges[3], edges[0], edges[1], edges[2]), (corners[3], corners[0], corners[1], corners[2])), ((edges[2], edges[3], edges[0], edges[1]), (corners[2], corners[3], corners[0], corners[1])),
            ((edges[1], edges[2], edges[3], edges[0]), (corners[1], corners[2], corners[3], corners[0]))]
            returnables = ((False, "yea nay"), (True, "U"), (True, "W"), (True, "V"))
            for num, item in enumerate(checkables):
                func = self.alter(item)
                if func[0] in self.dict_algs or func[1] in self.dict_algs or func[2] in self.dict_algs or func[3] in self.dict_algs:
                    return returnables[num], [func[0] in self.dict_algs, func[1] in self.dict_algs, func[2] in self.dict_algs, func[3] in self.dict_algs].index(True)
            raise ValueError("Not valid permutation in pre_auf in class LayerLayer")

    def main(self):
        """Main method of class LastLayer. Returns moves and the resulting state."""
        new_state = (tuple(self.state[0]), tuple(self.state[1]), tuple(self.state[2]), tuple(self.state[3]))
        moves = []
        if self.oll:
            thing_check = new_state[3][:4]
            auf_is_needed, auf = self.pre_auf(thing_check, self.oll)
        else:
            thing_check = (new_state[0][:4], new_state[1][:4])
            auffer = self.pre_auf(thing_check, self.oll)
            auf_is_needed, auf = auffer[0]
            idx_func = auffer[1]
        if auf_is_needed:
            moves.append(auf)
            state_after_pre_auf = perform_move(auf, self.state)
        else:
            state_after_pre_auf = self.state
        if self.oll:
            thing_check = state_after_pre_auf[3][:4]
        else:
            thing_check = (state_after_pre_auf[0][:4], state_after_pre_auf[1][:4])
            thing_check = self.alter(thing_check)[idx_func]
        for move in self.dict_algs[thing_check]:
            moves.append(move)
        list_state = self.state
        for move in moves:
            list_state = perform_move(move, list_state)
        if not self.oll and list_state[0][0] != 0:
            moves.append(["anything can go here", "U", "W", "V"][list_state[0][0]])
            list_state = perform_move(moves[-1], list_state)
        return moves, list_state

#class break

class EdgeOrientationError(Exception):
    """Easy to read name for invalid edge orientation."""
class PermutationError(Exception):
    """Easy to read name for invalid piece permutation."""
class CornerOrientationError(Exception):
    """Easy to read name for invalid corner orientation."""

def compute_and_print(state, want_st_state=True, pnga=False):
    """Biggest chunk of code. This func doesn't use any prompts; important when trying to profile, import, etc."""
    moves_for_third = ["R", "S", "T", "F", "G", "H", "U", "V", "W", "B", "C", "D"]
    moves_for_fourth = ["R", "S", "T", "U", "V", "W"]
    if not pnga:
        orig_time = round(1000 * time.time())
        time0 = orig_time
        print()
        print()
        print("Started search in 0 ms: + 0 ms from previous")
        moves_first_1, state_first_1 = BruteForcer(state, SOLVED_1[1], VALID_MOVES).main()
        time1 = round(time.time() * 1000)
        print("Completed Stage 1 in %d ms: + %d ms from previous" % (time1 - orig_time, time1 - time0))
        time0 = time1
        moves_third_1, state_third_1 = BruteForcer(state_first_1, SOLVED_3[0], VALID_MOVES).main()
        time1 = round(time.time() * 1000)
        print("Completed Stage 2 in %d ms: + %d ms from previous" % (time1 - orig_time, time1 - time0))
        time0 = time1
        moves_fourth_1, state_fourth_1 = BruteForcer(state_third_1, SOLVED_4[0], moves_for_fourth).main() # change from fourth to third if faster solution but longer wait is wanted
        time1 = round(time.time() * 1000)
        print("Completed F2L in %d ms: + %d ms from previous" % (time1 - orig_time, time1 - time0))
        time0 = time1
        moves_oll, state_oll = LastLayer(state_fourth_1, "oll").main()
        time1 = round(time.time() * 1000)
        print("Completed OLL in %d ms: + %d ms from previous" % (time1 - orig_time, time1 - time0))
        time0 = time1
        moves_pll = LastLayer(state_oll, "pll").main()[0]
        time1 = round(time.time() * 1000)
        print("Completed PLL in %d ms: + %d ms from previous" % (time1 - orig_time, time1 - time0))
        time0 = time1
        final_list = []
        all = [moves_first_1, moves_third_1, moves_fourth_1, moves_oll, moves_pll]
        for lister in all:
            for move in lister:
                final_list.append(move)
        final_moves = []
        for move in final_list:
            final_moves.append(move)
        final_moves = simplify(final_moves)
        for idx, move in enumerate(final_moves):
            final_moves[idx] = convert(move)[0]
        print()
        print("Solution:", end=' ')
        for move in final_moves:
            print(move, end=' ')
        print()
        print()
        print("INVERTED solution:", end=' ')
        for move in invert(final_moves):
            print(move, end=' ')
        print()
        print()
        print("Amount of moves: %d" % (len(final_moves)))
        print("Time taken: %s seconds" % (round(time.time() - orig_time / 1000, 3)))
        if want_st_state:
            print("Start state: %s" % (state,))
        print()
        return
    moves_first_1, state_first_1 = BruteForcer(state, SOLVED_1[1], VALID_MOVES).main()
    moves_third_1, state_third_1 = BruteForcer(state_first_1, SOLVED_3[0], VALID_MOVES).main()
    moves_fourth_1, state_fourth_1 = BruteForcer(state_third_1, SOLVED_4[0], moves_for_fourth).main()
    moves_oll, state_oll = LastLayer(state_fourth_1, "oll").main()
    moves_pll = LastLayer(state_oll, "pll").main()[0]
    return sum((len(x) for x in (moves_first_1, moves_third_1, moves_fourth_1, moves_oll, moves_pll)))

def corner_interpret(piece):
    """Returns a piece given three colors. Will return False if piece doesn't exist."""
    pieces = ["WGO", "WOB", "WBR", "WRG", "YOG", "YBO", "YRB", "YGR"]
    try:
        piece[2]
    except IndexError:
        return True
    if piece in pieces:
        return pieces.index(piece), 0
    elif piece[1] + piece[2] + piece[0] in pieces: 
        return pieces.index(piece[1] + piece[2] + piece[0]), 2
    elif piece[2] + piece[0] + piece[1] in pieces:
        return pieces.index(piece[2] + piece[0] + piece[1]), 1
    else:
        return False

def edge_interpret(piece):
    try:
        piece[1]
    except IndexError:
        return True
    """Returns a piece given two colors. Will return False if piece doesn't exist."""
    pieces = ["WG", "WO", "WB", "WR", "GO", "GR", "BO", "BR", "YG", "YO", "YB", "YR"]
    if piece in pieces:
        return pieces.index(piece), 0
    elif piece[1] + piece[0] in pieces:
        return pieces.index(piece[1] + piece[0]), 1
    else:
        return False

def main():
    """This is the whole program; involves prompting"""
    edge_oris = []
    edge_poses = []
    corner_oris = []
    corner_poses = []
    print()
    print("B = blue")
    print("G = green")
    print("O = orange")
    print("R = red")
    print("W = white")
    print("Y = yellow")
    print()
    print("To start, place the green center on front and white center on top. Your solve will not work if you don't do this!")
    print()
    quests_corner =[["top", "front", "left"], ["top", "left", "back"], ["top", "back", "right"], ["top", "right", "front"], ["bottom", "left", "front"], ["bottom", "back", "left"], ["bottom", "front", "right"]]
    quests_edge = [["top front", "up"], ["top left", "up"], ["top back", "up"], ["top right", "up"], ["front left", "forwards"], ["front right", "forwards"], ["back left", "backwards"], ["back right", "backwards"], ["front bottom", "down"], ["bottom left", "down"], ["bottom right", "down"]]
    num = 0
    while num < len(quests_corner):
        corner = input("What three colors are on the %s %s %s corner? The colors should be given in the order %s, %s, %s: " % (quests_corner[num][0], quests_corner[num][1], quests_corner[num][2], quests_corner[num][0], quests_corner[num][1], quests_corner[num][2])).upper()
        inter = corner_interpret(corner)
        if inter and inter != True:
            if inter[0] not in corner_poses:
                corner_poses.append(inter[0])
                corner_oris.append(inter[1])
                num += 1
            else:
                print()
                print("Error: duplicate pieces")
                print()
        elif not inter:
            print()
            print("Error: piece doesn't exist. Make sure you didn't accidentally flip two colors")
            print()
        else:
            print()
            print(f"Error: wanted 3 characters, got {len(corner)}")
            print()
    num = 0
    print()
    print()
    while num < len(quests_edge):
        edge = input("What two colors are on the %s edge. The first color should be the one facing %s: " % (quests_edge[num][0], quests_edge[num][1])).upper()
        inter = edge_interpret(edge)
        if inter and inter != True:
            if not inter[0] in edge_poses:
                edge_poses.append(inter[0])
                edge_oris.append(inter[1])
                num += 1
            else:
                print()
                print("Error: duplicate pieces")
                print()
        elif not inter:
            print()
            print("Error: piece doesn't exist")
            print()
        else:
            print()
            print(f"Error: wanted 2 characters, got {len(edge)}")
            print()

    edge_oris.insert(10, sum(edge_oris) % 2)
    for num in range(12):
        if not num in edge_poses:
            edge_poses.insert(10, num)
            break
    corner_oris.insert(6, (3 - (sum(corner_oris) % 3)) % 3)
    for num in range(8):
        if not num in corner_poses:
            corner_poses.insert(6, num)
            break
    state = [edge_poses, corner_poses, edge_oris, corner_oris]
    v_state = is_valid_state(state, __name__ == "__main__")
    if v_state[0]:
        compute_and_print(state)
    elif v_state[1] == 0:
        raise EdgeOrientationError("odd edge flips")
    elif v_state[1] == 1:
        raise CornerOrientationError("uneven corner twists")
    else:
        raise PermutationError("odd piece swaps")


if __name__ == "__main__":
    main()