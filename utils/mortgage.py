def mortgage(player):
    #finding_mortgaeable_assets
    mortgageable = [] 
    for tile in player["properties"]:
        if tile.get("mortgaged", False):
            continue
        if tile["type"] == "property" and tile.get("houses", 0) > 0:
            continue
        if tile["type"] in ["property", "railroad", "company"]:
            mortgage_price = tile["price"] // 2
            buyback_price = int(mortgage_price * 1.1)
            mortgageable.append({
                "tile": tile,
                "mortgage_price": mortgage_price,
                "buyback_price": buyback_price
            })
    if not mortgageable:
        print_panel("❌ Nothing to Mortgage!")
        return 
    #mortgage_choice
    while mortgageable:
        print_panel("\n🏦 MORTGAGE")
        options = []
        for i, item in enumerate(mortgageable, 1):
            tile = item["tile"]
            options.append((str(i), f"{tile['name']} - Get: ${item['mortgage_price']}"))

        options.append(("0", "Cancel"))

        selected = choice(
            message=f"Balance: ${player['money']}",
            options=options,
            default="0"
        )

        if selected == "0":
            return
        
        try:
            idx = int(selected) - 1
            item = mortgageable[idx]
            tile = item["tile"]
            confirm = choice(
                message=f"Mortgage {tile['name']} for ${item['mortgage_price']}?",
                options=[("yes", "Yes"), ("no", "No")],
                default="no"
            )

            if confirm == "yes":
                tile["mortgaged"] = True
                player["money"] += item["mortgage_price"]

                if "mortgages" not in player:
                    player["mortgages"] = []

                player["mortgages"].append({
                    "tile": tile,
                    "mortgage_price": item["mortgage_price"],
                    "buyback_price": item["buyback_price"]
                })

                print_panel(f"✅ {tile['name']} mortgaged!")

                mortgageable.pop(idx)

                if not mortgageable:
                    print_panel("✅ All mortgaged!")
                    return
                
                again = choice(
                    message="Continue?",
                    options=[("yes", "Yes"), ("no", "No")],
                    default="no"
                )
                if again == "no":
                    return
                
        except:
            print_panel("❌ Invalid!")
            time.sleep(1)