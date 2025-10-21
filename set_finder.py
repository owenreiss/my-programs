# finds all sets given cards for the "set" board game

import pygame
# pygame is a library that allows this program to run visually
import sys
import os

pygame.init()
os.chdir("/Users/owenreiss/Desktop/Coding/python/all_set_card_imgs") # os.chdir changes the directory that the program
# will try to load images from. Normally I would insert the directory with the
# images for the cards. The directory is removed in this case to avoid showing my name.

class Card(pygame.sprite.Sprite):
    # pygame.sprite.Sprite is a class that the pygame
    # documentation recommends that all visual objects inherit from
    def __init__(self, image, coordinates):
        super().__init__()
        self.image = pygame.image.load(image) # loads the image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()
        self.rect.topleft = coordinates # sets the top left of the image to given coordinates
        self.card_val = image[:4]
        # the first 4 characters of the image name should represent
        # its attributes. An example name is: 1312.png

    def draw(self):
        DISPLAY.blit(self.image, self.rect) # draws the image to the display

class Text(pygame.sprite.Sprite):
    def __init__(self, text, coordinates, size, color=(255,)*3, mid_left=False):
        super().__init__()
        font = pygame.font.Font("freesansbold.ttf", size)
        self.image = font.render(text, True, color)
        self.text = text
        self.size = size
        self.rect = self.image.get_rect()
        if mid_left:
            self.rect.midleft = coordinates
        else:
            self.rect.center = coordinates

    def draw(self):
        DISPLAY.blit(self.image, self.rect)


