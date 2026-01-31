import time

from features.Leaderboard import calculate_player_score
from utils.utils import print_alert, print_panel, show_loading
from prompt_toolkit.shortcuts import choice
from models.models import update_game, find_user, update_user
from utils.utils import dice
from features.auction import auction
from features.mortgage import mortgage
from features.status import show_status
from features.jail import jail
from features.cards_handler import pick_chance_card, pick_treasure_card
from features.unmortgage import unmortgage
from features.move_money import move_money, handle_new_props

#todo: trade must be added
#todo: alerts must be fixed
#todo: jail must be fixed
#todo: score calculator

colors = {"brown": 2, "light_blue": 3, "pink": 3, "orange": 3, "red": 3, "yellow": 3, "green": 3, "dark_blue": 2}
game = {}
turning = True
lengths = 4
options = []


def turner(game_model):
    global game, turning, options, lengths
    game = game_model
    turning = True
    options = []

    show_loading("Loading Game...", duration=4)

    players = game["players"]

    while not game["game_over"]:
        players = [p for p in players if not p["bankrupt"]]

        if len(players) <= 1:
            game["game_over"] = True
            break

        player = game["players"][game["turn"]]
        dice_num = 0
        is_double = False

        if player["remained_jail"]:
            jail(player, game)
            if player["remained_jail"]:
                next_turn()
                continue

        dice1, dice2, is_double = dice()
        dice_num = dice1 + dice2
        check_position(player, dice_num)

        tile = game["tiles"][player["position"]]

        if is_double:
            player["doubles"] += 1
            if player["doubles"] == 3:
                player["position"] = 10
                player["remained_jail"] = 3 
                player["doubles"] = 0
                show_status(game)
                print_alert(f"You Have Got Into Jail For Three Times Double ({dice1}, {dice2})", clear=False, sleep=2)
                next_turn()
                continue
        else:
            player["doubles"] = 0

        show_status(game)
        print_alert(f"You Have Rolled ({dice1}, {dice2}) | Landed On {tile['name']}", clear=False)
        check_tile(player, tile, dice_num)

        if player["bankrupt"]:
            next_turn()
            continue

        repeat = 0
        while turning:
            show_status(game)
            print_alert(f"You Have Rolled ({dice1}, {dice2}) | Landed On {tile['name']}", clear=False)
            
            command = make_turn(player, tile, repeat)
            if command == "end_turn":
                options = []
                break
            options = []
            make_choice(command, player, tile)
            repeat += 1

        if not is_double:  
            next_turn()
        else:
            update_game(game["id"], game)



    if game["game_over"]:
        game_over()


def game_over():
    global game
    winner = next(player for player in game["players"] if not player["bankrupt"])
    score = calculate_player_score(winner, game)
    print_alert(f"Game Is Over - Winner: {winner['name']} - Score: {score["total_assets"]}", sleep=6)

    for player in game["players"]:
        user = find_user(player["id"])

        if player["name"] == winner["name"]:
            user["score"] += score["total_assets"]

        else:
            user["score"] -= abs(player["debt"])

        update_user(user["id"], user)

    game["game_over"] = True
    update_game(game["id"], game)


def next_turn():
    global game

    game["turn"] = (game["turn"] + 1) % 4
    update_game(game["id"], game)


def make_turn(player, tile, repeat):
    buyable_tile = bool(tile["type"] in ["railroad", "property", "utilities"] and tile["owner"] == "game")
    if not (repeat == 0 and buyable_tile):
        build_option(player, tile)
        mortgage_option(player)
        unmortgage_option(player)
        trade_option(player)
        options.append(("end_turn", "End_turn"))

    print_panel("choose", clear=False)
    command = choice(message='', options=options)
    return command


def make_choice(command, player, tile):
    global game, options
    match command:
        case "build":
            build(player)
        case "mortgage":
            mortgage(player, game)
        case "buy":
            buy(player, tile)
        case "auction":
            auction(tile, game)
        case "unmortgage":
            unmortgage(player, game)
        case "trade":
            trade(player)

