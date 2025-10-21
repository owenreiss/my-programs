# board game simulator of forbidden island

# navigator, bugs

from copy import deepcopy
from os import chdir
from random import shuffle
import sys
import pygame

pygame.init()
chdir("/Users/owenreiss/Desktop/Coding/python/forbidden_island")

class Tile(pygame.sprite.Sprite):
    def __init__(self, name, index, state):
        super().__init__()
        self.name = name
        self.index = index
        self.state = state
        self.size = (120,) * 2
        if state == 0:
            self.image = pygame.image.load(name + ".png")
        elif state == 1:
            self.image = pygame.image.load(name + "(f).png")
        else:
            self.image = pygame.image.load("sunk.png")
        # self.image = pygame.transform.smoothscale(self.image, (120, 120))
        self.rect = self.image.get_rect()
        self.rect.topleft = tile_to_coordinates(index)
        self.coordinates = tile_to_coordinates(index)

    def get_idx(self):
        return self.index
    
    def draw(self):
        DISPLAY.blit(self.image, self.rect)

class Player(Tile):
    def __init__(self, player, tile, index):
        self.image = pygame.image.load(player + ".png")
        self.image = pygame.transform.smoothscale(self.image, (34, 60))
        self.rect = self.image.get_rect()
        self.size = (34, 60)
        coords = list(tile_to_coordinates(tile))
        coords[0] = coords[0] + (60 if index == 0 else (15 if index == 3 else 105))
        coords[1] = coords[1] + (90 if index // 2 else 30)
        if index in {1, 2}:
            self.rect.bottomright = coords
        elif index:
            self.rect.bottomleft = coords
        else:
            self.rect.midbottom = coords
        self.coordinates = coords

class Card(Tile):
    def __init__(self, card, indeces, override_coords_and_size=False):
        self.card = card
        self.indeces = indeces
        self.image = pygame.image.load(card + ".png")
        if not override_coords_and_size:
            self.image = pygame.transform.smoothscale(self.image, (72, 108))
            self.size = (72, 108)
            self.rect = self.image.get_rect()
            if indeces[0] in {0, 3}:
                x = 72 * indeces[1]
            else:
                x = 1128 - (72 * indeces[1])
            if indeces[0] <= 1:
                y = 0
            else:
                y = 612
            self.rect.topleft = (x, y)
            self.coordinates = (x, y)
        else:
            self.image = pygame.transform.smoothscale(self.image, override_coords_and_size[1])
            self.rect = self.image.get_rect()
            self.rect.center = override_coords_and_size[0]

class Text(pygame.sprite.Sprite):
    def __init__(self, text, coordinates, size, color, topleft=False, white_bg=False, midleft=False):
        super().__init__()
        font = pygame.font.Font("freesansbold.ttf", size)
        self.image = font.render(text, True, color)
        self.text = text
        self.coordinates = coordinates
        self.size = size
        self.color = color
        self.white_bg = white_bg
        self.rect = self.image.get_rect()
        self.tup_size = (self.rect.width, self.rect.height)
        self.midleft = midleft
        if midleft:
            self.rect.midleft = coordinates
        elif not topleft:
            self.rect.center = coordinates
        else:
            self.rect.topleft = coordinates

    def draw(self, current_player=False, black_bg=False):
        if current_player:
            pygame.draw.rect(DISPLAY, (127, 127, 127), self.rect)
        elif self.white_bg:
            pygame.draw.rect(DISPLAY, (255, 255, 255), self.rect)
        elif black_bg:
            pygame.draw.rect(DISPLAY, (0, 0, 0), self.rect)
        DISPLAY.blit(self.image, self.rect)

class Image(Tile):
    def __init__(self, name, size, coordinates, bw=False):
        self.name = name
        self.size = size
        self.coordinates = coordinates
        self.image = pygame.image.load(name + f"{'(bw)' if bw else ''}.png")
        self.image = pygame.transform.smoothscale(self.image, size)
        self.rect = self.image.get_rect()
        self.rect.center = coordinates

class ShoreUpIcon(Tile):
    def __init__(self, index, engineer=False):
        self.index = index
        self.engineer = engineer
        self.image = pygame.image.load(f"Shore Up{' Engineer' if engineer else ''}.png")
        self.image = pygame.transform.smoothscale(self.image, (35, 38)) # 1.09524
        self.rect = self.image.get_rect()
        self.rect.topleft = tile_to_coordinates(index)

ADJACENT_TILES = (({1, 3}, {2, 4}), ({0, 4}, {3, 5}), ({3, 7}, {0, 6, 8}), ({0, 2, 4, 8}, {1, 7, 9}), ({1, 3, 5, 9}, {0, 8, 10}), ({4, 10}, {1, 9, 11}), ({7, 12}, {2, 13}), ({2, 6, 8, 13}, {3, 12, 14}), ({3, 7, 9, 14}, {2, 4, 13, 15}), ({4, 8, 10, 15}, {3, 5, 14, 16}), ({5, 9, 11, 16}, {4, 15, 17}), ({10, 17}, {5, 16}), ({6, 13}, {7, 18}), ({7, 12, 14, 18}, {6, 8, 19}), ({8, 13, 15, 19}, {7, 9, 18, 20}), ({9, 14, 16, 20}, {8, 10, 19, 21}), ({10, 15, 17, 21}, {9, 11, 20}), ({11, 16}, {10, 21}), ({13, 19}, {12, 14, 22}), ({14, 18, 20, 22}, {13, 15, 23}), ({15, 19, 21, 23}, {14, 16, 22}), ({16, 20}, {15, 17, 23}), ({19, 23}, {18, 20}), ({20, 22}, {19, 21}))
VISIBLE_WATER_METER = Image("Water Meter", (85, 240), (1002, 360))
WATER_METER = (2, 2, 3, 3, 3, 4, 4, 5, 5, None)
WATER_METERS = {"Novice": 0, "Normal": 1, "Elite": 2, "Legendary": 3}
WATER_METER_LEVEL_HEIGHTS = (457, 435, 412, 389, 367, 344, 322, 301, 279, 257)
DISPLAY = pygame.display.set_mode((1200, 720))
# DISPLAY = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
FPS = pygame.time.Clock()
END_TURN = Text("End Turn", (120, 480), 25, (255, 0, 0))
VIEW_DISCARD_PILES = Text("View Discard Piles", (120, 240), 22, (255,) * 3)
TREASURES_TO_COLORS = {"Chalice": (0, 255, 255), "Flame": (255, 0, 0), "Lion": (255, 255, 0), "Stone": (192, 192, 192)}
NAME_COORDINATES = ((120, 180), (1080, 180), (1080, 540), (120, 540))
ONE_CHARACTER_TO_NAME = {"D": "Diver", "E": "Engineer", "M": "Messenger", "N": "Navigator", "P": "Pilot", "X": "Explorer"}
NAME_TO_ONE_CHARACTER = {x: y for y, x in ONE_CHARACTER_TO_NAME.items()}
PLAYER_COLORS = {"D": (0, 0, 0), "E": (255, 0, 0), "M": (192, 192, 192), "N": (255, 255, 0), "P": (0, 0, 255), "X": (0, 255, 0)}
TILES = ("Breakers Bridge", "Bronze Gate", "Cave of Embers", "Cave of Shadows", "Cliffs of Abandon", "Copper Gate", "Coral Palace", "Crimson Forest", "Dunes of Deception", "Fools' Landing", "Gold Gate", "Howling Garden", "Iron Gate", "Lost Lagoon", "Misty Marsh", "Observatory", "Phantom Rock", "Silver Gate", "Temple of the Moon", "Temple of the Sun", "Tidal Palace", "Twilight Hollow", "Watchtower", "Whispering Garden")
TREASURES = {"Chalice": ("Coral Palace", "Tidal Palace"), "Flame": ("Cave of Embers", "Cave of Shadows"), "Lion": ("Howling Garden", "Whispering Garden"), "Stone": ("Temple of the Moon", "Temple of the Sun")}
TREASURE_CARDS = ("Chalice", "Flame", "Lion", "Stone", "Helicopter", "Sandbags", "Waters Rise")
WIDTHS = (240, 360, 480, 600, 720, 840)
HEIGHTS = (0, 120, 240, 360, 480, 600)
GRID_LOCATIONS = ((2, 0), (3, 0), (1, 1), (2, 1), (3, 1), (4, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (1, 4), (2, 4), (3, 4), (4, 4), (2, 5), (3, 5))
STARTING_POSITIONS = {"D": "Iron Gate", "E": "Bronze Gate", "M": "Silver Gate", "N": "Gold Gate", "P": "Fools' Landing", "X": "Copper Gate"}

def shuffled(obj, convert_type=list, return_type=None):
    if return_type is None:
        return_type = type(obj)
    temp = convert_type(obj)
    shuffle(temp)
    if return_type == str:
        return "".join(temp)
    else:
        return return_type(temp)
    
def tile_to_coordinates(tile):
    return (WIDTHS[GRID_LOCATIONS[tile][0]], HEIGHTS[GRID_LOCATIONS[tile][1]])

def lost_needed_tile(washed_away_tiles, claimed_treasures):
    if "Fools' Landing" in washed_away_tiles:
        return True
    for unclaimed_treasure in set(TREASURES.keys()) - claimed_treasures:
        if all(needed_tile in washed_away_tiles for needed_tile in TREASURES[unclaimed_treasure]):
            return True
    return False

def game_over():
    pygame.quit()
    sys.exit()

def transparent_blit(source, opacity):
    x = source.coordinates[0]
    y = source.coordinates[1]
    temp = pygame.Surface((source.size[0], source.size[1]) if type(source) != Text else source.tup_size).convert()
    temp.blit(DISPLAY, (-x, -y))
    temp.blit(source.image, (0, 0))
    temp.set_alpha(int(opacity * 2.55))        
    DISPLAY.blit(temp, source.rect)

def diver_tiles(flooded, washed_away, current_location):
    return __diver_tiles(flooded, washed_away, current_location) - {current_location}

def __diver_tiles(flooded, washed_away, current_location, already_searched=frozenset()):
    all_tiles = set()
    new_tiles = ADJACENT_TILES[current_location][0] - already_searched
    all_tiles |= new_tiles
    for tile in (flooded | washed_away) & new_tiles:
        all_tiles |= __diver_tiles(flooded, washed_away, tile, frozenset(all_tiles | already_searched))
    return all_tiles - washed_away

def can_shore_up_tiles(role, location, flooded_tiles):
    if role == "X":
        temp = (ADJACENT_TILES[location][0] | ADJACENT_TILES[location][1]) & (flooded_tiles)
    else:
        temp = ADJACENT_TILES[location][0] & flooded_tiles
    if location in flooded_tiles:
        temp.add(location)
    return temp, [ShoreUpIcon(x) for x in temp]

def get_mode():
    players = set()
    difficulty = None
    can_start = False
    ready_text = Text("Start", (600, 588), 60, (0, 255, 0))
    player_texts = [Text(*x, midleft=True) for x in (("Diver", (132, 144), 60, (0,) * 3), ("Engineer", (421, 144), 60, (255, 0, 0)), ("Explorer", (817, 144), 60, (0, 255, 0)), ("Messenger", (114, 288), 60, (192,) * 3), ("Navigator", (556, 288), 60, (255, 255, 0)), ("Pilot", (954, 288), 60, (0, 0, 255)))]
    difficulty_texts = [Text(*x, 60, (0,) * 3, midleft=True) for x in (("Novice", (67, 432)), ("Normal", (334, 432)), ("Elite", (616, 432)), ("Legendary", (818, 432)))]
    clicking = [False, False]
    while True:
        clicked_img = None
        DISPLAY.fill((127,) * 3)
        del clicking[0]
        clicking.append(pygame.mouse.get_pressed()[0])
        for img in [ready_text] + player_texts + difficulty_texts:
            if img == ready_text and not can_start:
                continue
            img.draw()
            if clicking == [False, True] and img.rect.collidepoint(*pygame.mouse.get_pos()):
                clicked_img = img
        if not clicked_img is None:
            if clicked_img == ready_text and can_start:
                return "".join(players), difficulty
            if clicked_img in player_texts:
                one_char = NAME_TO_ONE_CHARACTER[clicked_img.text]
                idx = player_texts.index(clicked_img)
                if one_char not in players and len(players) < 4:
                    players.add(one_char)
                    new_dict = player_texts[idx].__dict__
                    new_dict["white_bg"] = True
                    del new_dict["_Sprite__g"]
                    del new_dict["rect"]
                    del new_dict["image"]
                    del new_dict["tup_size"]
                    player_texts[idx] = Text(**new_dict)
                elif one_char in players:
                    players.remove(one_char)
                    new_dict = player_texts[idx].__dict__
                    new_dict["white_bg"] = False
                    del new_dict["_Sprite__g"]
                    del new_dict["rect"]
                    del new_dict["image"]
                    del new_dict["tup_size"]
                    player_texts[idx] = Text(**new_dict)
            if clicked_img in difficulty_texts and clicked_img.text != difficulty:
                idx = difficulty_texts.index(clicked_img)
                difficulty = clicked_img.text
                difficulty_texts = [Text(*x, 60, (0,) * 3, midleft=True) for x in (("Novice", (67, 432)), ("Normal", (334, 432)), ("Elite", (616, 432)), ("Legendary", (818, 432)))]
                new_dict = difficulty_texts[idx].__dict__
                new_dict["white_bg"] = True
                del new_dict["_Sprite__g"]
                del new_dict["rect"]
                del new_dict["image"]
                del new_dict["tup_size"]
                difficulty_texts[idx] = Text(**new_dict)
            can_start = (len(players) > 1 and difficulty)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
              game_over()
        pygame.display.update()
        FPS.tick(24)

def main(arg_players, arg_difficulty):
    treasure_deck = (["Chalice"] * 5) + (["Flame"] * 5) + (["Lion"] * 5) + (["Stone"] * 5) + (["Helicopter"] * 3) + (["Sandbags"] * 2)
    shuffle(treasure_deck)
    treasure_discard = []
    clicking = [False, False]
    flood_deck = shuffled(TILES, return_type=list)
    flood_discard = []
    layout = shuffled(TILES)
    players = arg_players
    players = shuffled(players)
    tiles = set(range(24))
    flooded_tiles = set()
    engineer_ability = False
    must_engineer_ability = False
    for tile in flood_deck[-6:]: # Amount of flooded tiles at beginning
        flooded_tiles.add(layout.index(tile))
        flood_discard.append(tile)
        tiles.remove(layout.index(tile))
        flood_deck.remove(tile)
    decks = {x: [] for x in players}
    for player in players:
        for _ in range(2):
            decks[player].append(treasure_deck.pop())
    player_indeces = {b: a for (a, b) in enumerate(players)}
    visible_decks = [Card(card, (player_indeces[player], idx)) for player, cards in decks.items() for idx, card in enumerate(cards)]
    for _ in range(3):
        treasure_deck.append("Waters Rise")
    shuffle(treasure_deck)
    shored_up_tiles = tiles
    washed_away_tiles = set()
    visible_tiles = [Tile(layout[tile_index], tile_index, idx) for idx, current_list in enumerate((shored_up_tiles, flooded_tiles)) for tile_index in current_list]
    visible_tiles.sort(key=Tile.get_idx)
    del tiles, _
    current_player = players[0]
    pilot_ability = (current_player == "P")
    player_locations = {x: layout.index(STARTING_POSITIONS[x]) for x in players}
    actions_remaining = 3
    visible_players = [Player(x, layout.index(STARTING_POSITIONS[x]), idx) for idx, x in enumerate(players)]
    can_shore_up, visible_shore_up = can_shore_up_tiles(current_player, player_locations[current_player], flooded_tiles)
    name_indicators = [Text(ONE_CHARACTER_TO_NAME[x] + ("" if x != current_player else " 3"), NAME_COORDINATES[idx], 35, PLAYER_COLORS[x]) for idx, x in enumerate(players)]
    normal_mode = True
    asking_card_receiver = False
    discarding = False
    just_escaped = False
    drawing = [False, False]
    announcements = []
    water_meter_height = WATER_METERS[arg_difficulty]
    claimed_treasures = set()
    waiting = False, None
    frame = 0
    exit_after_wait = False
    escaping_flood = False
    finish_turn_after_waiting = False
    reshuffle_announcements = []
    undo_text = Text("Undo turn", (1122, 240), 20, (255, 0, 0))
    visible_treasures = [Image("Chalice Treasure", (51, 88), (300, 164), True), Image("Flame Treasure", (65, 88), (900, 164), True), Image("Lion Treasure", (70, 84), (300, 540), True), Image("Stone Treasure", (53, 81), (900, 540), True)]
    state_before_turn = tuple(deepcopy(x) for x in (claimed_treasures, treasure_discard, flooded_tiles, shored_up_tiles, decks, pilot_ability, player_locations, can_shore_up))
    can_undo = False
    just_finished_waiting = False
    viewing_discard = False
    end_viewing_discard = False
    exit_icon = []
    need_continue = False
    treasures = [False, False]
    using_special_card = False
    just_used_special_card = False
    discarding_after_drawing = False
    no_draws_yet = False
    special_undo = False
    used_special_card_last_time = False
    no_discard_sprite = Text("No cards in flood discard", (600, 360), 40, (0,) * 3)
    done = False
    visible_water_meter_indicator = Image("Water Meter Indicator", (40, 10), (980, WATER_METER_LEVEL_HEIGHTS[water_meter_height]))
#   =============================================================================================================================================================================================================================================================================================
#   =============================================================================================================================================================================================================================================================================================
    while True:
        if just_escaped:
            just_escaped = False
        if just_used_special_card:
            just_used_special_card = False
        if end_viewing_discard:
            viewing_discard = False
            end_viewing_discard = False
        DISPLAY.fill((80,) * 3)
        if len(claimed_treasures) == 4 and all(player_locations[x] == layout.index("Fools' Landing") for x in players) and (treasure_discard.count("Helicopter") + treasure_deck.count("Helicopter")) < 3 and not done:
            print("Congratulations! You escaped the island!")
            done = True
            opacity = 100
            fools_landing = visible_tiles[layout.index("Fools' Landing")]
            del visible_tiles[layout.index("Fools' Landing")]
        if not done:
            for img in (visible_tiles if flood_discard or not viewing_discard else [no_discard_sprite]) + (visible_shore_up + announcements + visible_players + visible_decks + visible_treasures + reshuffle_announcements + [VISIBLE_WATER_METER, visible_water_meter_indicator] + ([VIEW_DISCARD_PILES] if not using_special_card else []) + ([END_TURN] if not drawing[0] and not discarding and not asking_card_receiver and not using_special_card else []) if not viewing_discard else discard_sprites) + exit_icon + ([undo_text] if can_undo and not viewing_discard and (normal_mode or drawing) and not discarding and not asking_card_receiver else []):
                img.draw()
            if not viewing_discard and not using_special_card:
                for name in name_indicators:
                    name.draw((NAME_TO_ONE_CHARACTER[name.text.split()[0]] == current_player if not done else False))
        else:
            for img in visible_tiles + visible_decks + visible_treasures + name_indicators + [VISIBLE_WATER_METER, visible_water_meter_indicator]:
                transparent_blit(img, opacity)
            fools_landing.draw()
            for img in visible_players:
                img.draw()
            pygame.display.update()
            FPS.tick(24)
            opacity -= 2
            frame += 1
            if opacity == -2:
                game_over()
            continue
        if discarding and not viewing_discard:
            for img in xs:
                img.draw(False, True)
        if waiting[0]:
            if not waiting[2] is None and type(waiting[2]) != tuple:
                waiting[2].draw()
            if type(waiting[2]) == tuple:
                waiting[2][current_idx].draw()
                for img in visible_players:
                    img.draw()
                if frame == start_frame + waiting[1][current_idx]:
                    current_idx += 1
                    start_frame = frame
                    if current_idx == len(waiting[1]):
                        waiting = False, None
                        just_finished_waiting = True
                        if exit_after_wait:
                            game_over()
                        if finish_turn_after_waiting and not escaping_flood:
                            finish_turn_after_waiting = False
                            normal_mode = True
                            announcements = []
                            drawing = [False, False]
                            current_player = players[player_indeces[current_player] - len(players) + 1]
                            pilot_ability = (current_player == "P")
                            original = name_indicators[player_indeces[current_player]]
                            name_indicators[player_indeces[current_player]] = Text(original.text + " 3", original.coordinates, original.size, original.color)
                            can_shore_up, visible_shore_up = can_shore_up_tiles(current_player, player_locations[current_player], flooded_tiles)
                            state_before_turn = tuple(deepcopy(x) for x in (claimed_treasures, treasure_discard, flooded_tiles, shored_up_tiles, decks, pilot_ability, player_locations, can_shore_up))
            elif frame == start_frame + waiting[1]:
                waiting = False, None
                if exit_after_wait:
                    game_over()
        if just_finished_waiting:
            just_finished_waiting = False
            if escaping_flood:
                current_escaper = escaping_players[0]
                announcements = [Text("Click on tile for", (120, 345), 20, (255,) * 3), Text(f"{ONE_CHARACTER_TO_NAME[current_escaper]} to escape to", (120, 375), 20, (255,) * 3)]
                for player in escaping_players:
                    if player in {"P", "D"}:
                        continue
                    if player == "X":
                        if all(escape_tile in washed_away_tiles for escape_tile in (ADJACENT_TILES[player_locations["X"]][0] | ADJACENT_TILES[player_locations["X"]][1])):
                            print("Game has been lost due to the Explorer sinking.")
                            game_over()
                    elif all(escape_tile in washed_away_tiles for escape_tile in ADJACENT_TILES[player_locations[player]][0]):
                        print(f"Game has been lost due to the {ONE_CHARACTER_TO_NAME[player]} sinking.")
                        game_over()
        del clicking[0]
        clicking.append(pygame.mouse.get_pressed()[0])
        if not frame:
            clicking = [True, True]
        if viewing_discard:
            if clicking == [False, True] and exit_icon[0].rect.collidepoint(*pygame.mouse.get_pos()):
                exit_icon = []
                end_viewing_discard = True
        if clicking == [False, True] and VIEW_DISCARD_PILES.rect.collidepoint(*pygame.mouse.get_pos()) and not viewing_discard and not using_special_card and not waiting[0]:
            viewing_discard = True
            exit_icon = [Text("Go back", (120, 360), 25, (255,) * 3)]
            coords = tuple(51 + (x * 103) for x in range(7))
            discard_sprites = [Image("Discard Indicator", (30, 30), tuple(y + 60 for y in tile_to_coordinates(layout.index(x)))) for x in flood_discard] + [Image("Discarded Cards", (69, 720), (994, 360))] + [Text(f"x{treasure_discard.count(x)}", (1080, coords[idx]), 30, (0,) * 3) for idx, x in enumerate(TREASURE_CARDS)]
        if clicking == [False, True] and (normal_mode or any(drawing)) and not viewing_discard and can_undo and not using_special_card and undo_text.rect.collidepoint(*pygame.mouse.get_pos()):
            actions_remaining = 3
            treasures = [False, False]
            special_undo = False
            if no_draws_yet:
                drawing = [False, False]
                normal_mode = True
                announcements = []
            elif drawing[0]:
                special_undo = True
                must_engineer_ability = False
                engineer_ability = False
            dont_continue = True
            engineer_ability = False
            claimed_treasures, treasure_discard, flooded_tiles, shored_up_tiles, decks, pilot_ability, player_locations, can_shore_up = deepcopy(state_before_turn)
            visible_treasures = [Image("Chalice Treasure", (51, 88), (300, 164), "Chalice" not in claimed_treasures), Image("Flame Treasure", (65, 88), (900, 164), "Flame" not in claimed_treasures), Image("Lion Treasure", (70, 84), (300, 540), "Lion" not in claimed_treasures), Image("Stone Treasure", (53, 81), (900, 540), "Stone" not in claimed_treasures)]
            visible_decks = [Card(card, (player_indeces[player], idx)) for player, cards in decks.items() for idx, card in enumerate(cards)]
            visible_tiles = [Tile(layout[tile_index], tile_index, idx) for idx, current_list in enumerate((shored_up_tiles, flooded_tiles, washed_away_tiles)) for tile_index in current_list]
            visible_tiles.sort(key=Tile.get_idx)
            visible_players = [Player(x, player_locations[x], idx) for idx, x in enumerate(players)]
            if special_undo:
                special_undo = False
                visible_shore_up = []
                for a_player, deck in decks.items():
                    if len(deck) > 5:
                        discarding = True
                        normal_mode = False
                        announcements = [Text("Discard cards", (120, 360), 25, (255, 0, 0))]
                        xs = [Text("x", ((1128 - (idx * 72) if player_indeces[a_player] % 3 else idx * 72), (0 if player_indeces[a_player] < 2 else 612)), 18, (255, 0, 0), True) for idx in range(len(decks[a_player]))]
                        break
            else:
                delete, visible_shore_up = can_shore_up_tiles(current_player, player_locations[current_player], flooded_tiles)
                del delete
                original = name_indicators[player_indeces[current_player]]
                name_indicators[player_indeces[current_player]] = Text((original.text + " 3" if original.text[-1] in "rt" else original.text[:-1] + "3"), original.coordinates, original.size, original.color)
            can_undo = False
            pygame.display.update()
            FPS.tick(24)
            continue
        else:
            dont_continue = False
        if clicking == [False, True] and escaping_flood and not viewing_discard and not waiting[0]:
            if current_escaper == "P":
                escape_tiles = [visible_tiles[x] for x in range(24) if x not in washed_away_tiles]
            elif current_escaper == "D":
                escape_tiles = [visible_tiles[x] for x in diver_tiles(flooded_tiles, washed_away_tiles, player_locations["D"])]
            elif current_escaper == "X":
                escape_tiles = [visible_tiles[x] for x in (ADJACENT_TILES[player_locations["X"]][0] | ADJACENT_TILES[player_locations["X"]][1]) if x not in washed_away_tiles]
            else:
                escape_tiles = [visible_tiles[x] for x in ADJACENT_TILES[player_locations[current_escaper]][0] if x not in washed_away_tiles]
            if not escape_tiles:
                raise Exception("Should be a tile to go to")
            for tile in escape_tiles:
                if tile.rect.collidepoint(*pygame.mouse.get_pos()):
                    escaping_players.remove(current_escaper)
                    escaping_flood = bool(escaping_players)
                    player_locations[current_escaper] = tile.index
                    visible_players[player_indeces[current_escaper]] = Player(current_escaper, tile.index, player_indeces[current_escaper])
                    if not escaping_flood and flood_cards_drawn == WATER_METER[water_meter_height]:
                        normal_mode = True
                        announcements = []
                        drawing = [False, False]
                        current_player = players[player_indeces[current_player] - len(players) + 1]
                        pilot_ability = (current_player == "P")
                        original = name_indicators[player_indeces[current_player]]
                        name_indicators[player_indeces[current_player]] = Text(original.text + " 3", original.coordinates, original.size, original.color)
                        can_shore_up, visible_shore_up = can_shore_up_tiles(current_player, player_locations[current_player], flooded_tiles)
                        state_before_turn = tuple(deepcopy(x) for x in (claimed_treasures, treasure_discard, flooded_tiles, shored_up_tiles, decks, pilot_ability, player_locations, can_shore_up))
                        need_continue = True
                        break
                    elif escaping_flood:
                        current_escaper = escaping_players[0]
                        announcements[1] = Text(f"{ONE_CHARACTER_TO_NAME[current_escaper]} to escape to", (120, 375), 20, (255,) * 3)
                    else:
                        just_escaped = True
                        announcements = [Text("Click to draw", (120, 345), 28, (255,) * 3), Text("flood cards", (120, 375), 28, (255,) * 3)]
            if need_continue:
                need_continue = False
                pygame.display.update()
                FPS.tick(24)
                continue
        if clicking == [False, True] and not escaping_flood and not just_escaped and not viewing_discard and not asking_card_receiver and not treasures[1]:
            for (special_card, idx) in [(x, idx) for (idx, x) in enumerate(visible_decks) if x.card in {"Helicopter", "Sandbags"}]:
                if special_card.rect.collidepoint(*pygame.mouse.get_pos()) and (all((not x.rect.collidepoint(*pygame.mouse.get_pos())) for x in xs) if discarding else True):
                    if special_card.card == "Sandbags" and not flooded_tiles:
                        break
                    using_special_card = True
                    engineer_ability = False
                    must_engineer_ability = False
                    player_obtained_from = players[special_card.indeces[0]]
                    idx_clicked = special_card.indeces[1]
                    special_card_type = special_card.card
                    temp_name_indicators = name_indicators
                    temp_announcements = announcements
                    if any(drawing) and not used_special_card_last_time:
                        state_before_turn = tuple(deepcopy(x) for x in (claimed_treasures, treasure_discard, flooded_tiles, shored_up_tiles, decks, pilot_ability, player_locations, can_shore_up))
                    announcements = []
                    selected_players = []
                    name_indicators = [Text(ONE_CHARACTER_TO_NAME[x], NAME_COORDINATES[idx], 35, PLAYER_COLORS[x]) for idx, x in enumerate(players)]
                    if special_card_type == "Sandbags":
                        special_card_announcements = [Text("Click on tile", (120, 345), 28, (255,) * 3), Text("to shore up", (120, 375), 28, (255,) * 3)]
                        visible_shore_up = [ShoreUpIcon(x) for x in flooded_tiles]
                    else:
                        special_card_announcements = [Text("Click on players to", (120, 330), 25, (255,) * 3), Text("put in helicopter.", (120, 360), 25, (255,) * 3), Text("Then, click on destination", (120, 390), 25, (255,) * 3)]
                        visible_shore_up = []
                        players_in_heli = set()
                    used_special_card_last_time = True
                    break
        if using_special_card:
            for img in special_card_announcements:
                img.draw()
            for img in name_indicators:
                img.draw(False, img.text in selected_players)
            if clicking == [False, True]:
                success = False
                if special_card_type == "Sandbags":
                    for icon in visible_shore_up:
                        if icon.rect.collidepoint(*pygame.mouse.get_pos()):
                            treasure_discard.append("Sandbags")
                            visible_tiles[icon.index] = Tile(layout[icon.index], icon.index, 0)
                            flooded_tiles.remove(icon.index)
                            shored_up_tiles.add(icon.index)
                            if icon.index in can_shore_up:
                                can_shore_up.remove(icon.index)
                            if any(drawing):
                                visible_shore_up = []
                            else:
                                visible_shore_up = [ShoreUpIcon(x) for x in can_shore_up]
                            success = True
                elif special_card_type == "Helicopter":
                    for idx, name in enumerate(name_indicators):
                        if name.rect.collidepoint(*pygame.mouse.get_pos()):
                            traveling_player = NAME_TO_ONE_CHARACTER[name.text]
                            if traveling_player in players_in_heli:
                                players_in_heli.remove(traveling_player)
                            elif all(player_locations[x] == player_locations[traveling_player] for x in players_in_heli):
                                players_in_heli.add(traveling_player)
                            name_indicators[idx] = Text(name.text, name.coordinates, name.size, name.color, white_bg=(traveling_player in players_in_heli))
                    for tile in visible_tiles:
                        for x in players_in_heli:
                            break
                        if tile.state == 2 or not players_in_heli or tile.index == player_locations[x]:
                            continue
                        if tile.rect.collidepoint(*pygame.mouse.get_pos()):
                            success = True
                            treasure_discard.append("Helicopter")
                            for player in players_in_heli:
                                player_locations[player] = tile.index
                                visible_players[player_indeces[player]] = Player(player, tile.index, player_indeces[player])
                            if not any(drawing):
                                can_shore_up, visible_shore_up = can_shore_up_tiles(current_player, player_locations[current_player], flooded_tiles)
                if success:
                    can_undo = True
                    using_special_card = False
                    name_indicators = temp_name_indicators
                    del temp_name_indicators
                    del decks[player_obtained_from][idx_clicked]
                    visible_decks = [Card(card, (player_indeces[player], idx)) for player, cards in decks.items() for idx, card in enumerate(cards)]
                    just_used_special_card = True
                    announcements = temp_announcements
                    if not actions_remaining and not any(drawing):
                        actions_remaining = 3
                        drawing = [True, True]
                        original = name_indicators[player_indeces[current_player]]
                        name_indicators[player_indeces[current_player]] = Text((original.text[:-2]), original.coordinates, original.size, original.color)
                        normal_mode = False
                        engineer_ability = False
                        must_engineer_ability = False
                    del temp_announcements
                    if not any(drawing):
                        normal_mode = True
                    if discarding and len(decks[discarding_player]) <= 5:
                        discarding = False
                        if discarding_after_drawing:
                            continue_ok = True
                            announcements = [Text("Click to draw", (120, 345), 28, (255,) * 3), Text("flood cards", (120, 375), 28, (255,) * 3)]
                        else:
                            announcements = []
                    elif discarding and player_obtained_from == discarding_player:
                        del xs[-1]
        elif drawing[0] and clicking == [False, True] and not waiting[0] and not escaping_flood and not just_escaped and not viewing_discard and not discarding:
            can_undo = False
            reshuffle_announcements = []
            if treasures[1]:
                used_special_card_last_time = False
                card_type = treasure_deck.pop()
                no_draws_yet = False
                if card_type == "Waters Rise":
                    treasure_discard.append("Waters Rise")
                if not treasure_deck:
                    treasure_deck = shuffled(treasure_discard)
                    treasure_discard = []
                    reshuffle_announcements = [Text("Treasure discard", (1122, 340), 18, (255, 0, 0)), Text("has been reshuffled", (1122, 370), 15, (255, 0, 0))]
                if card_type == "Waters Rise":
                    waiting = True, 36, Card("Waters Rise", None, ((600, 360), (360, 540)))
                    exit_after_wait = False
                    start_frame = frame
                    water_meter_height += 1
                    visible_water_meter_indicator = Image("Water Meter Indicator", (40, 10), (980, WATER_METER_LEVEL_HEIGHTS[water_meter_height]))
                    if WATER_METER[water_meter_height] is None:
                        print("Game has been lost due to the water meter raising too high.")
                        exit_after_wait = True
                    else:
                        flood_deck.extend(shuffled(flood_discard))
                        flood_discard = []
                else:
                    decks[current_player].append(card_type)
                    visible_decks.append(Card(card_type, (player_indeces[current_player], len(decks[current_player]) - 1)))
                if treasures[0]:
                    treasures[0] = False
                else:
                    treasures = False, False
                    if len(decks[current_player]) > 5:
                        discarding = True
                        xs = [Text("x", ((1128 - (idx * 72) if player_indeces[current_player] % 3 else idx * 72), (0 if player_indeces[current_player] < 2 else 612)), 18, (255, 0, 0), True) for idx in range(len(decks[current_player]))]
                        discarding_after_drawing = True
                        discarding_player = current_player
                        continue_ok = False
                        announcements = [Text("Discard cards", (120, 360), 25, (255, 0, 0))]
                    else:
                        announcements[1] = Text("flood cards", (120, 375), 28, (255,) * 3)
                        continue_ok = True
            elif continue_ok and not special_undo:
                if discarding:
                    discarding = False
                flood_cards_drawn += 1
                can_undo = False
                flooded_tile = flood_deck.pop()
                flooded_tile_idx = layout.index(flooded_tile)
                if flooded_tile_idx in shored_up_tiles:
                    flood_discard.append(flooded_tile)
                    shored_up_tiles.remove(flooded_tile_idx)
                    flooded_tiles.add(flooded_tile_idx)
                    visible_tiles[flooded_tile_idx] = Tile(flooded_tile, flooded_tile_idx, 1)
                else:
                    flooded_tiles.remove(flooded_tile_idx)
                    washed_away_tiles.add(flooded_tile_idx)
                    visible_tiles[flooded_tile_idx] = Tile(flooded_tile, flooded_tile_idx, 2)
                    current_idx = 0
                    waiting = True, ((6,) * 4), ((Tile(flooded_tile, flooded_tile_idx, 0), Tile(flooded_tile, flooded_tile_idx, 1)) * 2)
                    start_frame = frame
                    if lost_needed_tile([layout[x] for x in washed_away_tiles], claimed_treasures):
                        exit_after_wait = True
                        print(f"Game has been lost due to losing the {flooded_tile} tile.")
                    escaping_players = [x for x in players if player_locations[x] == flooded_tile_idx]
                    escaping_flood = bool(escaping_players)
                if not flood_deck:
                    flood_deck = shuffled(flood_discard)
                    flood_discard = []
                    reshuffle_announcements = [Text("Flood discard", (1122, 340), 20, (255, 0, 0)), Text("has been reshuffled", (1122, 370), 15, (255, 0, 0))]
                if flood_cards_drawn == WATER_METER[water_meter_height]:
                    if waiting[0]:
                        finish_turn_after_waiting = True
                    else:
                        normal_mode = True
                        announcements = []
                        drawing = [False, False]
                        current_player = players[player_indeces[current_player] - len(players) + 1]
                        pilot_ability = (current_player == "P")
                        original = name_indicators[player_indeces[current_player]]
                        name_indicators[player_indeces[current_player]] = Text(original.text + " 3", original.coordinates, original.size, original.color)
                        can_shore_up, visible_shore_up = can_shore_up_tiles(current_player, player_locations[current_player], flooded_tiles)
                        state_before_turn = tuple(deepcopy(x) for x in (claimed_treasures, treasure_discard, flooded_tiles, shored_up_tiles, decks, pilot_ability, player_locations, can_shore_up))
                        pygame.display.update()
                        FPS.tick(24)
                        continue
        if clicking == [False, True] and normal_mode and not dont_continue and not viewing_discard and not using_special_card and not just_used_special_card:
            start_actions = actions_remaining
            dont_move = False
            skip_all = False
            if END_TURN.rect.collidepoint(*pygame.mouse.get_pos()):
                skip_all = True
                actions_remaining = 0
                turn_ended = True
            else:
                turn_ended = False
                for card in visible_decks:
                    if card.rect.collidepoint(*pygame.mouse.get_pos()) and card.card not in {"Helicopter", "Sandbags"} and card.indeces[0] == player_indeces[current_player]:
                        reachable_players = [player for player in players if player != current_player and (current_player == "M" or player_locations[player] == player_locations[current_player])]
                        if not reachable_players:
                            skip_all = True
                            break
                        elif len(reachable_players) == 1:
                            engineer_ability, must_engineer_ability = False, False
                            visible_shore_up = [ShoreUpIcon(x.index) for x in visible_shore_up]
                            decks[reachable_players[0]].append(card.card)
                            del decks[current_player][card.indeces[1]]
                            visible_decks = [Card(card, (player_indeces[player], idx)) for player, cards in decks.items() for idx, card in enumerate(cards)]
                            skip_all = True
                            engineer_ability = False
                            must_engineer_ability = False
                            actions_remaining -= 1
                            can_undo = True
                            if len(decks[reachable_players[0]]) > 5:
                                original = name_indicators[player_indeces[current_player]]
                                name_indicators[player_indeces[current_player]] = Text(original.text[:-1] + str(actions_remaining), original.coordinates, original.size, original.color)
                                discarding = True
                                xs = [Text("x", ((1128 - (idx * 72) if player_indeces[reachable_players[0]] % 3 else idx * 72), (0 if player_indeces[reachable_players[0]] < 2 else 612)), 18, (255, 0, 0), True) for idx in range(len(decks[reachable_players[0]]))]
                                discarding_after_drawing = False
                                discarding_player = reachable_players[0]
                                normal_mode = False
                                announcements.append(Text("Discard cards", (120, 360), 25, (255, 0, 0)))
                            break
                        else:
                            engineer_ability, must_engineer_ability = False, False
                            temp_visible_shore_up = [ShoreUpIcon(x.index) for x in visible_shore_up]
                            visible_shore_up = []
                            normal_mode = False
                            engineer_ability, must_engineer_ability = False, False
                            asking_card_receiver = True
                            announcements.append(Text(f"Select receiver of the {card.card}", (120, 360), 16, TREASURES_TO_COLORS[card.card]))
                            break
                for treasure in set(TREASURES.keys()) - claimed_treasures:
                    visble, idx = [(x, idx) for (idx, x) in enumerate(visible_treasures) if x.name.split()[0] == treasure][0]
                    if visble.rect.collidepoint(*pygame.mouse.get_pos()) and decks[current_player].count(treasure) >= 4 and layout[player_locations[current_player]] in TREASURES[treasure]:
                        claimed_treasures.add(treasure)
                        actions_remaining -= 1
                        original = visible_treasures[idx]
                        visible_treasures[idx] = Image(original.name, original.size, original.coordinates)
                        for _ in range(4):
                            treasure_discard.append(treasure)
                            decks[current_player].remove(treasure)
                        visible_decks = [Card(card, (player_indeces[player], idx)) for player, cards in decks.items() for idx, card in enumerate(cards)]
                        skip_all = True
                        break
            if not skip_all:
                for indicator in visible_shore_up:
                    if indicator.rect.collidepoint(*pygame.mouse.get_pos()):
                        can_undo = True
                        if not engineer_ability:
                            undo_engineer = False
                            actions_remaining -= 1
                            if current_player == "E":
                                engineer_ability = True
                        else:
                            undo_engineer = True
                            engineer_ability = False
                            must_engineer_ability = False
                        dont_move = True
                        location = indicator.index
                        can_shore_up.remove(location)
                        for idx in range(len(visible_shore_up)):
                            if visible_shore_up[idx].index == location:
                                del visible_shore_up[idx]
                                break
                        if engineer_ability:
                            for idx, icon in enumerate(visible_shore_up):
                                visible_shore_up[idx] = ShoreUpIcon(icon.index, True)
                        elif undo_engineer:
                            for idx, icon in enumerate(visible_shore_up):
                                visible_shore_up[idx] = ShoreUpIcon(icon.index)
                        flooded_tiles.remove(location)
                        shored_up_tiles.add(location)
                        old_tile = visible_tiles[location]
                        visible_tiles[location] = Tile(old_tile.name, old_tile.index, 0)
                if not dont_move and not must_engineer_ability:
                    if pilot_ability:
                        searched_tiles = (flooded_tiles | shored_up_tiles) - {player_locations["P"]}
                    else:
                        searched_tiles = (ADJACENT_TILES[player_locations[current_player]][0] - washed_away_tiles if current_player not in "XD" else ((ADJACENT_TILES[player_locations[current_player]][0] | ADJACENT_TILES[player_locations[current_player]][1]) - washed_away_tiles if current_player == "X" else diver_tiles(flooded_tiles, washed_away_tiles, player_locations["D"])))
                    for reachable_tile in searched_tiles:
                        if visible_tiles[reachable_tile].rect.collidepoint(*pygame.mouse.get_pos()):
                            if pilot_ability and reachable_tile not in ADJACENT_TILES[player_locations["P"]][0]:
                                pilot_ability = False
                            actions_remaining -= 1
                            can_undo = True
                            engineer_ability = False
                            player_locations[current_player] = reachable_tile
                            visible_players[player_indeces[current_player]] = Player(current_player, reachable_tile, player_indeces[current_player])
                            can_shore_up, visible_shore_up = can_shore_up_tiles(current_player, reachable_tile, flooded_tiles)
                            break
            if not actions_remaining and ((not can_shore_up or not engineer_ability) or turn_ended) and normal_mode:
                actions_remaining = 3
                drawing = [True, True]
                original = name_indicators[player_indeces[current_player]]
                name_indicators[player_indeces[current_player]] = Text((original.text[:-2] if normal_mode else original.text[:-1] + "0"), original.coordinates, original.size, original.color)
                normal_mode = False
                engineer_ability = False
                must_engineer_ability = False
            elif not actions_remaining and can_shore_up and normal_mode:
                must_engineer_ability = True
            if (start_actions - actions_remaining != 0 or turn_ended) and normal_mode:
                original = name_indicators[player_indeces[current_player]]
                name_indicators[player_indeces[current_player]] = Text((original.text[:-2] if actions_remaining != 3 else original.text) + " " + str(actions_remaining), original.coordinates, original.size, original.color)
        elif clicking == [False, True] and asking_card_receiver and not viewing_discard and not using_special_card:
            for indicator in name_indicators:
                player = NAME_TO_ONE_CHARACTER[indicator.text if indicator.text in NAME_TO_ONE_CHARACTER else indicator.text[:-2]]
                if indicator.rect.collidepoint(*pygame.mouse.get_pos()) and player in reachable_players:
                        decks[player].append(card.card)
                        del decks[current_player][card.indeces[1]]
                        visible_decks = [Card(card, (player_indeces[player], idx)) for player, cards in decks.items() for idx, card in enumerate(cards)]
                        normal_mode = True
                        asking_card_receiver = False
                        engineer_ability = False
                        must_engineer_ability = False
                        actions_remaining -= 1
                        can_undo = True
                        del announcements[0]
                        visible_shore_up = temp_visible_shore_up
                        del temp_visible_shore_up
                        if len(decks[player]) > 5:
                            discarding = True
                            xs = [Text("x", ((1128 - (idx * 72) if player_indeces[player] % 3 else idx * 72), (0 if player_indeces[player] < 2 else 612)), 18, (255, 0, 0), True) for idx in range(len(decks[player]))]
                            discarding_after_drawing = False
                            normal_mode = False
                            announcements.append(Text("Discard cards", (120, 360), 25, (255, 0, 0)))
                            temp_visible_shore_up = visible_shore_up
                            visible_shore_up = []
                            discarding_player = player
                        original = name_indicators[player_indeces[current_player]]
                        if actions_remaining:
                            name_indicators[player_indeces[current_player]] = Text(original.text[:-2] + " " + str(actions_remaining), original.coordinates, original.size, original.color)
                        else:
                            original = name_indicators[player_indeces[current_player]]
                            if normal_mode:
                                actions_remaining = 3
                                drawing = [True, True]
                                normal_mode = False
                                name_indicators[player_indeces[current_player]] = Text(original.text[:-2], original.coordinates, original.size, original.color)
                                engineer_ability = False
                                must_engineer_ability = False
                            else:
                                name_indicators[player_indeces[current_player]] = Text(original.text[:-1] + "0", original.coordinates, original.size, original.color)
                        break
        elif clicking == [False, True] and discarding and not viewing_discard and not using_special_card:
            for ((idx, card), xss) in zip(enumerate([x for x in visible_decks if x.indeces[0] == player_indeces[discarding_player]]), xs):
                if xss.rect.collidepoint(*pygame.mouse.get_pos()):
                    del decks[discarding_player][card.indeces[1]]
                    visible_decks = [Card(card, (player_indeces[player], idx)) for player, cards in decks.items() for idx, card in enumerate(cards)]
                    treasure_discard.append(card.card)
                    if len(decks[discarding_player]) == 5:
                        xs = []
                        normal_mode = not discarding_after_drawing
                        discarding = False
                        try:
                            temp_visible_shore_up
                        except NameError:
                            temp_visible_shore_up = visible_shore_up
                        visible_shore_up = temp_visible_shore_up
                        del temp_visible_shore_up
                        if discarding_after_drawing:
                            announcements = [Text("Click to draw", (120, 345), 28, (255,) * 3), Text("flood cards", (120, 375), 28, (255,) * 3)]
                            continue_ok = True
                        else:
                            del announcements[0]
                        if not actions_remaining:
                            original = name_indicators[player_indeces[current_player]]
                            actions_remaining = 3
                            name_indicators[player_indeces[current_player]] = Text(original.text[:-2], original.coordinates, original.size, original.color)
                            engineer_ability = False
                            must_engineer_ability = False
                            drawing = [True, True]
                            normal_mode = False
                    else:
                        del xs[-1]
                    break
        if drawing[1]:
            drawing[1] = False
            no_draws_yet = True
            flood_cards_drawn = 0
            visible_shore_up = []
            announcements.append(Text("Click to draw", (120, 345), 28, (255,) * 3))
            announcements.append(Text("treasure cards", (120, 375), 28, (255,) * 3))
            treasures = [True, True]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
              game_over()
        if clicking == [False, True]:
            print(actions_remaining)
        pygame.display.update()
        FPS.tick(24)
        frame += 1


if __name__ == "__main__":
    main(*get_mode())