ALL_CARD_NAMES = sorted(os.listdir())[1:] # os.listdir gets all file 
# names in the directory, including the extension (.png)
MARGIN = 80 # margin for text at the top of the screen
Y_VALUES = (80, 135, 191, 246, 301, 356, 409, 462, 517) # y values of cards
X_VALUES = (0, 100, 199, 298, 399, 499, 599, 697, 797) # x values of cards
DISPLAY = pygame.display.set_mode((897, 496 + MARGIN)) # sets the window size
FPS = pygame.time.Clock() # used later to control FPS
ALL_CARDS = set()
for index, card_name in enumerate(ALL_CARD_NAMES):
    # index increases by 1 after every loop starting from 0
    ALL_CARDS.add(
        Card(
            card_name, (X_VALUES[index % 9], Y_VALUES[index // 9]) 
            )
        )
pygame.display.set_caption("Set Finder")


def is_set(cards):
    card1, card2, card3 = cards
    for index in range(4):
        # a card identity consists of 4 numbers, one each for
        # shape, amount of figures, color, and shading.
        # 3 cards are considered to be a set if all of their
        # attributes are the same, or different for each 4 attributes.
        same = card1[index] == card2[index] and card1[index] == card3[index]
        different = card1[index] != card2[index] and card1[index] != card3[index] and card2[index] != card3[index]
        if not same and not different:
            return False
        elif index == 3: # the index equaling 3 will be the last loop, since range(4) consists of 0, 1, 2, and 3
            return True

def get_sets(cards):
    # checks all possible 3 card combinations in the given cards and looks for sets
    sets = []
    c1 = 0
    c2 = 1
    c3 = 2
    while c1 < len(cards) - 2:
        while c2 < len(cards) - 1:
            while c3 < len(cards):
                check = (cards[c1], cards[c2], cards[c3])
                if is_set(check):
                    sets.append(check)
                c3 += 1
            c2 += 1
            c3 = c2 + 1
        c1 += 1
        c2 = c1 + 1
        c3 = c2 + 1
    return sets

def main():
    instructions = Text("Click on cards, press return to finish", (454, MARGIN // 2), 45)
    included_cards = set() # cards that will be searched for sets
    done_selecting = False
    start_instructions = (Text("3 cards are considered a set if all of their", (454, 213), 32),
                          Text("attributes are either the same or all different.", (454, 263), 32),
                          Text("The attributes are: color, amount, shading, and shape", (454, 313), 32),
                          Text("Click anywhere to begin", (454, 363), 32))
    displaying_start_instructions = True
    no_sets = False # True if there are no sets present, False if there are sets
    current_set = () # current set being displayed. Not relevant right now
    clicking_list = [False, False] # current mouse click status.
    # in clicking_list, index 0 was previous frame, index 1 is current frame
    while True:
        DISPLAY.fill((0,) * 3) # fills the display with black
        if not done_selecting and not displaying_start_instructions:
            instructions.draw()
        if displaying_start_instructions:
            for instruction in start_instructions:
                instruction.draw()
        for card in ALL_CARDS:
            if done_selecting and not displaying_start_instructions:
                should_draw = card.card_val in current_set
            elif not displaying_start_instructions:
                should_draw = card.card_val not in {included_card.card_val for included_card in included_cards} # if card is not in included cards
            else:
                should_draw = False
            if should_draw:
                card.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # checks if the window is being closed
                pygame.quit()
                sys.exit() # closes the program
            if event.type == pygame.KEYDOWN and not done_selecting and not displaying_start_instructions:
                if event.key == pygame.K_RETURN: # if return key is pressed:
                    done_selecting = True
                    sets = get_sets([card.card_val for card in included_cards])
                    if len(sets) == 0:
                        no_sets = True
                        no_sets_text = Text("No sets present", (454, 232), 50)
                        play_again_text = Text("Play again", (554, 344), 30, (0,255,0))
                        exit_text = Text("Exit", (354, 344), 30, (255,0,0))
                    else:
                        current_set = sets[0]
                        current_set_index = 0 # index of current set being shown
                        sets_texts = [
                            Text(f"{len(sets)} set{'s' if len(sets) > 1 else ''} present. Click to view next set", (5, MARGIN // 4), 35, mid_left=True),
                            Text(f"Currently viewing set {current_set_index + 1} of {len(sets)}", (5, (3 * MARGIN) // 4), 35, mid_left=True)
                            ]
                        # mid_left means the given coordinates will be at the middle left of the text, instead of the center
                        play_again_text = Text("Play again", (800, MARGIN // 4), 30, (0,255,0))
                        exit_text = Text("Exit", (800, (3 * MARGIN) // 4), 30, (255,0,0))
        clicking_list.append(pygame.mouse.get_pressed()[0]) # update clicking status
        del clicking_list[0]
        if clicking_list[1]:
            if displaying_start_instructions:
                displaying_start_instructions = False
            else:
                if not done_selecting:
                    # if the user holds down and moves the mouse, new cards will be added
                    coordinates = pygame.mouse.get_pos() # position of the mouse
                    for card in ALL_CARDS:
                        if card.rect.collidepoint(*coordinates): # if the mouse is over the card:
                            included_cards.add(card)
                            break # exits the loop, because only 1 card should be able to be clicked at a time
                elif not no_sets and not clicking_list[0]:
                    # if the user holds the mouse, the sets will not advance because of "and not clicking_list[0]"
                    current_set_index += 1 
                    current_set_index %= len(sets) # if the set being shown exceeds the length of the sets, this resets it to the first set
                    current_set = sets[current_set_index]
                    sets_texts[1] = Text(f"Currently viewing set {current_set_index + 1} of {len(sets)}", (5, (3 * MARGIN) // 4), 35, mid_left=True)
        if done_selecting:
            play_again_text.draw()
            exit_text.draw()
            if clicking_list[1] and not clicking_list[0]: # makes sure the mouse has just been clicked on this frame
                if play_again_text.rect.collidepoint(*pygame.mouse.get_pos()):
                    return True # returning True calls this function again
                if exit_text.rect.collidepoint(*pygame.mouse.get_pos()):
                    return False # returning False terminates the program
            if no_sets:
                no_sets_text.draw()
            else:
                for txt in sets_texts:
                    txt.draw()
        pygame.display.update()
        FPS.tick(30)
        # These 2 lines update the screen. FPS.tick(30) means the program will run at 30 frames per second


if __name__ == "__main__":
    while main():
        pass
