# text-based 2 player tic tac toe

row_1 = [" ", "|", " ", "|", " "]
row_2 = [" ", "|", " ", "|", " "]
row_3 = [" ", "|", " ", "|", " "]
wins = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
visible_board_state = [row_1, row_2, row_3]
board_state = [0, 1, 2, 3, 4, 5, 6, 7, 8]

def print_board():
    for gen, row in enumerate(visible_board_state):
        for individual in row:
            print(individual, end =" ")
        if gen < 2:
            print()
            print("----------")
    print()
    print()

def valid_input(given):
    return given >= 1 and given <= 9 and board_state[given - 1] != "X" and board_state[given - 1] != "O"

def edit_board(cell, placement):
    visible_board_state[(cell // 3)][(cell % 3) * 2] = placement
    board_state[cell] = placement

def check_win_and_draw():
    full = True
    for num in range(9):
        if num in board_state:
            full = False
    for arr in wins:
        if board_state[arr[0]] == board_state[arr[1]] and board_state[arr[0]] == board_state[arr[2]]:
            return board_state[arr[0]], *[x + 1 for x in arr]
    if full:
        return "Draw"
def main(argv):
    game_over = False   
    current_player = 1
    current_mark = "X"
    marks = ("X", "O")

    while not game_over:
        print_board()
        vi = False
        while not vi:
            given_cell = int(input("Player %s, what cell do you wish to play in (1-9)?: " % (str(current_player))))
            if valid_input(given_cell):
                vi = True
            else:
                print("Invalid input")
        edit_board(given_cell - 1, current_mark)
        current_mark = marks[current_player % 2]
        current_player = (current_player % 2) + 1
        if check_win_and_draw():
            game_over = True
    print()
    print()
    print()
    print()
    print_board()
    print()
    print()
    if check_win_and_draw()[0] == "X" or check_win_and_draw()[0] == "O":
        print("%s is the winner with cells %d, %d, and %d" % check_win_and_draw())
    else:
        print("It's a draw!")
    print()
    return

main(None)
