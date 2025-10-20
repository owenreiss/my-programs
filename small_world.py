import pygame
import sys

from copy import copy
from os import chdir
from random import shuffle, randint
from time import perf_counter

pygame.init()
chdir("/Users/owenreiss/Desktop/Coding/python/small_world")

class Polygon:
    def __init__(self, points):
        self.points = tuple((x[0] - 4, x[1]) for x in points)
        math_points = tuple(pygame_to_math_point(x) for x in self.points)
        lines = []
        y_ranges = []
        for idx, first_point in enumerate(math_points):
            second_point = math_points[idx + 1 if idx != len(self.points) - 1 else 0]
            if second_point[0] == first_point[0]:
                raise Exception(f"Cannot have vertical line, x value is {first_point[0]}")
            slope = (second_point[1] - first_point[1]) / (second_point[0] - first_point[0])
            if slope == 0:
                raise Exception(f"Cannot have flat line, y value is {pygame_to_math_point((0, second_point[1]))[1]}")
            y_intercept = first_point[1] - slope * first_point[0]
            lines.append((slope, y_intercept))
            y_ranges.append(sorted((first_point[1], second_point[1])))
        self.lines = lines
        self.y_ranges = y_ranges

    def contains(self, arg_point):
        """input pygame point, not math point"""
        math_point = pygame_to_math_point(arg_point)
        math_point = (math_point[0] + 0.2, math_point[1])
        vertical_intersections = 0
        for line, y_range in zip(self.lines, self.y_ranges):
            # intersection going vertical from arg_point
            y_intersection_value = line[0] * math_point[0] + line[1]

            if y_range[0] < y_intersection_value < y_range[1] and y_intersection_value > math_point[1]:
                vertical_intersections += 1

        return bool(vertical_intersections % 2) # even intersections means outside

    def draw(self, constant_color=None):
        """red is first, violet is last"""
        amount_of_points = len(self.points)
        for idx, first_point in enumerate(self.points):
            second_point = self.points[idx + 1 if idx != len(self.points) - 1 else 0]
            pygame.draw.line(DISPLAY, rainbow_to_rgb(idx / amount_of_points) if constant_color is None else constant_color, first_point, second_point, 3)

    def draw_points(self, color=(255, 0, 0)):
        for point in self.points:
            pygame.draw.rect(DISPLAY, color, pygame.Rect(point[0] - 2, point[1] - 2, 5, 5))

class Text(pygame.sprite.Sprite):
    def __init__(self, text, location, size, color=(0,0,0), reference_point="topleft"):
        super().__init__()
        self.size = size
        self.image = pygame.font.Font("freesansbold.ttf", size).render(text, True, color)
        self.text = text
        self.color = color
        self.rect = self.image.get_rect()
        self.location = location
        exec(f"self.rect.{reference_point} = location")

    def draw(self):
        DISPLAY.blit(self.image, self.rect)

class Image(pygame.sprite.Sprite):
    def __init__(self, name, location, reference_point="topleft", dimensions=None, grayscale=False):
        super().__init__()
        self.name = name
        self.grayscale = grayscale
        self.location = location
        self.image = pygame.image.load(name + ".png")
        if grayscale:
            self.image = pygame.transform.grayscale(self.image)
        if dimensions is not None:
            self.image = pygame.transform.smoothscale(self.image, dimensions)
        self.rect = self.image.get_rect()
        exec(f"self.rect.{reference_point} = location")

    def draw(self):
        DISPLAY.blit(self.image, self.rect)

class RaceToken(pygame.sprite.Sprite):
    def __init__(self, race, location, amount, declined):
        super().__init__()
        self.race = race
        self.location = location
        self.amount = amount
        self.declined = declined
        self.images = [pygame.image.load(race + ("_token.png" if race != "hero" and race != "fortress" else ".png"))]
        if amount != 1:
            self.images.extend([Rect(location[0] + 13, location[1] + 8, 12, 17, (0, 0, 0)), Text(str(amount), (location[0] + 19, location[1] + 18), 15, (255, 255, 255), "center")])
        if declined:
            self.images[0] = pygame.transform.grayscale(self.images[0])
        self.images[0] = pygame.transform.smoothscale(self.images[0], (50, 50))
        self.rect = self.images[0].get_rect()
        self.rect.center = location
        self.images = tuple(self.images)

    def draw(self):
        for idx, image in enumerate(self.images):
            if idx == 0:
                DISPLAY.blit(image, self.rect)
            else:
                image.draw()

class Rect(pygame.sprite.Sprite):
    def __init__(self, left, top, width, height, color):
        super().__init__()
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.color = color

    def draw(self):
        pygame.draw.rect(DISPLAY, self.color, pygame.Rect(self.left, self.top, self.width, self.height))

class Player(pygame.sprite.Sprite):
    def __init__(self, index, name, coins, race, power, unused_tokens, declined_race=None, finished_profile=True, show_unused_tokens=False):
        super().__init__()
        self.name = name
        self.coins = coins
        self.index = index
        self.race = race
        self.power = power
        self.unused_tokens = unused_tokens
        self.visuals = []
        self.declined_race = declined_race
        self.finished_profile = finished_profile
        self.show_unused_tokens = show_unused_tokens
        self.total_tokens = unused_tokens
        self.make_visuals()

    def make_visuals(self):
        self.visuals = []
        self.visuals.append(Text(f"{self.name}: {self.coins} coins", (1338, 92 + 165 * self.index), 20, (0,0,0), "center"))
        if self.finished_profile:
            self.visuals.append(Image(self.race + "_banner", (1442, 105 + 165 * self.index), "topright", RACE_BANNER_DIMENSIONS))
            self.visuals.append(Image(self.power, (1233, 105 + 165 * self.index), "topleft", POWER_DIMENSIONS))
            if self.show_unused_tokens:
                self.visuals.append(RaceToken(self.race, (1273, 219 + 165 * self.index), self.unused_tokens, False))
        if self.declined_race is not None:
            self.visuals.append(Image(self.declined_race + "_token", (1338, 219 + 165 * self.index), "center", (50, 50), grayscale=True))

    def update(self, coins="None", race="None", power="None", unused_tokens="None", finished_profile="None", show_unused_tokens="None", declined_race="None"):
        for string in ("coins", "race", "power", "unused_tokens", "finished_profile", "show_unused_tokens", "declined_race"):
            exec(f'if {string} != "None":\n\tself.{string} = {string}')
        self.make_visuals()

    def draw(self):
        for image in self.visuals:
            image.draw()

def exit_if_needed():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

def tile_at_location(point):
    for idx, polygon in enumerate(POLYGONS_AROUND_TILES):
        if polygon.contains(point):
            return idx
    return None

def rainbow_to_rgb(decimal):
    start = [255, 0, 0]
    one_sixth = 1 / 6
    if decimal < one_sixth:
        start[1] = int(255 * decimal / one_sixth)
    elif decimal < 2 * one_sixth:
        start[1] = 255
        start[0] -= int(255 * (decimal - one_sixth) / one_sixth)
    elif decimal < 0.5:
        start[0] = 0
        start[1] = 255
        start[2] = int(255 * (decimal - (2 * one_sixth)) / one_sixth)
    elif decimal < 4 * one_sixth:
        start[0] = 0
        start[1] = 255 - int(255 * (decimal - 0.5) / one_sixth)
        start[2] = 255
    elif decimal < 5 * one_sixth:
        start[0] = int(255 * (decimal - (4 * one_sixth)) / one_sixth)
        start[2] = 255
    else:
        start[2] = 255 - int(255 * (decimal - (5 * one_sixth)) / one_sixth)
    return tuple(start)

def pygame_to_math_point(point):
    return point[0], SCREEN_DIMENSIONS[1] - point[1]

def update():
    pygame.display.update()
    FPS.tick(60)

def get_visible_races(races):
    return [Image(race + "_banner", (209, 78 * idx), "topright", RACE_BANNER_DIMENSIONS) for idx, race in enumerate(races)]

def get_visible_race_tokens(occupants_on_tiles):
    return [None if race is None else RaceToken(race, CENTER_OF_TILE[idx], amount, declined) for idx, (race, amount, declined) in enumerate(occupants_on_tiles)]

def get_visible_powers(powers):
    return [Image(power, (0, 78 * idx), "topleft", POWER_DIMENSIONS) for idx, power in enumerate(powers)]

def get_visible_money(money):
    return [Text(str(coins), (209, 78 * idx), 15, reference_point="topright") for idx, coins in enumerate(money)]