def check_tile(player, tile, dice_num):
    global game, turning
    kind = tile["type"]
    match kind:
        case "property":
            prop(player, tile)
        case "railroad":
            rail(player, tile)
        case "tax":
            tax(player, tile)
        case "utilities":
            utility(player, tile, dice_num)
        case "go_to_jail":
            player["remained_jail"]=3
            player["position"] = 10
            print_alert("You Got Into Jail!", clear=False, sleep=2)
            turning = False
        case "chance":
            card = pick_chance_card(game)
            if card == "Go back 3 tiles":
                check_tile(player, tile, dice_num)
        case "community":
            pick_treasure_card(game)
        case _:
            return


def check_position(player: dict, dice_num):
    player["position"] += dice_num
    pos = player["position"]
    if pos >= 40:
        player["money"] += 200
        pos = pos % 40
    player["position"] = pos


def prop(player, tile):
    global game

    if tile["owner"] == "game":
        buy_option(player, tile)

    elif tile["owner"] != player["name"]:
        rent = rent_calculator(tile, player)
        is_paid = move_money(player["name"], tile["owner"], rent, game)
        if is_paid:
            print_alert(f"You Have Paid ${rent} To {tile['owner']}", clear=False, sleep=2)


def build_option(player, tile):
    global options
    if get_buildable(player):
        options.append(("build", "Build House/Hotel"))


def buy_option(player, tile):
    global options

    if tile["price"] > player["money"]:
        options.append(("auction", f"auction {tile['name']}"))
    else:
        options.append(("buy", f"Buy {tile['name']} ${tile['price']}"))
        options.append(("auction", f"auction {tile['name']}"))


def unmortgage_option(player):
    global game
    unmortgageable = [
        tile
        for tile in game["tiles"]
        if tile["owner"] == player["name"]
        and tile["is_mortgaged"]
        and player["money"] > round(tile["mortgage"] * 1.1)
    ]

    if unmortgageable:
        options.append(("unmortgage", "Unmortgage"))


def mortgage_option(player):
    global game
    mortgageable = [
        tile
        for tile in game["tiles"]
        if tile["owner"] == player["name"]
        and not tile["is_mortgaged"]
        and tile.get("houses", 0) == 0
    ]

    if mortgageable:
        options.append(("mortgage", "Mortgage"))


def trade_option(player):
    global game, options

    player_props = [
        tile
        for tile in game["tiles"]
        if tile["owner"] == player["name"]
        and tile.get("houses", 0) == 0
    ]

    owned_props = [
        tile
        for tile in game["tiles"]
        if tile["owner"] != player["name"]
        and tile["owner"] != "game"
        and tile.get("houses", 0) == 0
    ]

    if player_props and owned_props:
        options.append(("trade", "Trade"))


def trade(player):
    global game

    properties = [
        tile
        for tile in game["tiles"]
        if tile["owner"] == player["name"]
        and tile.get("houses", 0) == 0
    ]

    owned_props = [
        tile
        for tile in game["tiles"]
        if tile["owner"] != player["name"]
        and tile["owner"] != "game"
        and tile.get("houses", 0) == 0
    ]

    print_panel("Choose The Property You Want To Trade")
    player_prop_name = choice(message="", options=[(prop["name"], prop['name']) for prop in properties])
    player_prop = next(tile for tile in game["tiles"] if tile["name"] == player_prop_name)


    print_panel("Choose The Property You Want To Trade With")
    opponent_prop_name = choice(message="", options=[(prop["name"], prop["name"]) for prop in owned_props])
    opponent_prop = next(tile for tile in game["tiles"] if tile["name"] == opponent_prop_name)
    opponent = next(plyr for plyr in game["players"] if plyr["name"] == opponent_prop["owner"])

    print_panel(f"{opponent['name']} Do You Want To Trade {player_prop_name} With {opponent_prop_name}?")
    answer = choice(message="", options=[("yes", "Yes"), ("no", "No")])

    if answer == "yes":
        player_prop["owner"] = opponent["name"]
        opponent_prop["owner"] = player["name"]
        print_alert(f"{player_prop_name} Is Traded With {opponent_prop_name}", type="SUCCESS", sleep=2)
        handle_new_props([opponent_prop], player, game)
        handle_new_props([player_prop], opponent, game)

    else:
        print_alert(f"{opponent['name']} Has Refused To Trade With", type="ERROR", sleep=2)

