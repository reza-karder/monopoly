from utils.utils import print_panel, print_alert
from prompt_toolkit.shortcuts import choice
import time

def mortgage(player, game):
    #finding_mortgaeable_assets
    mortgageable = [
        tile for tile in game["tiles"]
        if tile["owner"] == player["name"]
        and tile.get("houses", 0) == 0
        and not tile["is_mortgaged"]
    ]

    #mortgage_choice
    while mortgageable:
        print_panel("\n🏦 MORTGAGE")
        options = [(tile, f"{tile['name']} - ${tile['mortgage']}") for tile in mortgageable]

        options.append(("cancel", "Cancel"))

        print_panel("Choose The Property you Want To Mortgage")
        selected = choice(
            message="",
            options=options,
        )

        if selected == "cancel":
            return
        
        try:
            index = game["tiles"].index(selected)
            tile = game["tiles"][index]

            tile["is_mortgaged"] = True
            player["money"] += tile["mortgage"]
            mortgageable.remove(tile)
            print_alert(f"Mortgaged {tile['name']} - ${tile['mortgage']}", type="SUCCESS")
            time.sleep(2)
                
        except:
            print_panel("❌ Invalid!")
            time.sleep(1)