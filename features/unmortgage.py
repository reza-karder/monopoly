import time

from utils.utils import print_panel, print_alert
from prompt_toolkit.shortcuts import choice

def unmortgage(player, game):
    active_mortgages = [
        tile
        for tile in game["tiles"]
        if tile["owner"] == player["name"]
        and not tile["is_mortgaged"]
    ]

    while active_mortgages:
        options = [(tile, f"{tile['name']} - ${round(tile['mortgage'] * 1.1)}") for tile in active_mortgages]
        options.append(("cancel", "cancel"))

        print_panel(f"Choose The Property To Unmortgage | Money: ${player['money']}")
        selected = choice(message="", options=options)

        if selected == "cancel":
            return

        index = game["tiles"].index(selected)
        tile = game["tiles"][index]
        price = round(tile["mortgage"] * 1.1)
        if player["money"] < price:
            print_alert("You Don't Have Money!")
            time.sleep(1)
            continue

        tile["is_mortgaged"] = False
        player["money"] -= price
        active_mortgages.remove(tile)
        print_alert(f"You Unmortgaged ${player['money']} - ${price}", type="SUCCESS")
        time.sleep(1)