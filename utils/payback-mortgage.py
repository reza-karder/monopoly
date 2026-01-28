def buy_back_mortgage(player):
    total_bought_back = 0  
    while True: 
        active_mortgages = []
        
        for mortgage in player.get("mortgages", []):
            tile = mortgage.get("tile", {})
            is_active = (
                mortgage.get("active") == True or 
                tile.get("mortgaged") == True
            )
            if is_active:
                active_mortgages.append(mortgage)
        
        if not active_mortgages:
            if total_bought_back > 0:
                print_panel(f"\n🎉 You've bought back {total_bought_back} properties!")
                return True
            else:
                print_panel("\n❌ No active mortgages found!")
                print_panel("   You don't have any properties to buy back.")
                return False
        
        print_panel("\n" + "─" * 50)
        print_panel("🏦 MORTGAGE BUY BACK")
        print_panel("─" * 50)
        
        print_panel(f"Player: {player['name']}")
        print_panel(f"Balance: ${player['money']}")
        print_panel(f"Available: {len(active_mortgages)} property(s)")
        if total_bought_back > 0:
            print_panel(f"Already bought back: {total_bought_back}")
        print_panel()
        
        for i, mortgage in enumerate(active_mortgages, 1):
            tile = mortgage["tile"]
            buyback_price = mortgage.get("buyback_price") or mortgage.get("buyback_value")
            if buyback_price is None:
                buyback_price = int(tile.get("price", 0) * 1.1)
            
            can_afford = "✓" if player['money'] >= buyback_price else "✗"
            
            print_panel(f"{i:2}. {tile['name'][:20]:20} ${buyback_price:6} {can_afford}")
        
        print_panel("\n 0. Finish buying back")
        print_panel("─" * 50)
        
        try:
            choice = input("\nSelect property (number) or 0 to finish: ").strip()
            
            if choice == "0":
                if total_bought_back > 0:
                    print_panel(f"\n✅ Finished! Bought back {total_bought_back} properties.")
                    return True
                else:
                    print_panel("\n❌ No properties were bought back.")
                    return False
            
            if not choice.isdigit():
                print_panel("❌ Please enter a number!")
                continue  

            idx = int(choice) - 1
            if idx < 0 or idx >= len(active_mortgages):
                print_panel(f"❌ Please choose between 1 and {len(active_mortgages)}!")
                continue 
            
            selected = active_mortgages[idx]
            tile = selected["tile"]
            
            final_price = selected.get("buyback_price") or selected.get("buyback_value")
            if final_price is None:
                final_price = int(tile.get("price", 0) * 1.1)
                print_panel(f"⚠️  Using estimated price: ${final_price}")
            
            if player['money'] < final_price:
                print_panel(f"\n❌ Not enough money!")
                print_panel(f"   Need: ${final_price}")
                print_panel(f"   Have: ${player['money']}")
                print_panel(f"   Missing: ${final_price - player['money']}")
                
                continue_choice = input("\nContinue with other properties? (yes/no): ").strip().lower()
                if continue_choice not in ['yes', 'y']:
                    if total_bought_back > 0:
                        return True
                    else:
                        return False
                continue 
            
            print_panel(f"\n🔍 CONFIRM BUY BACK:")
            print_panel(f"   Property: {tile['name']}")
            print_panel(f"   Cost: ${final_price}")
            print_panel(f"   Your money: ${player['money']} → ${player['money'] - final_price}")
            
            confirm = input(f"\nBuy this property? (yes/no): ").strip().lower()
            
            if confirm not in ['yes', 'y']:
                print_panel("Skipping this property...")
                continue 
            
            old_balance = player['money']
            player['money'] -= final_price
            
            tile["mortgaged"] = False
            selected["active"] = False
            
            for m in player.get("mortgages", []):
                if m.get("tile") == tile:
                    m["active"] = False
            
            total_bought_back += 1
            
            print_panel(f"\n✅ {tile['name']} UNMORTGAGED!")
            print_panel(f"💰 Paid: ${final_price}")
            print_panel(f"💵 New balance: ${player['money']}")
            print_panel(f"📊 Total bought back: {total_bought_back}")
            
            if len(active_mortgages) > 1:
                continue_choice = input(f"\nBuy back another property? ({len(active_mortgages)-1} remaining) (yes/no): ").strip().lower()
                if continue_choice not in ['yes', 'y']:
                    print_panel(f"\n🎉 Finished! Bought back {total_bought_back} properties.")
                    return True
            
        except KeyboardInterrupt:
            print_panel("\n\n⏹️  Operation cancelled.")
            if total_bought_back > 0:
                return True
            else:
                return False
        except Exception as e:
            print_panel(f"\n❌ Error: {e}")
            continue