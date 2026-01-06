def alert(msg):
    print_panel(f"\n⭐ {msg}")

def auction(tile, players, state):
    print_panel("\n" * 3)
    print_panel("=" * 50)
    print_panel("🏆 AUCTION STARTED")
    print_panel(f"Property: {tile['name']} (Base Price: ${tile['price']})")
    print_panel("=" * 50)

    if tile["price"] <= 0:
        alert("Weird price... skipping auction")
        return None

    active_players = players.copy()
    price = 0
    top_player = None
    bid_logs = []
    round_no = 1
    last_bid = None  
    if len(active_players) < 2:
        alert("Not enough players with money for auction!")
        return None

    print_panel("\nPlayers in auction:")
    for i, p in enumerate(active_players, 1):
        print_panel(f"  {i}. {p['name']} - ${p['money']}")

    time.sleep(2)

    while len(active_players) > 1:
        print_panel(f"\n{'=' * 40}")
        print_panel(f"ROUND {round_no}")
        print_panel(f"Current Price: ${price}")
        if top_player:
            print_panel(f"Highest Bidder: {top_player['name']}")
        print_panel(f"Players Left: {len(active_players)}")
        print_panel(f"{'=' * 40}")

        if len(active_players) == 1:
            break

        for player in active_players.copy():
            if len(active_players) == 1:
                break

            print_panel(f"\n🎮 {player['name']}'s Turn")
            print_panel(f"💰 Balance: ${player['money']}")
            print_panel(f"📈 Current Price: ${price}")

            print_panel("\nOptions:")
            can_bid = player["money"] >= price + 1  # At least $1 higher
            if can_bid:
                print_panel("  [1] Place a bid")
            print_panel("  [2] Pass (leave auction)")
            print_panel("  [3] Skip (stay but don't bid)")

            try:
                choice = input("\nYour choice: ").strip()

                if choice == "2":
                    alert(f"{player['name']} passed and left the auction!")
                    active_players.remove(player)
                    if len(active_players) == 1 and top_player:
                        break
                    continue

                elif choice == "1" and can_bid:
                    try:
                        bid = int(input(f"Enter your bid (>${price}): $"))

                        if bid <= price:
                            print_panel("❌ Must be higher than current price!")
                            continue

                        if bid > player["money"]:
                            print_panel(f"❌ You only have ${player['money']}!")
                            continue

                        price = bid
                        top_player = player
                        last_bid = bid

                        bid_logs.append({
                            "player": player["name"],
                            "amount": bid,
                            "round": round_no
                        })

                        print_panel(f"\n✅ {player['name']} bid ${bid}!")
                        print_panel(f"🔥 New highest price: ${price}")

                    except ValueError:
                        print_panel("❌ Please enter a valid number!")
                        continue

                elif choice == "3":
                    print_panel(f"{player['name']} skips this round")
                    continue

                else:
                    print_panel("❌ Invalid choice! Skipping turn...")
                    continue

            except KeyboardInterrupt:
                print_panel("\n\n⚠️ Auction interrupted!")
                return None

        round_no += 1

        if len(active_players) == 1:
            break

        print_panel(f"\nEnd of Round {round_no - 1}")
        cont = input("Continue auction? (yes/no): ").strip().lower()
        if cont not in ["yes", "y", ""]:
            break

    print_panel("\n" + "=" * 50)
    print_panel("AUCTION FINISHED")
    print_panel("=" * 50)

    if top_player is None:
        alert(f"No one bid on {tile['name']}!")
        print_panel("Property remains unowned.")
        return None

    print_panel(f"\n🏆 WINNER: {top_player['name']}")
    print_panel(f"💰 Winning Bid: ${price}")

    if bid_logs:
        print_panel("\n📊 Bidding History:")
        sorted_bids = sorted(bid_logs, key=lambda x: x["amount"], reverse=True)
        for i, b in enumerate(sorted_bids, 1):
            mark = "🏆" if i == 1 else f"{i}."
            print_panel(f"  {mark} {b['player']}: ${b['amount']}")

    print_panel("\n" + "-" * 40)
    confirm = input(
        f"Confirm sale to {top_player['name']} for ${price}? (yes/no): "
    ).strip().lower()

    if confirm in ["yes", "y", ""]:
        top_player["money"] -= price
        state["money"] += price
        tile["owner"] = top_player["name"]

        if "properties" not in top_player:
            top_player["properties"] = []
        top_player["properties"].append(tile)

        alert(f"✅ {tile['name']} sold to {top_player['name']} for ${price}!")

        print_panel("\n📊 FINAL STATUS:")
        print_panel(f"  {top_player['name']}: ${top_player['money']} (was ${top_player['money'] + price})")
        print_panel(f"  Bank: ${state['money']}")

        return top_player

    else:
        alert("❌ Sale cancelled!")
        return None