def get_visible_protections(immunes):
    race_visual = []
    power_visual = []
    for idx, i in enumerate(immunes):
        if i == set():
            continue
        for protection in i:
            if protection in {"hole", "troll_lair"}:
                race_visual.append(Image(protection, tuple(CENTER_OF_TILE[idx][j] + 20 for j in range(2)), "center", (45, 45)))
            elif "bivouacking_token" in protection:
                power_visual.append(Image("bivouacking_token", tuple(CENTER_OF_TILE[idx][j] - 30 for j in range(2)), "center", (35, 35)))
                if protection[-1] != "1":
                    power_visual.append(Rect(CENTER_OF_TILE[idx][0] - 41, CENTER_OF_TILE[idx][1] - 23, 12, 17, (0,) * 3))
                    power_visual.append(Text(protection[-1], (CENTER_OF_TILE[idx][0] - 35, CENTER_OF_TILE[idx][1] - 14), 15, (255,) * 3, "center"))
            else:
                power_visual.append(Image(protection, tuple(CENTER_OF_TILE[idx][j] - 30 for j in range(2)), "center", (35, 35)))
    return race_visual, power_visual

def draw_all(*args):
    DISPLAY.fill((128,)*3)
    BOARD.draw()
    for collection in args:
        for image in collection:
            if image is not None:
                image.draw()

def shuffled(sequence):
    new_sequence = list(copy(sequence))
    shuffle(new_sequence)
    return new_sequence

def get_tokens(race, power):
    return RACE_TOKENS[race] + POWER_TOKENS[power] + (4 if race == "amazons" else 0)

def reinforcement(reinforcement_amount, *draws):
    current_image = Image("0", (725, 288), "center", (98, 98))
    frame = 1
    wait = [False, None]
    while True:
        exit_if_needed()
        draw_all(*draws)
        if frame % 10 == 0 and not wait[0]:
            current_image = Image(str((int(current_image.name) + 1) % 4), (725, 288), "center", (98, 98))
            if frame == 80 + (reinforcement_amount * 10):
                wait = [True, 0]
                current_image = Image(current_image.name, (725, 288), "center", (131, 131))
        current_image.draw()
        update()
        frame += 1
        if wait[0]:
            wait[1] = wait[1] + 1
            if wait[1] == 90:
                return
            
def get_visual_diplomats(occupants_on_tiles, player):
    lst = []
    for idx, tile in enumerate(occupants_on_tiles):
        if tile[0] == player:
            lst.append(Image("diplomat_token", (CENTER_OF_TILE[idx][0] + 23, CENTER_OF_TILE[idx][1] - 27), "center", (31, 36)))
    if len(lst) == 0:
        raise Exception()
    return lst

