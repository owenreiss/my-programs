# computer plays cows and bulls and tries to guess user's number, algorithm creation in mastermind.py

import copy
import frozendict
import pickle
import os
os.chdir("/Users/owenreiss/Desktop/Coding/python")
frzn = frozendict.frozendict
def get_result(secret, given):
    green = 0
    yellow = 0
    for secret_char, given_char in zip(secret, given):
        if given_char == secret_char:
            green += 1
        elif given_char in secret:
            yellow += 1
    return green, yellow

def determine_possible_secrets(guess_dict):
    possible_strs = []
    for answer in all_strs:
        works = True
        for guess, result in guess_dict.items():
            if get_result(answer, guess) != result:
                works = False
        if works:
            possible_strs.append(answer)
    return possible_strs

def median(data):
    sorted_data = sorted(data)
    if len(data) % 2 == 0:
        return (sorted_data[len(data) // 2] + sorted_data[(len(data) // 2) - 1]) / 2
    else:
        return sorted_data[len(data) // 2]
    
def avg(data):
    return sum(data) / len(data)

all_strs = []
for num in range(10_000):
    will_continue = False
    str_num = str(num)
    while len(str_num) < 4:
        str_num = "0" + str_num
    occurances = set()
    for digit in str_num:
        if digit in occurances:
            will_continue = True
            break
        else:
            occurances.add(digit)
    if will_continue:
        continue
    all_strs.append(str_num)

with open("mastermind_tablebase", "rb") as file:
    guess_tablebase = pickle.load(file)
all_results = ("00", "01", "02", "03", "04", "10", "11", "12", "13", "20", "21", "22", "30", "31", "40")
possible_strs = all_strs
guesses = {}
done = False
guess = "0123"
unseen_digits = {str(x) for x in range(10)}
amnt_possible = 5040

while not done:
    result = input(f"My guess it {guess}, result: ")
    result = (int(result[0]), int(result[1]))
    if result == (4, 0):
        done = True
        continue
    guesses[guess] = result
    possible_strs = determine_possible_secrets(guesses)
    amnt_possible = len(possible_strs)
    print(amnt_possible)
    medians = {}
    averages = {}
    unseen_digits -= set(guess)
    if amnt_possible <= 15:
        print(possible_strs)
    count = 0
    first = True
    if amnt_possible <= 2:
        guess = possible_strs[0]
        continue
    if frzn(guesses) in guess_tablebase:
        guess = guess_tablebase[frzn(guesses)]
        continue
    not_needed_guesses = set()
    for possible_guess in all_strs:
        print(count / 50.4, end="\r")
        if possible_guess in guesses or possible_guess in not_needed_guesses:
            count += 1
            continue
        for idx, num in enumerate(possible_guess):
            if num not in unseen_digits:
                continue
            identicals = unseen_digits - set(possible_guess)
            for iden in identicals:
                not_needed_guesses.add(possible_guess[:idx] + iden + possible_guess[idx + 1:])
        the_lens = []
        for result in all_results:
            possible_guesses = copy.copy(guesses) # shallow
            possible_guesses[possible_guess] = tuple(int(result[x]) for x in (0, 1))
            possible_possible_strs = determine_possible_secrets(possible_guesses)
            if not possible_possible_strs:
                continue
            the_lens.append(len(possible_possible_strs))
        medians[possible_guess] = median(the_lens)
        averages[possible_guess] = avg(the_lens)
        if avg(the_lens) == 1:
            best_guess = possible_guess
            break
        if first:
            best_guess = possible_guess
            first = False
        elif averages[best_guess] > avg(the_lens):
            best_guess = possible_guess
        count += 1
    guess = best_guess
