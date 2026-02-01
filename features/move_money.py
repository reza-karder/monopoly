from utils.utils import print_alert, print_panel
from features.mortgage import  mortgage
from prompt_toolkit.shortcuts import choice


def move_money(player_name, opponent_name, amount, game):
    player = next(plyr for plyr in game["players"] if plyr["name"] == player_name)
    opponent = next((plyr for plyr in game["players"] if plyr["name"] == opponent_name), opponent_name)

    if player["money"] < amount:
        has_raised = raise_money(player,amount - player["money"], game)

        if not has_raised:
            print_alert(f"{player['name']} You Have Been Bankrupted", type="ERROR", sleep=2)
            clean_dead(player, opponent, amount, game)
            return False

    if opponent == "game":
        player["money"] -= amount
        return True

    else:
        player["money"] -= amount
        opponent["money"] -= amount
        return True


def raise_money(player, price, game):
    mortgageable = [
        tile
        for tile in game["tiles"]
        if tile.get("houses", 0) == 0
        and tile["owner"] == player["name"]
        and not tile["is_mortgaged"]
    ]
    total_value = sum([tile["mortgage"] for tile in mortgageable])

    if total_value < price:
        return False

    print_alert(f"{player['name']} You Are About To Get Bankrupt | Need ${price - player['money']}", sleep=2)
    while player["money"] < price:
        mortgage(player, game)
        if player["money"] < price:
            print_alert(f"You Can't Steel Afford That Payment | Need ${price - player["money"]}", sleep=2)

    return True


def clean_dead(player, opponent, amount, game):
    mortgaged_props = []

    for tile in game["tiles"]:
        if tile.get("owner") == player["name"]:

            if tile["is_mortgaged"]:
                mortgaged_props.append(tile)

            if tile["type"] == "property":
                houses = tile["houses"]
                hotels = tile["hotels"]

                player["money"] += round((houses * tile["house_cost"]) / 2)
                player["money"] += round((hotels * tile["hotel_cost"]) / 2)

                game["houses"] += houses
                game["hotels"] += hotels
                tile["houses"] = 0
                tile["hotels"] = 0

            if opponent == "game":
                tile["owner"] = "game"

            else:
                tile["owner"] = opponent["name"]

    if opponent != "game":
        opponent["money"] += player["money"]
        opponent["jail_cards_count"] += player["jail_cards_count"]
        handle_new_props(mortgaged_props, opponent, game)

    else:
        game["cards"]["chance_cards"] = ([
            "This card may be kept until needed\nGet out of jail free"
        ] * player["jail_cards_count"] ) + game["cards"]["chance_cards"]

    player["debt"] = player["money"] - amount
    player["money"] = 0
    player["jail_cards_count"] = 0
    player["bankrupt"] = True


def handle_new_props(new_props, player, game):
    mortgages = [prop for prop in new_props if prop["is_mortgaged"]]

    for property in mortgages:
        options = []
        unmortgage_cost = round(property["mortgage"] * 1.1)
        keeping_cost = round(property["mortgage"] * 0.1)

        if player["money"] < keeping_cost:
            has_raised = raise_money(player, keeping_cost, new_props)
            if not has_raised:
                print_alert(f"{player['name']} You Have Been Bankrupted", type="ERROR", sleep=2)
                clean_dead(player, "game", keeping_cost, game)
                break

        if player["money"] >= unmortgage_cost:
            options.append(("unmortgage", f"Pay ${unmortgage_cost} And Free The Property"))

        if player["money"] >= keeping_cost:
            options.append(("keep", f"Pay ${keeping_cost} And Keep The Property"))


        print_panel(f"{player['name']} You Have New Property ({property['name']}) And It's Mortgaged")
        command = choice(message="", options=options)
        property = next(prop for prop in game["tiles"] if prop["name"] == property["name"])

        if command == "unmortgage":
            player["money"] -= unmortgage_cost
            property["is_mortgaged"] = False
            print_alert(f"You Have Free The {property['name']}", sleep=2, type="SUCCESS")

        else:
            player["money"] -= keeping_cost
            print_alert(f"You Have kept The {property['name']}", sleep=2, type="SUCCESS")