def main():

    occupants_on_tiles = [[None, 0, False] if x not in TILES_WITH_LOST_TRIBE else ["lost tribe", 1, False] for x in range(30)]
    visible_race_tokens = get_visible_race_tokens(occupants_on_tiles)
    active_board_occupants = set()
    unused_races = shuffled(ALL_RACES)
    unused_powers = shuffled(ALL_POWERS)
    current_races = unused_races[:6]
    current_powers = unused_powers[:6]
    current_powers[0] = "fortified"
    del unused_races[:6], unused_powers[:6]
    current_money = [0,] * 6
    end_turn_text = Text("END TURN", (1338, 18), 15, (255, 0, 0), "center")
    visible_races = get_visible_races(current_races)
    visible_powers = get_visible_powers(current_powers)
    visible_money = get_visible_money(current_money)
    player_infos = [Player(x, f"Player {x + 1}", 5, None, None, None, finished_profile=False) for x in range(3)]
    announcements = [Text("Player 1, select a race!", (1338, 40), 18, reference_point="center")]
    clicking = [False, False]
    mode = "selecting race"
    turn = 0
    first_conquest = [True, True, True]
    just_started_conquering = False
    need_redeploying = None
    decline_images = tuple(Image("decline", (1273, 219 + 165 * idx), "center", (26, 39)) for idx in range(3))
    redeployed = False
    turn_number = 1
    adjusted_turn = True
    turn_text_list = [Text("Turn 1/10", (105, 485), 21, reference_point="center")]
    protected_tiles = [set() for _ in range(30)]
    visual_race_protections, visual_power_protections = [], []
    visual_dragon = None
    using_dragon_master = False
    non_empty_regions_conquered = 0
    sorcerer_wand = Image("sorcerer_tool", (105, 532), "center", (60, 64))
    using_sorcerer = False
    can_use_sorcerer = False
    sorcerer_borders = []
    stout_decline_img = None
    decline_after_count_money = False
    immunity_from = None
    visual_diplomats = []
    player_with_diplomat = None
    berserk_asked_decline = False
    berserk_spin = False
    visual_fortress = None
    unused_forts = 0

    while True: # redeployment when attacked
        exit_if_needed()
        del clicking[0]
        clicking.append(pygame.mouse.get_pressed()[0])
        mouse_position = pygame.mouse.get_pos()
        current_player_info = player_infos[turn if isinstance(turn, int) else turn[1]]
        if turn == 0 and not adjusted_turn:
            turn_number += 1
            turn_text_list[0] = Text(f"Turn {turn_number}/10", (105, 485), 21, reference_point="center")
            adjusted_turn = True
        draw_all(visible_races, visible_powers, visible_money, player_infos, announcements, visual_race_protections, visual_power_protections, visible_race_tokens, turn_text_list, sorcerer_borders, visual_diplomats)
        if visual_fortress is not None:
            visual_fortress.draw()
        if mode == "selecting race":
            if len(visual_diplomats) == 0 and turn == immunity_from and player_with_diplomat in active_board_occupants:
                visual_diplomats = get_visual_diplomats(occupants_on_tiles, player_with_diplomat)
            if clicking == FALSE_TRUE and mouse_position[1] < 468 and mouse_position[0] < 212:
                idx_clicked = mouse_position[1] // 78
                new_money = current_player_info.coins - idx_clicked + current_money[idx_clicked]
                if new_money >= 0:
                    mode = "conquering"
                    have_abandoned = False
                    started_conquest = False
                    announcements = [Text(f"Player {turn + 1}, go conquering!", (1338, 40), 17, reference_point="center")]
                    race_clicked, power_clicked = current_races[idx_clicked], current_powers[idx_clicked]
                    del current_races[idx_clicked], current_powers[idx_clicked]
                    current_races.append(unused_races.pop(0))
                    current_powers.append(unused_powers.pop(0))
                    visible_races, visible_powers = get_visible_races(current_races), get_visible_powers(current_powers)
                    current_player_info.update(new_money, race_clicked, power_clicked, get_tokens(race_clicked, power_clicked), True)
                    current_player_info.total_tokens = current_player_info.unused_tokens
                    for idx in range(idx_clicked):
                        current_money[idx] += 1
                    del current_money[idx_clicked]
                    current_money.append(0)
                    visible_money = get_visible_money(current_money)
                    if current_player_info.power == "dragon master":
                        visual_dragon = Image("dragon", (1403, 219 + 165 * turn), "center", (50, 50))
                    if current_player_info.race == "sorcerers":
                        sorcerer_attacks = set()
                    if current_player_info.power == "berserk":
                        berserk_spin = True
        elif mode == "conquering":
            if len(visual_diplomats) == 0 and turn == immunity_from and player_with_diplomat in active_board_occupants:
                visual_diplomats = get_visual_diplomats(occupants_on_tiles, player_with_diplomat)
            if current_player_info.power == "dragon master" and visual_dragon is not None and current_player_info.unused_tokens:
                visual_dragon.draw()
            end_turn_text.draw()
            can_decline = not first_conquest[turn] and not started_conquest and not have_abandoned
            if can_decline and current_player_info.power != "berserk":
                decline_images[turn].draw()
                if decline_images[turn].rect.collidepoint(*mouse_position) and clicking == FALSE_TRUE:
                    for idx, tile in enumerate(occupants_on_tiles):
                        if tile[0] == current_player_info.race:
                            occupants_on_tiles[idx] = [current_player_info.race, 1, True]
                        elif tile[0] == current_player_info.declined_race and current_player_info.declined_race is not None:
                            occupants_on_tiles[idx] = [None, 0, False]
                        if "hole" in protected_tiles[idx] and current_player_info.race == "halflings":
                            protected_tiles[idx].remove("hole")
                    if current_player_info.race == "halflings":
                        visual_race_protections, visual_power_protections = get_visible_protections(protected_tiles)
                        halfling_holes_used = 0
                    if current_player_info.declined_race is not None:
                        unused_races.append(current_player_info.declined_race)
                    if current_player_info.race not in active_board_occupants:
                        unused_races.append(current_player_info.race)
                    visible_race_tokens = get_visible_race_tokens(occupants_on_tiles)
                    mode = "count money"
                    unused_powers.append(current_player_info.power)
                    current_player_info.update(race=None, power=None, finished_profile=False, show_unused_tokens=False, declined_race=current_player_info.race if current_player_info.race in active_board_occupants else None)
                    if current_player_info.declined_race in active_board_occupants:
                        active_board_occupants.remove(current_player_info.declined_race)
                    update()
                    continue
            current_player_info.update(show_unused_tokens=False)
            if current_player_info.race in active_board_occupants and just_started_conquering:
                just_started_conquering = False
                if current_player_info.race == "sorcerers":
                    sorcerer_attacks = set()
                for idx, tile in enumerate(occupants_on_tiles):
                    if tile[0] != current_player_info.race:
                        continue
                    tokens_on_tile = tile[1]
                    current_player_info.update(unused_tokens=current_player_info.unused_tokens + tokens_on_tile - 1)
                    occupants_on_tiles[idx][1] = 1
                if current_player_info.race == "amazons":
                    current_player_info.update(unused_tokens=current_player_info.unused_tokens + 4)
                visible_race_tokens = get_visible_race_tokens(occupants_on_tiles)
                if current_player_info.power == "dragon master":
                    using_dragon_master = False
                    visual_dragon = Image("dragon", (1403, 219 + 165 * turn), "center", (50, 50))
                for idx, protection in enumerate(protected_tiles):
                    if occupants_on_tiles[idx][0] != current_player_info.race:
                        continue
                    if "dragon" in protection:
                        protection.remove("dragon")
                    if "hero" in protection:
                        protection.remove("hero")
                    for a in tuple(protection):
                        if "bivouacking" in a:
                            protection.remove(a)
                visual_race_protections, visual_power_protections = get_visible_protections(protected_tiles)
            elif just_started_conquering:
                non_empty_regions_conquered = 0
            if current_player_info.power == "berserk":
                if not berserk_asked_decline and not first_conquest[turn]:
                    mode = "berserk decline"
                    current_player_info.update(show_unused_tokens=True)
                    announcements = [Text(f"Player {turn + 1},", (1338, 30), 18, reference_point="center"), Text("decline or roll?", (1338, 50), 18, reference_point="center"), Image("3", (1442, 219 + 165 * turn), "midright", (39, 39)), Image("decline", (1383, 219 + 165 * turn), "center", (26, 39))]
                    update()
                    continue
                if berserk_spin:
                    berserk_spin = False
                    berserk_discount = randint(-2, 3)
                    if berserk_discount < 0:
                        berserk_discount = 0
                    reinforcement(berserk_discount, visible_races, visible_powers, visible_money, player_infos, announcements, visual_race_protections, visual_power_protections, visible_race_tokens, turn_text_list, visual_diplomats)
            if 234 <= mouse_position[0] <= 1208 and 25 <= mouse_position[1] <= 550:
                mouse_attached_race_token = (RaceToken(current_player_info.race, mouse_position, current_player_info.unused_tokens, False) if not using_dragon_master else Image("dragon", mouse_position, "center", (50, 50))) if not using_sorcerer else Image("sorcerer_tool", mouse_position, "center", (60, 64))
                mouse_attached_race_token.draw()
                if current_player_info.power == "berserk" and not using_sorcerer:
                    Image(str(berserk_discount), (mouse_position[0] + 25, mouse_position[1] - 25), "center", (20, 20)).draw()
            if current_player_info.race == "sorcerers" and len(sorcerer_attacks) != 2 and current_player_info.total_tokens < 18:
                adjacent_tiles = set()
                my_tiles = {x for x in range(30) if occupants_on_tiles[x][0] == "sorcerers"}
                if current_player_info.power == "flying":
                    adjacent_tiles = set(range(30)) - my_tiles
                elif current_player_info.race in active_board_occupants:
                    for idx, tile in enumerate(occupants_on_tiles):
                        if tile[0] == "sorcerers":
                            adjacent_tiles |= ADJACENT_TILES[idx]
                    if current_player_info.power == "underworld" and any(occupants_on_tiles[x][0] == "sorcerers" for x in UNDERWORLD_TILES):
                        adjacent_tiles |= UNDERWORLD_TILES
                    adjacent_tiles -= my_tiles
                sorcerer_tiles = {x for x in adjacent_tiles if occupants_on_tiles[x][1] == 1 and occupants_on_tiles[x][0] != "lost tribe" and not occupants_on_tiles[x][2] and all("bivouacking" not in y for y in protected_tiles[x]) and all(y not in protected_tiles[x] for y in ("dragon", "hero", "hole")) and occupants_on_tiles[x][0] not in sorcerer_attacks and not (turn == immunity_from and occupants_on_tiles[x][0] == player_with_diplomat)}
                if current_player_info.power != "seafaring":
                    sorcerer_tiles -= SEA_TILES
                if sorcerer_tiles and not using_sorcerer:
                    sorcerer_wand.draw()
                    can_use_sorcerer = True
            if current_player_info.race == "sorcerers" and not current_player_info.unused_tokens and not can_use_sorcerer:
                redeployed = False
                mode = "redeploying"
                have_token_on_mouse = False
                announcements = [Text(f"Player {turn + 1}, redeploy!", (1338, 40), 18, reference_point="center")]
                remaining_tokens = False
            if clicking == FALSE_TRUE:
                if end_turn_text.rect.collidepoint(*mouse_position):
                    mode = "redeploying"
                    if using_dragon_master:
                        visual_dragon = None
                    have_token_on_mouse = False
                    announcements = [Text(f"Player {turn + 1}, redeploy!", (1338, 40), 18, reference_point="center")]
                    if current_player_info.unused_tokens > 0:
                        current_player_info.update(show_unused_tokens=True)
                        remaining_tokens = True
                    else:
                        remaining_tokens = False
                    update()
                    continue
                tile_clicked = tile_at_location(mouse_position)
                if not using_dragon_master and not using_sorcerer and can_use_sorcerer and sorcerer_wand.rect.collidepoint(*mouse_position):
                    using_sorcerer = True
                    sorcerer_borders = [Image("sorcerer_boundary", CENTER_OF_TILE[x], "center") for x in sorcerer_tiles]
                if using_sorcerer and tile_clicked in sorcerer_tiles:
                    sorcerer_attacks.add(occupants_on_tiles[tile_clicked][0])
                    player_taken_from = player_infos[turn - (1 if player_infos[turn - 1].race == occupants_on_tiles[tile_clicked][0] else 2)]
                    occupants_on_tiles[tile_clicked] = ["sorcerers", 1, False]
                    protected_tiles[tile_clicked] = set()
                    visible_race_tokens, (visual_race_protections, visual_power_protections) = get_visible_race_tokens(occupants_on_tiles), get_visible_protections(protected_tiles)
                    using_sorcerer, can_use_sorcerer = False, False
                    sorcerer_borders = []
                    started_conquest = True
                    current_player_info.total_tokens += 1
                    player_taken_from.total_tokens -= 1
                    non_empty_regions_conquered += 1
                    if all(x[0] != player_taken_from.race for x in occupants_on_tiles):
                        active_board_occupants.remove(player_taken_from.race)
                    update()
                    continue
                if current_player_info.race in active_board_occupants:
                    available_tiles = set()
                    tiles_with_race = set()
                    for idx, tile in enumerate(occupants_on_tiles):
                        if tile[0] != current_player_info.race:
                            continue
                        tiles_with_race.add(idx)
                        if current_player_info.power != "flying":
                            available_tiles |= ADJACENT_TILES[idx]
                    if current_player_info.power == "flying":
                        available_tiles = set(range(30))
                    available_tiles -= tiles_with_race
                else:
                    available_tiles = copy(OUTSIDE_TILES) if current_player_info.power != "flying" and current_player_info.race != "halflings" else set(range(30))
                    if first_conquest[turn] and current_player_info.race == "halflings":
                        halfling_holes_used = 0
                if current_player_info.power != "seafaring":
                    available_tiles -= SEA_TILES
                if current_player_info.power == "underworld" and any(occupants_on_tiles[x][0] == current_player_info.race for x in UNDERWORLD_TILES):
                    available_tiles |= UNDERWORLD_TILES
                    available_tiles -= tiles_with_race
                if using_sorcerer:
                    continue
                if tile_clicked in available_tiles:
                    required_tokens = 2 + occupants_on_tiles[tile_clicked][1] + int(tile_clicked in MOUNTAINS)
                    for a in protected_tiles[tile_clicked]:
                        if "bivouacking" in a:
                            required_tokens += int(a[-1])
                            break
                    if any(x in protected_tiles[tile_clicked] for x in ("dragon", "hero", "hole")) or (turn == immunity_from and occupants_on_tiles[tile_clicked][0] == player_with_diplomat):
                        required_tokens += 1000000
                    if occupants_on_tiles[tile_clicked][0] == "trolls":
                        required_tokens += 1
                    if current_player_info.power == "commando":
                        required_tokens -= 1
                    if current_player_info.race == "tritons" and any(tile_clicked in ADJACENT_TILES[x] for x in SEA_TILES):
                        required_tokens -= 1
                    if current_player_info.race == "giants" and any(tile_clicked in ADJACENT_TILES[x] | (UNDERWORLD_TILES if current_player_info.power == "underworld" and "giants" in (occupants_on_tiles[12][0], occupants_on_tiles[15][0]) else set()) for x in range(30) if occupants_on_tiles[x][0] == "giants" and x in MOUNTAINS):
                        required_tokens -= 1
                    if current_player_info.power == "mounted" and tile_clicked in (HILLS | FARMS):
                        required_tokens -= 1
                    if current_player_info.power == "underworld" and tile_clicked in UNDERWORLD_TILES:
                        required_tokens -= 1
                    if current_player_info.power == "berserk":
                        required_tokens -= berserk_discount
                    if required_tokens < 1:
                        required_tokens = 1
                    if using_dragon_master and all(x not in protected_tiles[tile_clicked] for x in ("hole", "hero")) and not (turn == immunity_from and occupants_on_tiles[tile_clicked][0] == player_with_diplomat):
                        required_tokens = 1
                    if required_tokens - 3 <= current_player_info.unused_tokens < required_tokens and current_player_info.unused_tokens and current_player_info.power != "berserk":
                        reinforcement_amount = randint(-2, 3)
                        if reinforcement_amount < 0:
                            reinforcement_amount = 0
                        started_conquest = True
                        reinforcement(reinforcement_amount, visible_races, visible_powers, visible_money, player_infos, announcements, visual_race_protections, visual_power_protections, visible_race_tokens, turn_text_list, visual_diplomats) # change in berserk too
                        required_tokens -= reinforcement_amount
                        if required_tokens < 1:
                            required_tokens = 1
                        if current_player_info.unused_tokens < required_tokens:
                            mode = "redeploying"
                            have_token_on_mouse = False
                            current_player_info.update(show_unused_tokens=True)
                            announcements = [Text(f"Player {turn + 1}, redeploy!", (1338, 40), 18, reference_point="center")]
                            remaining_tokens = True
                        else:
                            redeployed = True
                    if current_player_info.unused_tokens >= required_tokens:
                        protected_tiles[tile_clicked] = set()
                        if using_dragon_master:
                            protected_tiles[tile_clicked].add("dragon")
                            using_dragon_master, visual_dragon = False, None
                        active_board_occupants.add(current_player_info.race)
                        old_occupant = occupants_on_tiles[tile_clicked][0]
                        other_player_races = (player_infos[turn - 1].race, player_infos[turn - 2].race)
                        all_declined_races = tuple(player.declined_race for player in player_infos)
                        if old_occupant in other_player_races and old_occupant is not None and (occupants_on_tiles[tile_clicked][1] > 1 or old_occupant == "elves"):
                            player_taken_from = player_infos[turn - (1 if player_infos[turn - 1].race == old_occupant else 2)]
                            amount_on_tile = occupants_on_tiles[tile_clicked][1]
                            player_taken_from.update(unused_tokens=player_taken_from.unused_tokens+amount_on_tile - (0 if player_taken_from.race == "elves" else 1), show_unused_tokens=True)
                            if old_occupant == other_player_races[0]:
                                need_redeploying = (turn - 1) % 3
                        if old_occupant is not None:
                            non_empty_regions_conquered += 1
                            if old_occupant != "lost tribe":
                                player_taken_from = player_infos[turn - (1 if player_infos[turn - 1].race == old_occupant else 2)]
                                player_taken_from.total_tokens -= 0 if player_taken_from.race == "elves" else 1
                        if current_player_info.race == "halflings" and halfling_holes_used < 2:
                            protected_tiles[tile_clicked].add("hole")
                            halfling_holes_used += 1
                        tokens_used = current_player_info.unused_tokens if redeployed else required_tokens
                        occupants_on_tiles[tile_clicked] = [current_player_info.race, tokens_used, False]
                        if current_player_info.race == "trolls":
                            protected_tiles[tile_clicked].add("troll_lair")
                        visual_race_protections, visual_power_protections = get_visible_protections(protected_tiles)
                        current_player_info.update(unused_tokens=current_player_info.unused_tokens - tokens_used)
                        visible_race_tokens[tile_clicked] = RaceToken(current_player_info.race, CENTER_OF_TILE[tile_clicked], tokens_used, False)
                        if old_occupant is not None and old_occupant in all_declined_races and all(x[0] != old_occupant for x in occupants_on_tiles):
                            player_idx = all_declined_races.index(old_occupant)
                            unused_races.append(player_infos[player_idx].declined_race)
                            player_infos[player_idx].update(declined_race=None)
                        del all_declined_races
                        started_conquest = True
                        nonexistent = set()
                        for race in active_board_occupants:
                            if all(x[0] != race for x in occupants_on_tiles):
                                nonexistent.add(race)
                        active_board_occupants -= nonexistent
                        # check for sorcerer again
                        if current_player_info.race == "sorcerers" and len(sorcerer_attacks) != 2 and current_player_info.total_tokens < 18:
                            adjacent_tiles = set()
                            my_tiles = {x for x in range(30) if occupants_on_tiles[x][0] == "sorcerers"}
                            if current_player_info.power == "flying":
                                adjacent_tiles = set(range(30)) - my_tiles
                            elif current_player_info.race in active_board_occupants:
                                for idx, tile in enumerate(occupants_on_tiles):
                                    if tile[0] == "sorcerers":
                                        adjacent_tiles |= ADJACENT_TILES[idx]
                                if current_player_info.power == "underworld" and any(occupants_on_tiles[x][0] == "sorcerers" for x in UNDERWORLD_TILES):
                                    adjacent_tiles |= UNDERWORLD_TILES
                                adjacent_tiles -= my_tiles
                            sorcerer_tiles = {x for x in adjacent_tiles if occupants_on_tiles[x][1] == 1 and occupants_on_tiles[x][0] != "lost tribe" and not occupants_on_tiles[x][2] and all("bivouacking" not in y for y in protected_tiles[x]) and all(y not in protected_tiles[x] for y in ("dragon", "hero", "hole")) and occupants_on_tiles[x][0] not in sorcerer_attacks and not (turn == immunity_from and occupants_on_tiles[x][0] == player_with_diplomat)}
                            if current_player_info.power != "seafaring":
                                sorcerer_tiles -= SEA_TILES
                            if sorcerer_tiles and not using_sorcerer:
                                sorcerer_wand.draw()
                                can_use_sorcerer = True

                        if (current_player_info.unused_tokens == 0 and not can_use_sorcerer) or redeployed:
                            redeployed = False
                            mode = "redeploying"
                            have_token_on_mouse = False
                            announcements = [Text(f"Player {turn + 1}, redeploy!", (1338, 40), 18, reference_point="center")]
                            remaining_tokens = False
                        else:
                            berserk_spin = True
                elif tile_clicked is not None:
                    if not using_dragon_master:
                        for idx, tile in enumerate(occupants_on_tiles):
                            if tile_clicked == idx and tile[0] == current_player_info.race and not started_conquest:
                                occupants_on_tiles[idx] = [None, 0, False]
                                have_abandoned = True
                                current_player_info.update(unused_tokens=current_player_info.unused_tokens + 1)
                                visible_race_tokens[idx] = None
                                if all(x[0] != current_player_info.race for x in occupants_on_tiles):
                                    active_board_occupants.remove(current_player_info.race)
                                protected_tiles[tile_clicked] = set()
                                visual_race_protections, visual_power_protections = get_visible_protections(protected_tiles)
                else:
                    if current_player_info.power == "dragon master" and visual_dragon is not None and visual_dragon.rect.collidepoint(*mouse_position):
                        if using_dragon_master:
                            using_dragon_master = False
                            visual_dragon = Image("dragon", (1403, 219 + 165 * turn), "center", (50, 50))
                        elif current_player_info.unused_tokens:
                            using_dragon_master = True
                            visual_dragon = RaceToken(current_player_info.race, (1403, 219 + 165 * turn), current_player_info.unused_tokens - 1, False)
                            if current_player_info.unused_tokens - 1 == 0:
                                visual_dragon = None
        elif mode == "redeploying": # XXX when redeploying troops because was attacked, cannot move troops already on board
            try:
                skeleton_add
            except UnboundLocalError: # first frame
                if current_player_info.race == "skeletons":
                    skeleton_add = non_empty_regions_conquered // 2
                    if skeleton_add + current_player_info.total_tokens > 20:
                        skeleton_add = 20 - current_player_info.total_tokens
                    current_player_info.total_tokens += skeleton_add
                    current_player_info.update(unused_tokens=current_player_info.unused_tokens + skeleton_add, show_unused_tokens=current_player_info.unused_tokens + skeleton_add != 0)
                    remaining_tokens = current_player_info.show_unused_tokens
                skeleton_add = None
                if current_player_info.power == "heroic":
                    visual_hero = RaceToken("hero", (1403, 219 + 165 * turn), 2, False) if isinstance(turn, int) else None
                if current_player_info.power == "bivouacking":
                    visual_bivouack = RaceToken("bivouacking", (1403, 219 + 165 * turn), 5, False) if isinstance(turn, int) else None
                have_hero_on_mouse = False
                have_bivouack_on_mouse = False
                have_fortress_on_mouse = False
                if current_player_info.power == "fortified" and isinstance(turn, int):
                    current_forts = unused_forts
                    for protections in protected_tiles:
                        if "fortress" in protections:
                            current_forts += 1
                    if current_forts < 2:
                        unused_forts += 1
                    visual_fortress = None if unused_forts == 0 else RaceToken("fortress", (1403, 219 + 165 * turn), unused_forts, False)
                if current_player_info.race == "amazons" and isinstance(turn, int):
                    extra = current_player_info.unused_tokens
                    for tile in occupants_on_tiles:
                        if tile[0] == "amazons":
                            extra += tile[1] - 1
                    if extra < 4:
                        del skeleton_add
                        current_player_info.update(unused_tokens=0)
                        for tile in occupants_on_tiles:
                            if tile[0] == "amazons":
                                tile[1] = 1
                        need_abandon = 4 - extra
                        mode = "amazon abandon"
                        visible_race_tokens = get_visible_race_tokens(occupants_on_tiles)
                        announcements = [Text(f"Player {turn + 1}, abandon", (1338, 30), 18, reference_point="center"), Text(f"{need_abandon} region{'' if need_abandon == 1 else 's'}!", (1338, 50), 18, reference_point="center")]
                        update()
                        continue
                    else:
                        removed = current_player_info.unused_tokens
                        if current_player_info.unused_tokens >= 4:
                            current_player_info.update(unused_tokens=current_player_info.unused_tokens - 4)
                            removed = 4
                        else:
                            current_player_info.update(unused_tokens=0)
                            for tile in occupants_on_tiles:
                                if tile[0] == "amazons" and tile[1] != 1:
                                    can_remove = tile[1] - 1
                                    if can_remove > 4 - removed:
                                        tile[1] = tile[1] - 4 + removed
                                        break
                                    else:
                                        tile[1] = 1
                                        removed += can_remove
                                        if removed == 4:
                                            break # most indents lol
                        visible_race_tokens = get_visible_race_tokens(occupants_on_tiles)
                    current_player_info.update(show_unused_tokens=bool(current_player_info.unused_tokens))
                    remaining_tokens = bool(current_player_info.unused_tokens)
            if current_player_info.power == "stout" and stout_decline_img is None:
                stout_decline_img = Image("decline", (1403, 219 + 165 * turn), "center", (26, 39))
            if current_player_info.power == "heroic" and visual_hero is not None:
                visual_hero.draw()
            if current_player_info.power == "bivouacking" and visual_bivouack is not None:
                visual_bivouack.draw()
            if not have_token_on_mouse:
                end_turn_text.draw()
            if current_player_info.power == "stout":
                stout_decline_img.draw()
                if clicking == FALSE_TRUE and stout_decline_img.rect.collidepoint(*mouse_position):
                    decline_after_count_money = True
                    mode = "count money"
                    update()
                    continue
            if clicking == FALSE_TRUE and end_turn_text.rect.collidepoint(*mouse_position) and not have_token_on_mouse:
                if isinstance(turn, int):
                    mode = "count money"
                else:
                    mode, turn, announcements, need_redeploying, just_started_conquering, started_conquest = ("conquering" if player_infos[turn[0]].finished_profile else "selecting race", turn[0], [Text(f"Player {turn[0] + 1}, go conquering!", (1338, 40), 17, reference_point="center") if player_infos[turn[0]].finished_profile else Text(f"Player {turn[0] + 1}, select a race!", (1338, 40), 18, reference_point="center")], None, player_infos[turn[0]].finished_profile and player_infos[turn[0]].race in active_board_occupants, False)
                    adjusted_turn = False
                    have_abandoned = False
                del skeleton_add
                update()
                continue
            tile_clicked = tile_at_location(mouse_position)
            if clicking == FALSE_TRUE and not have_token_on_mouse and not have_hero_on_mouse and not have_bivouack_on_mouse and not have_fortress_on_mouse:
                for idx, token in enumerate(visible_race_tokens):
                    if token is None or token.race != current_player_info.race:
                        continue
                    if token.rect.collidepoint(*mouse_position) and token.amount > 1:
                        have_token_on_mouse = True
                        amount_on_tile = occupants_on_tiles[idx][1]
                        if amount_on_tile == 1:
                            occupants_on_tiles[idx] = [None, 0, False]
                        else:
                            occupants_on_tiles[idx][1] = amount_on_tile - 1
                        visible_race_tokens = get_visible_race_tokens(occupants_on_tiles)
                if remaining_tokens and current_player_info.visuals[3].rect.collidepoint(*mouse_position):
                    current_player_info.update(unused_tokens=current_player_info.unused_tokens - 1)
                    if current_player_info.unused_tokens == 0:
                        remaining_tokens = False
                        current_player_info.update(show_unused_tokens=False)
                    have_token_on_mouse = True
                if current_player_info.power == "heroic" and not have_token_on_mouse and isinstance(turn, int):
                    if visual_hero is not None and visual_hero.rect.collidepoint(*mouse_position):
                        have_hero_on_mouse = True
                        if visual_hero.amount == 2:
                            visual_hero = RaceToken("hero", (1403, 219 + 165 * turn), 1, False)
                        else:
                            visual_hero = None
                    elif tile_clicked is not None and "hero" in protected_tiles[tile_clicked] and all(CENTER_OF_TILE[tile_clicked][i] - 47 <= mouse_position[i] <= CENTER_OF_TILE[tile_clicked][i] - 12 for i in range(2)):
                        protected_tiles[tile_clicked].remove("hero")
                        visual_race_protections, visual_power_protections = get_visible_protections(protected_tiles)
                        have_hero_on_mouse = True
                if current_player_info.power == "bivouacking" and not have_token_on_mouse and isinstance(turn, int):
                    if visual_bivouack is not None and visual_bivouack.rect.collidepoint(*mouse_position):
                        have_bivouack_on_mouse = True
                        visual_bivouack = RaceToken("bivouacking", (1403, 219 + 165 * turn), visual_bivouack.amount - 1, False) if visual_bivouack.amount > 1 else None
                    elif tile_clicked is not None and any("bivouacking" in x for x in protected_tiles[tile_clicked]) and all(CENTER_OF_TILE[tile_clicked][i] - 47 <= mouse_position[i] <= CENTER_OF_TILE[tile_clicked][i] - 12 for i in range(2)):
                        element_with_bivouack = [x for x in protected_tiles[tile_clicked] if "bivouacking" in x][0]
                        protected_tiles[tile_clicked].remove(element_with_bivouack)
                        if element_with_bivouack[-1] != "1":
                            protected_tiles[tile_clicked].add(element_with_bivouack[:-1] + str(int(element_with_bivouack[-1]) - 1))
                        visual_race_protections, visual_power_protections = get_visible_protections(protected_tiles)
                        have_bivouack_on_mouse = True
                if current_player_info.power == "fortified" and not have_token_on_mouse and isinstance(turn, int) and visual_fortress is not None and visual_fortress.rect.collidepoint(*mouse_position):
                    have_fortress_on_mouse = True
                    unused_forts -= 1
                    visual_fortress = None if unused_forts == 0 else RaceToken("fortress", (1403, 219 + 165 * turn), unused_forts, False)
            elif clicking == FALSE_TRUE:
                if tile_clicked is None:
                    a = 165 * (turn if isinstance(turn, int) else turn[1])
                    if 194 + a < mouse_position[1] < 244 + a and mouse_position[0] > 1237:
                        have_token_on_mouse = False
                        if not have_hero_on_mouse and not have_bivouack_on_mouse and not have_fortress_on_mouse:
                            current_player_info.update(unused_tokens=current_player_info.unused_tokens + 1, show_unused_tokens=True)
                            remaining_tokens = True
                        elif have_hero_on_mouse:
                            visual_hero = RaceToken("hero", (1403, 219 + 165 * turn), 1 if visual_hero is None else 2, False)
                            have_hero_on_mouse = False
                        elif have_bivouack_on_mouse:
                            visual_bivouack = RaceToken("bivouacking", (1403, 219 + 165 * turn), 1 if visual_bivouack is None else visual_bivouack.amount + 1, False)
                            have_bivouack_on_mouse = False
                        else: # have_fortress_on_mouse
                            unused_forts += 1
                            visual_fortress = RaceToken("fortress", (1403, 219 + 165 * turn), unused_forts, False)
                            have_fortress_on_mouse = False
                else:
                    state_of_tile = occupants_on_tiles[tile_clicked]
                    if state_of_tile[0] == current_player_info.race:
                        have_token_on_mouse = False
                        if not have_hero_on_mouse and not have_bivouack_on_mouse and not have_fortress_on_mouse:
                            occupants_on_tiles[tile_clicked][1] = occupants_on_tiles[tile_clicked][1] + 1
                            visible_race_tokens = get_visible_race_tokens(occupants_on_tiles)
                        if "hero" not in protected_tiles[tile_clicked] and have_hero_on_mouse:
                            have_hero_on_mouse = False
                            protected_tiles[tile_clicked].add("hero")
                            visual_race_protections, visual_power_protections = get_visible_protections(protected_tiles)
                        if have_bivouack_on_mouse:
                            if any("bivouacking" in x for x in protected_tiles[tile_clicked]):
                                element_with_bivouack = [x for x in protected_tiles[tile_clicked] if "bivouacking" in x][0]
                                amount = int(element_with_bivouack[-1])
                                protected_tiles[tile_clicked].remove(element_with_bivouack)
                                protected_tiles[tile_clicked].add("bivouacking_token" + str(amount + 1))
                            else:
                                protected_tiles[tile_clicked].add("bivouacking_token1")
                            visual_race_protections, visual_power_protections = get_visible_protections(protected_tiles)
                            have_bivouack_on_mouse = False
                        if have_fortress_on_mouse and "fortress" not in protected_tiles[tile_clicked]:
                            protected_tiles[tile_clicked].add("fortress")
                            have_fortress_on_mouse = False
                            visual_race_protections, visual_power_protections = get_visible_protections(protected_tiles)
            if have_token_on_mouse:
                mouse_attached_race_token = RaceToken(current_player_info.race, mouse_position, 1, False)
                mouse_attached_race_token.draw()
            if have_hero_on_mouse:
                mouse_attached_race_token = RaceToken("hero", mouse_position, 1, False)
                mouse_attached_race_token.draw()
            if have_bivouack_on_mouse:
                mouse_attached_race_token = RaceToken("bivouacking", mouse_position, 1, False)
                mouse_attached_race_token.draw()
            if have_fortress_on_mouse:
                RaceToken("fortress", mouse_position, 1, False).draw()
        if mode == "amazon abandon": 
            if clicking == FALSE_TRUE:
                tile_at_loc = tile_at_location(mouse_position)
                if tile_at_loc is not None and occupants_on_tiles[tile_at_loc][0] == "amazons":
                    need_abandon -= 1
                    occupants_on_tiles[tile_at_loc] = [None, 0, False]
                    visible_race_tokens = get_visible_race_tokens(occupants_on_tiles)
                    if need_abandon == 0:
                        mode = "count money"
                    else:
                        announcements[1] = Text(f"{need_abandon} region{'' if need_abandon == 1 else 's'}!", (1338, 50), 18, reference_point="center")
        if mode == "count money":
            if current_player_info.power == "diplomat" and immunity_from is None:
                mode = "diplomat select"
                announcements = [Text(f"Player {turn + 1}, select a player to", (1338, 30), 16, reference_point="center"), Text(f"be immune to next round", (1338, 50), 16, reference_point="center")]
                other_players = ((turn + 1) % 3, (turn + 2) % 3)
                update()
                continue
            active_occupied_regions = 0
            declined_occupied_regions = 0
            bonuses = 0
            for idx, tile in enumerate(occupants_on_tiles):
                if tile[0] is None:
                    continue
                if tile[0] == current_player_info.race:
                    active_occupied_regions += 1
                    if current_player_info.power == "forest" and idx in FORESTS:
                        bonuses += 1
                    if current_player_info.power == "hill" and idx in HILLS:
                        bonuses += 1
                    if current_player_info.power == "swamp" and idx in SWAMPS:
                        bonuses += 1
                    if current_player_info.race == "wizards" and idx in MAGIC_TILES:
                        bonuses += 1
                    if current_player_info.race == "humans" and idx in FARMS:
                        bonuses += 1
                    if current_player_info.race == "dwarves" and idx in MINES:
                        bonuses += 1
                if tile[0] == current_player_info.declined_race:
                    declined_occupied_regions += 1
                    if current_player_info.declined_race == "dwarves" and idx in MINES:
                        bonuses += 1
            if current_player_info.power == "merchant":
                bonuses += active_occupied_regions
            if current_player_info.power == "alchemist":
                bonuses += 2
            if current_player_info.power == "wealthy" and first_conquest[turn]:
                bonuses += 7
            if current_player_info.power == "pillaging":
                bonuses += non_empty_regions_conquered
            if current_player_info.race == "orcs":
                bonuses += non_empty_regions_conquered
            if "fortified" == current_player_info.power:
                for idx, tile in enumerate(occupants_on_tiles):
                    if tile[0] == current_player_info.race and "fortress" in protected_tiles[idx]:
                        bonuses += 1
            current_player_info.update(coins=current_player_info.coins + active_occupied_regions + declined_occupied_regions + bonuses)
            if immunity_from == turn:
                visual_diplomats = []
                immunity_from = None
            if decline_after_count_money:
                decline_after_count_money = False
                stout_decline_img = None
                current_player_info.update(unused_tokens=0)
                for idx, tile in enumerate(occupants_on_tiles):
                    if tile[0] == current_player_info.race:
                        occupants_on_tiles[idx] = [current_player_info.race, 1, True]
                    elif tile[0] == current_player_info.declined_race and current_player_info.declined_race is not None:
                        occupants_on_tiles[idx] = [None, 0, False]
                    if "hole" in protected_tiles[idx] and current_player_info.race == "halflings":
                        protected_tiles[idx].remove("hole")
                if current_player_info.race == "halflings":
                    visual_race_protections, visual_power_protections = get_visible_protections(protected_tiles)
                    halfling_holes_used = 0
                if current_player_info.declined_race is not None:
                    unused_races.append(current_player_info.declined_race)
                if current_player_info.race not in active_board_occupants:
                    unused_races.append(current_player_info.race)
                unused_powers.append(current_player_info.power)
                visible_race_tokens = get_visible_race_tokens(occupants_on_tiles)
                current_player_info.update(race=None, power=None, finished_profile=False, show_unused_tokens=False, declined_race=current_player_info.race if current_player_info.race in active_board_occupants else None)
                if current_player_info.declined_race in active_board_occupants:
                    active_board_occupants.remove(current_player_info.declined_race)
            first_conquest[turn] = current_player_info.race is None
            turn = (turn + 1) % 3
            non_empty_regions_conquered = 0
            adjusted_turn = False
            if need_redeploying is not None and player_infos[need_redeploying].race in active_board_occupants:
                mode, announcements, turn, have_token_on_mouse, remaining_tokens = "redeploying", [Text(f"Player {((turn - 1) % 3) if ((turn - 1) % 3) else 3}, redeploy!", (1338, 40), 18, reference_point="center")], (turn, need_redeploying), False, player_infos[need_redeploying].unused_tokens > 0
            else:
                mode, announcements, just_started_conquering = ("conquering", [Text(f"Player {turn + 1}, go conquering!", (1338, 40), 17, reference_point="center")], player_infos[turn].race in active_board_occupants) if player_infos[turn].finished_profile else ("selecting race", [Text(f"Player {turn + 1}, select a race!", (1338, 40), 18, reference_point="center")], False)
                started_conquest, have_abandoned, need_redeploying = False, False, None
            berserk_asked_decline = False
        if mode == "diplomat select":
            Image("diplomat_token", mouse_position, "center", (62, 72)).draw()
            if clicking == FALSE_TRUE:
                for p in other_players:
                    if any(x.rect.collidepoint(*mouse_position) for x in player_infos[p].visuals):
                        immunity_from = p
                        player_with_diplomat = current_player_info.race
                        mode = "count money"
                        break
        if mode == "berserk decline":
            if clicking == FALSE_TRUE:
                if announcements[2].rect.collidepoint(*mouse_position):
                    mode = "conquering"
                    announcements = [Text(f"Player {turn + 1}, go conquering!", (1338, 40), 17, reference_point="center")]
                    berserk_asked_decline = True
                    berserk_spin = True
                elif announcements[3].rect.collidepoint(*mouse_position):
                    for idx, tile in enumerate(occupants_on_tiles):
                        if tile[0] == current_player_info.race:
                            occupants_on_tiles[idx] = [current_player_info.race, 1, True]
                        elif tile[0] == current_player_info.declined_race and current_player_info.declined_race is not None:
                            occupants_on_tiles[idx] = [None, 0, False]
                        if "hole" in protected_tiles[idx] and current_player_info.race == "halflings":
                            protected_tiles[idx].remove("hole")
                    if current_player_info.race == "halflings":
                        visual_race_protections, visual_power_protections = get_visible_protections(protected_tiles)
                        halfling_holes_used = 0
                    if current_player_info.declined_race is not None:
                        unused_races.append(current_player_info.declined_race)
                    if current_player_info.race not in active_board_occupants:
                        unused_races.append(current_player_info.race)
                    unused_powers.append(current_player_info.power)
                    visible_race_tokens = get_visible_race_tokens(occupants_on_tiles)
                    mode = "count money"
                    current_player_info.update(race=None, power=None, finished_profile=False, show_unused_tokens=False, declined_race=current_player_info.race if current_player_info.race in active_board_occupants else None)
                    if current_player_info.declined_race in active_board_occupants:
                        active_board_occupants.remove(current_player_info.declined_race)
                    update()
                    continue
        update()

