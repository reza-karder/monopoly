from utils.utils import print_panel, print_alert
import time
from prompt_toolkit import choice

def auction(tile, game):
    players = game["players"]

    print_panel(f"🏆 AUCTION STARTED\nProperty: {tile['name']} (Base Price: $50)", sleep=2)

    active_players = players.copy()
    price = 50
    top_player = None
    bid_logs = []
    round_no = 1
    last_bid = None

    if len(active_players) < 2:
        print_alert("Not enough players with money for auction!", type="ERROR")
        return False

    while len(active_players) > 1:
        print_panel(f"ROUND {round_no} | Current Price: ${price}")
        if top_player:
            print_alert(f"Highest Bidder: {top_player['name']}")
        time.sleep(2)

        if len(active_players) == 1:
            break

        for player in active_players.copy():

            print_panel(f"\n🎮 {player['name']}'s Turn | 📈 Current Price: ${price}")

            options = [("leave", "Leave The Auction")]

            can_bid = player["money"] >= price + 1  # At least $1 higher
            if can_bid:
                options.append(("skip", "SKip This Turn"))
                options.insert(0, ("bid", "Place a Bid"))

            command = choice(
                message="",
                options= options
            )

            try:

                if command == "bid":
                    try:
                        bid = None

                        while not bid:
                            bid = int(input(f"Enter your bid (Larger Than ${price}): $"))

                            if bid <= price:
                                print_alert("❌ Must be higher than current price!", sleep=2)
                                bid = None
                                continue

                            if bid > player["money"]:
                                print_alert(f"❌ You only have ${player['money']}!", sleep=2)
                                bid = None
                                continue

                        price = bid
                        top_player = player
                        last_bid = bid

                        bid_logs.append({
                            "player": player["name"],
                            "amount": bid,
                            "round": round_no
                        })

                    except ValueError:
                        print_alert("❌ Please enter a valid number!", sleep=2)
                        continue

                elif command == "leave":
                    print_alert(f"{player['name']} passed and left the auction!", sleep=2)
                    active_players.remove(player)
                    if len(active_players) == 1 and top_player:
                        break
                    continue


                elif command == "skip":
                    print_alert(f"{player['name']} skips this round", sleep=2)
                    continue


            except KeyboardInterrupt:
                print_alert("\n\n⚠️ Auction interrupted!", sleep=2)
                return False

        round_no += 1

        if len(active_players) == 1:
            break

        print_panel(f"\nEnd of Round {round_no - 1}")

    if top_player is None:
        print_alert(f"No one bid on {tile['name']}!", type="ERROR", sleep=2)
        return False

    top_player = game["players"].index(top_player)
    top_player = game["players"][top_player]
    top_player["money"] -= price
    tile["owner"] = top_player["name"]

    print_alert(f"✅ {tile['name']} sold to {top_player['name']} for ${price}!", type="SUCCESS", sleep=2)

    return True
