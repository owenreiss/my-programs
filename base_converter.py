valid_base = lambda arg: arg in range(2, 37)
CHARACTERS = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")

def to10(arg_number, base):
    alpha_conv = []
    new_num = 0
    str_num = str(arg_number)
    for idx, num in enumerate(str_num):
        alpha_conv.append(CHARACTERS.index(num))
    len_alpha = len(alpha_conv) - 1
    for idx, num in enumerate(alpha_conv):
        new_num += (base ** (len_alpha - idx)) * num
    return new_num

def ten_to(number, base):
    start = number
    new_num_list = []
    while start > 0:
        new_num_list.append(start % base)
        start = start // base
    new_num_list.reverse()
    for idx, digit in enumerate(new_num_list):
            new_num_list[idx] = CHARACTERS[digit]
    return new_num_list

def convert(number, base_in=10, base_out=2):
    """Returns string representation of number"""
    return "".join(ten_to(to10(number, base_in), base_out))

def main():
    while True:
        given_base = int(input("What base is your number in (2-36)?: "))
        if valid_base(given_base):
            break
        else:
            print("Number not between 2 and 36")
    number = input("What is your number?: ").upper()
    while True:
        wanted_base = int(input("What base do you want to convert to (2-36)?: "))
        if valid_base(wanted_base):
            break
        else:
            print("Number not between 2 and 36")
    sol = convert(number, given_base, wanted_base)
    print(f"{number}({given_base}) = {sol}({wanted_base})")

main()