SCREEN_DIMENSIONS = (1442, 575)
POLYGONS_AROUND_TILES = ( # all polygons are shifted 4 pixels left during __init__
    Polygon(((213, 1), (212, 243), (229, 234), (251, 252), (279, 221), (288, 210), (272, 167), (283, 145), (276, 118), (327, 106), (317, 58), (336, 48), (339, 35), (264, 0))),
    Polygon(((327, 106), (317, 58), (336, 48), (339, 35), (264, 0), (556, 1), (505, 38), (504, 55), (494, 64), (495, 75), (523, 99), (504, 118), (421, 136), (381, 156))),
    Polygon(((504, 118), (528, 119), (541, 125), (552, 121), (558, 126), (574, 128), (583, 135), (602, 129), (656, 92), (657, 76), (665, 72), (645, 13), (632, 0), (556, 1), (505, 38), (504, 55), (494, 64), (495, 75), (523, 99))),
    Polygon(((656, 92), (657, 76), (665, 72), (645, 13), (632, 0), (846, 1), (801, 24), (765, 51), (770, 58), (795, 68), (797, 79), (785, 88), (778, 84), (771, 87), (756, 104), (744, 120), (731, 129), (720, 131), (705, 147), (690, 141), (665, 122), (668, 109))),
    Polygon(((846, 1), (801, 24), (765, 51), (770, 58), (795, 68), (797, 79), (785, 88), (800, 108), (819, 132), (831, 146), (845, 147), (872, 137), (874, 124), (945, 99), (941, 95), (918, 83), (916, 80), (922, 68), (930, 63), (958, 55), (973, 48), (989, 34), (991, 28), (989, 21), (1001, 0))),
    Polygon(((945, 99), (941, 95), (918, 83), (916, 80), (922, 68), (930, 63), (958, 55), (973, 48), (989, 34), (991, 28), (989, 21), (1001, 0), (1237, 1), (1236, 9), (1180, 32), (1169, 33), (1166, 36), (1167, 45), (1155, 51), (1149, 60), (1122, 75), (1124, 80), (1130, 88), (1124, 95), (1129, 100), (1148, 108), (1151, 117), (1143, 128), (1117, 139), (1093, 142), (1088, 143), (1007, 138), (995, 122))),
    Polygon(((279, 221), (288, 210), (272, 167), (283, 145), (276, 118), (327, 106), (381, 156), (415, 197), (399, 203), (390, 218), (371, 226), (356, 225), (321, 240), (312, 234), (300, 243), (291, 241), (282, 229))),
    Polygon(((381, 156), (421, 136), (504, 118), (528, 119), (541, 125), (552, 121), (558, 126), (574, 128), (583, 135), (587, 149), (581, 166), (563, 177), (570, 194), (554, 206), (559, 213), (587, 230), (579, 242), (561, 246), (529, 244), (505, 252), (452, 249), (415, 197))),
    Polygon(((587, 230), (559, 213), (554, 206), (570, 194), (563, 177), (581, 166), (587, 149), (583, 135), (602, 129), (656, 92), (668, 109), (665, 122), (690, 141), (705, 147), (695, 158), (696, 167), (713, 182), (709, 193), (717, 206), (704, 219), (709, 225), (717, 256), (702, 265), (674, 269), (649, 279), (643, 285), (628, 266), (591, 254))),
    Polygon(((717, 256), (709, 225), (704, 219), (717, 206), (709, 193), (713, 182), (696, 167), (695, 158), (705, 147), (720, 131), (731, 129), (744, 120), (756, 104), (771, 87), (778, 84), (785, 88), (800, 108), (819, 132), (831, 146), (845, 147), (859, 174), (866, 188), (851, 192), (850, 207), (835, 230), (807, 245), (789, 256), (778, 257), (762, 251), (747, 250))),
    Polygon(((850, 207), (851, 192), (866, 188), (859, 174), (845, 147), (872, 137), (874, 124), (945, 99), (995, 122), (1007, 138), (1088, 143), (1069, 158), (1061, 176), (1042, 184), (1022, 210), (1008, 221), (1007, 241), (940, 249), (929, 244), (899, 247), (889, 238), (873, 235), (863, 228))),
    Polygon(((1007, 241), (1008, 221), (1022, 210), (1042, 184), (1061, 176), (1069, 158), (1088, 143), (1093, 142), (1117, 139), (1143, 128), (1151, 117), (1148, 108), (1129, 100), (1124, 95), (1130, 88), (1124, 80), (1122, 75), (1149, 60), (1155, 51), (1167, 45), (1166, 36), (1169, 33), (1180, 32), (1236, 9), (1237, 231), (1201, 206), (1176, 207), (1169, 213), (1137, 221), (1085, 249), (1056, 251))),
    Polygon(((212, 243), (229, 234), (251, 252), (279, 221), (282, 229), (291, 241), (300, 243), (312, 234), (321, 240), (356, 225), (371, 226), (390, 218), (399, 203), (415, 197), (452, 249), (475, 275), (503, 290), (500, 298), (509, 324), (478, 330), (466, 339), (465, 348), (451, 351), (460, 366), (443, 373), (427, 376), (417, 372), (398, 376), (391, 369), (365, 375), (368, 381), (328, 402), (329, 412), (315, 420), (300, 438), (289, 434), (265, 428), (259, 424), (213, 422))),
    Polygon(((460, 366), (451, 351), (465, 348), (466, 339), (478, 330), (509, 324), (500, 298), (503, 290), (475, 275), (452, 249), (505, 252), (529, 244), (561, 246), (579, 242), (587, 230), (591, 254), (628, 266), (643, 285), (654, 324), (644, 336), (633, 362), (618, 382), (604, 393), (601, 401), (579, 403), (542, 422), (532, 405), (517, 397), (490, 375), (478, 370))),
    Polygon(((601, 401), (604, 393), (618, 382), (633, 362), (644, 336), (654, 324), (643, 285), (649, 279), (674, 269), (702, 265), (717, 256), (747, 250), (762, 251), (778, 257), (787, 265), (797, 304), (810, 322), (824, 364), (828, 371), (825, 391), (797, 407), (791, 416), (779, 422), (773, 426), (766, 427), (741, 430), (721, 435), (696, 424), (674, 428), (668, 416), (660, 411), (639, 402))),
    Polygon(((825, 391), (828, 371), (824, 364), (810, 322), (797, 304), (787, 265), (778, 257), (789, 256), (807, 245), (835, 230), (850, 207), (863, 228), (873, 235), (889, 238), (899, 247), (929, 244), (940, 249), (960, 296), (972, 306), (974, 318), (964, 322), (954, 328), (944, 330), (927, 342), (914, 357), (903, 376), (897, 383), (890, 384), (878, 379), (859, 377), (840, 381))),
    Polygon(((974, 318), (972, 306), (960, 296), (940, 249), (1007, 241), (1056, 251), (1085, 249), (1110, 258), (1104, 265), (1110, 295), (1115, 301), (1116, 309), (1131, 324), (1118, 327), (1053, 351), (1038, 348), (1027, 336), (1007, 326), (990, 319))),
    Polygon(((1131, 324), (1116, 309), (1115, 301), (1110, 295), (1104, 265), (1110, 258), (1085, 249), (1137, 221), (1169, 213), (1176, 207), (1201, 206), (1237, 231), (1236, 393), (1226, 392), (1208, 397), (1204, 396), (1188, 400), (1182, 389), (1160, 375), (1155, 368), (1154, 347), (1150, 340))),
    Polygon(((213, 422), (259, 424), (265, 428), (289, 434), (300, 438), (315, 420), (329, 412), (328, 402), (368, 381), (365, 375), (391, 369), (398, 376), (417, 372), (427, 376), (443, 373), (460, 366), (478, 370), (490, 375), (517, 397), (532, 405), (542, 422), (529, 449), (522, 465), (506, 473), (492, 484), (458, 491), (446, 476), (433, 470), (414, 467), (398, 468), (387, 470), (372, 480), (357, 483), (345, 489), (335, 499), (324, 501), (312, 502), (301, 508), (290, 514), (281, 523), (279, 528), (260, 542), (237, 541), (232, 543), (214, 557))),
    Polygon(((522, 465), (529, 449), (542, 422), (579, 403), (601, 401), (639, 402), (660, 411), (668, 416), (674, 428), (672, 454), (674, 466), (672, 471), (679, 511), (674, 520), (671, 518), (662, 515), (655, 507), (617, 505), (603, 501), (595, 498), (584, 492), (574, 493), (564, 488), (539, 482), (530, 484), (521, 479))),
    Polygon(((679, 511), (672, 471), (674, 466), (672, 454), (674, 428), (696, 424), (721, 435), (741, 430), (766, 427), (778, 447), (789, 453), (801, 476), (802, 497), (813, 510), (820, 515), (807, 529), (801, 547), (795, 563), (788, 571), (784, 574), (765, 575), (743, 562), (741, 557), (731, 546), (709, 535), (697, 531), (687, 525))),
    Polygon(((820, 515), (813, 510), (802, 497), (801, 476), (789, 453), (778, 447), (766, 427), (773, 426), (779, 422), (791, 416), (797, 407), (825, 391), (840, 381), (859, 377), (878, 379), (890, 384), (897, 383), (887, 397), (886, 406), (893, 426), (901, 436), (912, 443), (939, 447), (958, 462), (940, 468), (914, 475), (896, 482), (888, 487), (845, 508), (826, 510))),
    Polygon(((958, 462), (939, 447), (912, 443), (901, 436), (893, 426), (886, 406), (887, 397), (897, 383), (903, 376), (914, 357), (927, 342), (944, 330), (954, 328), (964, 322), (974, 318), (990, 319), (1007, 326), (1027, 336), (1038, 348), (1053, 351), (1044, 371), (1051, 407), (1034, 423), (1031, 428), (1025, 453), (1004, 460), (989, 458))),
    Polygon(((1025, 453), (1031, 428), (1034, 423), (1051, 407), (1044, 371), (1053, 351), (1118, 327), (1131, 324), (1150, 340), (1154, 347), (1155, 368), (1160, 375), (1182, 389), (1188, 400), (1190, 417), (1176, 437), (1172, 458), (1165, 462), (1158, 477), (1152, 483), (1147, 497), (1106, 518), (1082, 503), (1065, 489), (1048, 475), (1037, 465))),
    Polygon(((214, 557), (232, 543), (237, 541), (260, 542), (279, 528), (281, 523), (290, 514), (301, 508), (312, 502), (324, 501), (335, 499), (345, 489), (357, 483), (372, 480), (387, 470), (398, 468), (414, 467), (433, 470), (446, 476), (458, 491), (446, 524), (418, 536), (413, 542), (417, 549), (432, 559), (428, 575), (213, 574))),
    Polygon(((428, 575), (432, 559), (417, 549), (413, 542), (418, 536), (446, 524), (458, 491), (492, 484), (506, 473), (522, 465), (521, 479), (530, 484), (539, 482), (564, 488), (574, 493), (584, 492), (595, 498), (587, 512), (589, 528), (578, 539), (579, 551), (566, 567), (564, 574))),
    Polygon(((564, 574), (566, 567), (579, 551), (578, 539), (589, 528), (587, 512), (595, 498), (603, 501), (617, 505), (655, 507), (662, 515), (671, 518), (674, 520), (679, 511), (687, 525), (697, 531), (709, 535), (731, 546), (741, 557), (743, 562), (765, 575))),
    Polygon(((784, 574), (788, 571), (795, 563), (801, 547), (807, 529), (820, 515), (826, 510), (845, 508), (888, 487), (898, 495), (905, 512), (912, 523), (922, 535), (926, 549), (941, 564), (942, 575))),
    Polygon(((942, 575), (941, 564), (926, 549), (922, 535), (912, 523), (905, 512), (898, 495), (888, 487), (896, 482), (914, 475), (940, 468), (958, 462), (989, 458), (1004, 460), (1025, 453), (1037, 465), (1048, 475), (1065, 489), (1082, 503), (1106, 518), (1104, 545), (1091, 552), (1082, 563), (1058, 574))),
    Polygon(((1058, 574), (1082, 563), (1091, 552), (1104, 545), (1106, 518), (1147, 497), (1152, 483), (1158, 477), (1165, 462), (1172, 458), (1176, 437), (1190, 417), (1188, 400), (1204, 396), (1208, 397), (1226, 392), (1236, 393), (1237, 575)))
)

