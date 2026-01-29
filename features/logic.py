from utils.utils import print_alert, print_panel, clear_console
from prompt_toolkit.shortcuts import choice
from data.tiles import tiles as ti
import copy
from models.models import update_game
from utils.common import dice
from utils.auction import auction
from utils.mortgage import mortgage
from features.status import show_status
from features.jail import jail
from features.cards_handler import pick_chance_card, pick_treasure_card
import time


colors = {"brown": 2, "light_blue": 3, "pink": 3, "orange": 3, "red": 3, "yellow": 3, "green": 3, "dark blue": 2}


def turner(game):

    global turning
    turning = True


    players = game["players"]
    global lengths
    lengths = 4
    while not game["game_over"]:

        players[:] = [p for p in players if not p["bankrupt"]]

        if len(players) <= 1:
            game["game_over"] = True
            break
        player = players[game["turn"]]
        show_status(game)
        global options
        options = []
        dice_num = 0
        is_double = False
        if player["in_jail"]:
            jail()
            next_turn(game, players)
            continue

        dice_num, is_double = dice()
        check_position(player, dice_num)

        tile = game["tiles"][player["position"]]

        if is_double:
            player["doubles"] += 1
            if player["doubles"] == 3:
                player["position"] = 10
                player["in_jail"] = True
                player["remained_jail"] = 3 
                player["doubles"] = 0
                show_players(game["players"], player, dice=dice_num)
                next_turn(game, players)
                continue
        else:
            player["doubles"] = 0

        check_tile(player, tile, dice_num, is_double)

        while turning:
            options = []
            
            command = make_turn(player, tile)
            if command == "end_turn":
                break
            make_choice(command, player, tile)
        if not is_double:  
            next_turn(game, players)
        else:
            update_game(game["id"], game)


def next_turn(game, players):
    update_game(game["id"], game)
    time.sleep(3)
    if len(players) == lengths:
        game["turn"] = (game["turn"] + 1) % len(players)


def make_turn(player, tile):
    build_option(player, tile)
    buy_option(player, tile)
    sell_option(player)  
    options.append(("end_turn", "End_turn"))

    print_panel("choose", clear=False)
    if len(options) == 1:
        return "end_turn"
    command = choice(message='', options=options)
    return command


def make_choice(command, player, tile):
    match command:
        case "build":
            built_list_maker(player, tile["color"])
        case "sell":
            sell(player, game)
        case "mortgage":
            mortgage()
        case "buy":
            buy(player, tile, game)
        case "auction":
            auction(tile, game["players"], game)


def show_players(players, current, dice=None):
    clear_console()
    for player in players:
        properties = player["properties"]
        showing = ''
        for proper in properties:
            name = proper["name"]
            if proper["is_mortgaged"]:
                name += '#'
            showing += name + ", "
        if player == current:
            print_panel(player["name"], str(player["money"]) + "$", player["position"], showing, "injail:",
                        player["in_jail"], dice, clear=False, color="red")
            continue
        print_panel(player["name"], str(player["money"]) + "$", player["position"], showing, "injail:",
                    player["in_jail"], clear=False)


def check_tile(player, tile, dice_num, is_double):
    kind = tile["type"]
    match kind:
        case "property":
            prop(player, tile)
        case "railroad":
            rail(player, tile)
        case "tax":
            taxs(player, tile)
        case "utilities":
            comp(player, tile, dice_num)
        case "jail":
            player["in_jail"]=True
        case "chance":
            pick_chance_card(game)
            turning = False
        case "community":
            pick_treasure_card(game)
            turning = False


def check_position(player: dict, dice_num):
    player["position"] += dice_num
    pos = player["position"]
    if pos >= 40:
        player["money"] += 200
        pos = pos % 40
    player["position"] = pos


def prop(player, tile):
    if tile["owner"] == None:
        # buy check money and buy or auction
        pass

    elif tile["owner"] != player["name"]:
        cost = rentcalculator(tile, player)
        move_money(player["name"], tile["owner"], cost)
    else:
        choices = []
        try:
            if tile.get("is_mortgaged", False) == True:
                # mortgage buy back
                options.append(("end_turn", "End_turn"))
                command = choice(message="", options=[("mortgage", "Buy back"), ("end_turn", "End turn")],
                                 default="end_turn")
                if command == "mortgage":
                    mortgage()
        except Exception as e:
            print_alert("not doing", e)


def build_option(player, tile):
    if own_color_set(player, tile):
        try:
            if tile.get("house_cost", None) <= player["money"] and can_change_house(player,tile,1):
                options.append(("build", "build house"))
        except Exception:
            pass