def get_buildable(player):
    global game, colors

    properties = [
        tile
        for tile in game["tiles"]
        if tile["owner"] == player["name"] and tile["type"] == "property"
    ]
    buildable = []

    for tile in properties:
        same_colors = [
            prop
            for prop in properties
            if prop.get("color", None) == tile.get("color", None)
        ]

        count = len(same_colors)
        if count != colors[tile["color"]]:
            continue

        if tile["houses"] < 4:
            if not game["houses"]:
                continue

            if player["money"] < tile["house_cost"]:
                continue

            if tile["houses"] > min([prop["houses"] for prop in same_colors]):
                continue

        elif tile["houses"] == 4 :
            if not game["hotels"]:
                continue

            if player["money"] < tile["hotel_cost"]:
                continue

        buildable.append(tile)

    return buildable


def rent_calculator(tile, player:dict, dice=0):
    global game

    if tile["type"] == "property":
        return tile["rent"][tile["houses"] + tile["hotels"]]

    elif tile["type"] == "railroad":
        num = 0
        railroads = [
            prop
            for prop in game["tiles"]
            if prop["owner"] == tile["owner"]
               and prop["type"] == "railroad"
               and not prop["is_mortgaged"]
        ]
        num = len(railroads)
        return tile["rent"][num-1]

    elif tile["type"] == "utilities":
        num = 0
        utilities = [
            prop
            for prop in game["tiles"]
            if prop["owner"] == tile["owner"]
            and prop["type"] == "utilities"
            and not prop["is_mortgaged"]
        ]
        print(utilities)
        time.sleep(2)
        num = len(utilities)
        if num == 1:
            return dice * 4
        elif num == 2:
            return dice * 10


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
    global game
    print_panel("Select The Property You Want To Sell")
    sold = choice(message="", options=sell_list)
    sold_tile = next(tile for tile in game["tiles"] if tile["name"] == sold)
    return sold_tile


def tax(player, tile):
    tax = tile["amount"]
    is_paid = move_money(player["name"], "game", tax, game)
    if is_paid:
        print_alert(f"You Have Paid Tax Of ${tax}", clear=False, sleep=2)


def rail(player, tile):
    global game

    if tile["owner"] == "game":
        buy_option(player, tile)

    elif tile["owner"] != player["name"]:
        owner = next(plyr for plyr in game["players"] if plyr["name"] == tile["owner"])
        rent = rent_calculator(tile, player=owner)
        is_paid = move_money(player["name"], tile["owner"], rent, game)
        if is_paid:
            print_alert(f"You Have Paid ${rent} To {tile['owner']}", clear=False, sleep=2)


def utility(player, tile, dice_num):
    global game

    if tile["owner"] == "game":
        buy_option(player, tile)

    elif tile["owner"] != player["name"]:
        rent = rent_calculator(tile, player, dice=dice_num)
        is_paid = move_money(player["name"], tile["owner"], rent, game)
        if is_paid:
            print_alert(f"You Have Paid ${rent} To {tile['owner']}", clear=False, sleep=2)


def buy(player, tile):
    global game
    move_money(player["name"], "game", tile["price"], game)
    tile["owner"] = player["name"]
    print_alert(f"You Have Bought {tile['name']} - ${tile['price']}", type="SUCCESS", sleep=2)


def build(player):
    global game, colors

    buildable = get_buildable(player)

    while buildable:

        options = [
            (tile, f"{tile["name"]} - {f'+house ${tile['house_cost']}' if tile['houses'] < 4 else f'+hotel ${tile['hotel_cost']}'} ")
            for tile in buildable
        ]
        options.append(("return", "Return"))
        print_panel("Choose The Property You Want To Build On")
        selected = choice(message="", options=options)

        if selected == "return":
            return

        index = game["tiles"].index(selected)
        tile = game["tiles"][index]

        if tile["houses"] < 4:
            tile["houses"] += 1
            player["money"] -= tile["house_cost"]
            game["houses"] -= 1
            print_alert(f"You Have Built House On {tile['name']}", type="SUCCESS", sleep=2)

        else:
            tile["hotels"] += 1
            player["money"] -= tile["hotel_cost"]
            game["hotels"] -= 1
            print_alert(f"You Have Built Hotel On {tile['name']}", type="SUCCESS", sleep=2)

        buildable = get_buildable(player)
    

if __name__ == "__main__":
    turner(game_model)