TILES_WITH_LOST_TRIBE = {5, 6, 8, 10, 13, 19, 21, 22, 23, 28}
OUTSIDE_TILES = {0, 1, 2, 3, 4, 5, 6, 11, 12, 17, 18, 23, 24, 25, 26, 27, 28, 29}
ADJACENT_TILES = (
    {1, 6, 12}, {0, 6, 7, 2}, {1, 7, 8, 3}, {2, 8, 9, 4}, {3, 9, 10, 5}, {4, 10, 11},
    {0, 1, 7, 12}, {6, 1, 2, 8, 13, 12}, {2, 3, 9, 7, 13, 14}, {8, 3, 4, 10, 15, 14}, {9, 4, 5, 11, 16, 15}, {5, 10, 16, 17},
    {0, 6, 7, 13, 18}, {12, 18, 19, 14, 8, 7}, {8, 9, 13, 15, 19, 20, 21}, {14, 9, 10, 16, 22, 21}, {15, 10, 11, 17, 23, 22}, {11, 16, 23, 29},
    {12, 13, 19, 25, 24}, {18, 13, 14, 20, 26, 25}, {19, 14, 21, 27, 26}, {20, 14, 15, 22, 28, 27}, {21, 15, 16, 23, 28}, {22, 16, 17, 28, 29},
    {18, 25}, {24, 18, 19, 26}, {25, 19, 20, 27}, {20, 21, 28, 26}, {27, 21, 22, 23, 29}, {28, 23, 17}
)
MINES = {1, 9, 11, 12, 28}
FARMS = {3, 6, 10, 18, 22}
MAGIC_TILES = {6, 8, 16, 18, 21}
UNDERWORLD_TILES = {4, 12, 15, 19, 23}
FORESTS = {1, 5, 19, 27, 28}
HILLS = {8, 16, 20, 23, 24}
SWAMPS = {4, 7, 11, 13, 21}