def buy_option(player, tile):
    if tile.get("owner", "not buyable") == None:
        if tile["price"] > player["money"]:
            options.append(("auction", f"auction {tile['name']}"))
        else:
            options.append(("buy", f"Buy {tile['name']} {tile['price']}"))
            options.append(("auction", f"auction {tile['name']}"))


def end_turn():
    turning = False


def sell_option(player):
    properties = [til for til in game["tiles"] if til.get("owner", None) == player["name"]]
    if properties:
        options.append(("sell", "Sell"))
        return (True)


def can_change_house(player, tile, change):
    houses = []
    if color_set := own_color_set(player, tile):
        for land in color_set:
            if land == tile:
                houses.append(tile["houses"] + change)
                continue
            houses.append(land["houses"])
    else:
        return False
    if max(houses) - min(houses) >= 2:
        return False
    else:
        return True


def own_color_set(player, tile):
    color = tile.get("color", None)
    if not color:
        return False
    color_set = []
    for property in game["tiles"]:
        if property["type"] == "property" and property["color"] == color and property["owner"] == player["name"] and property["mortgaged"]==False:
            color_set.append(property)
    if len(color_set) == colors[color]:
        return color_set
    else:
        return None


def rentcalculator(tile, player: dict, dice=0):
    if tile["type"] == "property":
        return tile["rent"][tile["houses"]]  
    elif tile["type"] == "railroad":
        num = 0
        for proper in game["tiles"]:
            if proper["type"] == "railroad" and proper["owner"] == player["name"]:
                num += 1
        return tile["rent"][num-1] 
    elif tile["type"] == "utilities":  
        num = 0
        properties = [x for x in game["tiles"] if x["owner"] == tile["owner"]]
        for proper in properties:
            if proper["type"] == "utilities":
                num += 1
        if num == 1:
            return dice * 4
        elif num == 2:
            return dice * 10
        else:
            ValueError("wrong number of utilities") 
    else:
        raise ValueError("wrong type")


def bankrupcy(player, price, opponent: dict):
    global lengths
    if player["bankrupt"] == True:
        return []
    while price > player["money"]:
        properties = [x for x in game["tiles"] if x.get("owner", None) == player["name"]]
        if not properties:
            player["bankrupt"] = True
            clean_dead(player, game, opponent)
            lengths -= 1
            return []
        sell(player, opponent)


def sell_value(tile):
    if tile["type"] == "property":
        if tile["houses"] == 0:
            return tile["price"] / 2
        elif tile["houses"] == 4:
            return tile["hotel_cost"] / 2
        else:
            return tile["house_cost"] / 2
    elif tile["type"] == "railroad":
        return 100
    else:
        return tile.get("price", 0) / 2


def show_property(sell_list):
    sold = choice(message="", options=sell_list)
    sold_tile = next(tile for tile in game["tiles"] if tile["name"] == sold)
    return sold_tile





def taxs(player, tile):
    tax = tile["amount"]
    move_money(player["name"], "game", tax)
    turning = False


def rail(player, tile):
    if tile["owner"] == None:
        buy_option(player, tile)
    elif tile["owner"] != player["name"]:
        for user in game["players"]:
            if user["name"] == tile["owner"]:
                owner = user
                break
        rent = rentcalculator(tile, player=owner)
        move_money(player["name"], tile["owner"], rent)


def comp(player, tile, dice_num):
    if tile["owner"] == None:
        buy(player, tile, game)
    elif tile["owner"] != player["name"]:
        rent = rentcalculator(tile, player, dice=dice_num)
        move_money(player["name"], tile["owner"], rent)


def move_money(player, opponent, amount):
    opponent = next((x for x in game["players"] if x["name"] == opponent), game)
    player = next((x for x in game["players"] if x["name"] == player), game)
    if player["money"] >= amount:
        player["money"] -= amount
        opponent["money"] += amount
    elif player!=game:
        bankrupcy(player, amount, opponent)
    else:
        opponent["money"] += player["money"]
        player["money"] =0
        


def buy(player, tile, opponent):
    move_money(player["name"], opponent.get("name", "game"), tile["price"])
    tile["owner"] = player["name"]
    player["value"] += tile["price"]
    player["properties"] = [x for x in game["tiles"] if x.get("owner", None) == player["name"]]