FALSE_TRUE = [False, True]  
SEA_TILES = {0, 14, 29}
MOUNTAINS = {2, 9, 12, 15, 17, 25, 26}
CENTER_OF_TILE = ((259, 68), (421, 48), (578, 62), (714, 58), (878, 53), (1053, 54), (331, 186), (488, 184), (634, 198), (769, 169), (946, 174), (1165, 166), (352, 315), (558, 323), (733, 347), (863, 293), (1032, 289), (1188, 292), (382, 431), (587, 452), (746, 491), (830, 450), (974, 386), (1113, 427), (365, 537), (517, 525), (621, 538), (870, 539), (1000, 506), (1181, 526))
RACE_BANNER_DIMENSIONS = (150, 78)
POWER_DIMENSIONS = (78, 78)
ALL_RACES = ("amazons", "dwarves", "elves", "ghouls", "giants", "halflings", "humans", "orcs", "ratmen", "skeletons", "sorcerers", "tritons", "trolls", "wizards")
ALL_POWERS = ("alchemist", "berserk", "bivouacking", "commando", "diplomat", "dragon master", "flying", "forest", "fortified", "heroic", "hill", "merchant", "mounted", "pillaging", "seafaring", "spirit", "stout", "swamp", "underworld", "wealthy")
RACE_TOKENS = {'amazons': 6, 'dwarves': 3, 'elves': 6, 'ghouls': 5, 'giants': 6, 'halflings': 6, 'humans': 5, 'orcs': 5, 'ratmen': 8, 'skeletons': 6, 'sorcerers': 5, 'tritons': 6, 'trolls': 5, 'wizards': 5}
POWER_TOKENS = {'alchemist': 4, 'berserk': 4, 'bivouacking': 5, 'commando': 4, 'diplomat': 5, 'dragon master': 5, 'flying': 5, 'forest': 4, 'fortified': 3, 'heroic': 5, 'hill': 4, 'merchant': 2, 'mounted': 5, 'pillaging': 5, 'seafaring': 5, 'spirit': 5, 'stout': 4, 'swamp': 4, 'underworld': 5, 'wealthy': 4}
DISPLAY = pygame.display.set_mode(SCREEN_DIMENSIONS)
FPS = pygame.time.Clock()
BOARD = Image("board", (721, 287), "center")
COMPLETED_RACES = {"amazons", "dwarves", "elves", "giants", "halflings", "humans", "orcs", "ratmen", "skeletons", "sorcerers", "tritons", "trolls", "wizards"}
COMPLETED_POWERS = {"alchemist", "berserk", "bivouacking", "commando", "diplomat", "dragon master", "flying", "forest", "fortified", "heroic", "hill", "merchant", "mounted", "pillaging", "seafaring", "stout", "swamp", "underworld", "wealthy"}
print(set(ALL_RACES) - COMPLETED_RACES, set(ALL_POWERS) - COMPLETED_POWERS)
print(len(COMPLETED_POWERS) + len(COMPLETED_RACES), len(ALL_RACES) + len(ALL_POWERS) - len(COMPLETED_POWERS) - len(COMPLETED_RACES))

if __name__ == "__main__":
    main()

# https://steamcommunity.com/sharedfiles/filedetails/?id=210305597