def built_list_maker(player, color):
    color_set = [til for til in game["tiles"] if
                 (til.get("owner", None) == player["name"] and til.get('color', None) == color)]
    built_list = [] 
    for pro in sorted(color_set, key=lambda x: x["index"]):
        text = pro["name"]
        text += '*' * pro.get("houses", 0)
        text += str(pro.get("house_cost", 0))
        built_list.append((pro["name"], text))
    built = show_property(built_list)
    build(player, built)


def build(player, tile):
    if tile["houses"] == 4 and game["hotels"] != 0 and player["money"] >= tile["hotel_cost"]:
        game["houses"] += 4
        game["hotels"] -= 1
        tile["houses"] += 1
        player["money"] -= tile["hotel_cost"]
    elif (0 < tile["houses"] < 4) and game["houses"] != 0 and player["money"] >= tile["house_cost"]:
        game["houses"] -= 1
        tile["houses"] += 1
        player["money"] -= tile["house_cost"]


def real_sell(player, opponent: dict, tile):
    if tile["houses"] == 0:
        mortgage()
    else:
        if can_change_house(player, tile, -1):
            # sell option

            if tile["houses"] == 4:
                game["houses"] -= 4
                game["hotels"] += 1
                tile["houses"] -= 1
                move_money(opponent.get("name", "game"), player["name"], sell_value(tile))
            elif (tile["houses"] < 4):
                game["houses"] += 1
                tile["houses"] -= 1
                move_money(opponent.get("name", "game"), player["name"], sell_value(tile))
            else:
                print_alert("problem")


def sell(player, opponent: dict):
    properties = [tile for tile in game["tiles"] if tile.get("owner", None) == player["name"]]
    sell_list = []
    for pro in sorted(properties, key=lambda x: sell_value(x)):
        text = pro["name"]
        text += '*' * pro.get("houses", 0)
        text += str(sell_value(pro))
        sell_list.append((pro["name"], text))
    clear_console()
    show_players(game["players"], player)
    sold = show_property(sell_list)
    real_sell(player, opponent, sold)

    


def clean_dead(player, game, debter):
    for tile in game["tiles"]:
        if tile.get("owner") == player["name"]:
            if debter == game:
                tile["owner"] = None
            else:
                tile["owner"] = debter["name"]
            tile["houses"] = 0
            tile["is_mortgaged"] = False
                


if __name__ == "__main__":
    game = {"turn": 1, "houses": 32, "hotels": 12, "game_over": False, "money": 100000, "cards": {"chance_cards": ["Move to Boardwalk", "Go directly to Jail", "This card may be kept until needed\nGet out of jail free", "Pay $50 for visit a Doctor", "Go to GO tile and Collect $200", "This card may be kept until needed\nGet out of jail free", "Your speeding ticket is $20", "It's your birthday receive $100 from bank", "Go back 3 tiles", "Pay poor tax of $15"], "treasure_cards": ["Go to jail", "Get $50 from selling stocks", "Pay $50 to each player on the occasion of Nowruz", "Go to game Avenue\nIf you pass the GO tile you will receive $200", "Get a $50 subsidy", "Bank error in your account\nCollect $200", "Pay hospital fee of $100", "Go to the Short Line station\nGet $200 if you cross the GO tile", "Receive $100 from bank", "You have inherited $100"]}, "id": "6e752e1a-fce6-11f0-af12-dcf5059026fb", "players": [{"username": "yasin2007", "money": 1500, "in_jail": False, "position": 1, "properties": [], "jail_pass": 0, "dice_turn": 3, "bankrupt": False, "value": 0, "selling_power": 0, "doubles": 0, "id": "6d3bb9eb-fce6-11f0-9d7c-dcf5059026fb", "name": "4"}, {"username": "yasin2007", "money": 1500, "in_jail": False, "position": 1, "properties": [], "jail_pass": 0, "dice_turn": 3, "bankrupt": False, "value": 0, "selling_power": 0, "doubles": 0, "id": "60c8d601-fce6-11f0-b7d2-dcf5059026fb", "name": "2"}, {"username": "yasin2007", "money": 1500, "in_jail": False, "position": 1, "properties": [], "jail_pass": 0, "dice_turn": 3, "bankrupt": False, "value": 0, "selling_power": 0, "doubles": 0, "id": "675a2f4f-fce6-11f0-b091-dcf5059026fb", "name": "3"}, {"username": "yasin2007", "money": 1500, "in_jail": False, "position": 1, "properties": [], "jail_pass": 0, "dice_turn": 3, "bankrupt": False, "value": 0, "selling_power": 0, "doubles": 0, "id": "54541db9-fce6-11f0-a27e-dcf5059026fb", "name": "1"}]}
    turner(game)