def pay(payer, amount, receiver, reason="", state=None):
    
    def show_header():
        print_panel("\n" + "=" * 50)
        print_panel("💰 PAYMENT PROCESS")
        print_panel("=" * 50)
    
    def show_status():
        print_panel(f"\n📋 PAYMENT DETAILS:")
        print_panel(f"  From: {payer['name']}")
        print_panel(f"  To: {receiver['name'] if 'name' in receiver else 'Bank'}")
        print_panel(f"  Amount: ${amount}")
        if reason:
            print_panel(f"  Reason: {reason}")
        print_panel(f"  Payer Balance: ${payer['money']}")
        print_panel("-" * 40)
    
    def show_success():
        print_panel("\n✅ PAYMENT SUCCESSFUL!")
        print_panel(f"  {payer['name']}: ${payer['money'] + amount} → ${payer['money']}")
        print_panel(f"  {receiver['name']}: ${receiver['money'] - amount} → ${receiver['money']}")
        print_panel("=" * 50)
    
    show_header()
    show_status()
    
    if payer.get("bankrupt", False):
        print_panel("❌ PAYER IS BANKRUPT!")
        print_panel(f"{payer['name']} cannot make any payments.")
        return False
    
    if payer["money"] >= amount:
        payer["money"] -= amount
        receiver["money"] += amount
        show_success()
        return True
    
    print_panel("⚠️  INSUFFICIENT FUNDS!")
    print_panel(f"Need: ${amount}")
    print_panel(f"Have: ${payer['money']}")
    print_panel(f"Short: ${amount - payer['money']}")
    
    while payer["money"] < amount:
        deficit = amount - payer["money"]
        
        print_panel(f"\n📊 CURRENT SITUATION:")
        print_panel(f"  Still need: ${deficit}")
        print_panel(f"  Properties owned: {len(payer.get('properties', []))}")
        print_panel(f"  Current balance: ${payer['money']}")
        

        if not payer.get("properties", []):
            print_panel("\n💀 NO ASSETS LEFT!")
            print_panel(f"{payer['name']} has no properties to mortgage or sell.")
            payer["bankrupt"] = True
            
            print_panel("\n" + "💀" * 20)
            print_panel("🏚️ BANKRUPTCY!")
            print_panel("💀" * 20)
            print_panel(f"\n{payer['name']} is now BANKRUPT!")
            print_panel("Leaving the game...")
            time.sleep(2)
            
            if state:
                clean_dead(payer, state)
            return False
        
        print_panel("\n" + "🔄" * 20)
        print_panel("OPTIONS TO RAISE MONEY:")
        print_panel("🔄" * 20)
        print_panel("1. 🏦 Mortgage a property (get 50% of value)")
        print_panel("2. 💰 Sell a property (get full value)")
        print_panel("3. 🏳️ Give up and declare bankruptcy")
        
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "3":
                print_panel("\n" + "💀" * 20)
                print_panel("BANKRUPTCY DECLARED!")
                print_panel("💀" * 20)
                print_panel(f"\n{payer['name']} has given up!")
                payer["bankrupt"] = True
                
                if state:
                    clean_dead(payer, state)
                return False
                
            elif choice == "1":
                print_panel("\n🏦 MORTGAGE PROPERTY")
                print_panel(f"Need to raise: ${deficit}")
                
                success = mortgage_property(payer)
                
                if success:
                    print_panel(f"✅ Mortgage successful!")
                    print_panel(f"💰 New balance: ${payer['money']}")
                else:
                    print_panel("❌ Mortgage failed or cancelled")
                    
            elif choice == "2":
            
                print_panel("\n💰 SELL PROPERTY")
                print_panel(f"Need to raise: ${deficit}")
                
                sold = show_property(payer["properties"], payer, receiver)
                
                if sold:
                    payer["properties"].remove(sold)
                    print_panel(f"✅ Property sold!")
                    print_panel(f"💰 New balance: ${payer['money']}")
                else:
                    print_panel("❌ Sale cancelled")
                    
            else:
                print_panel("❌ Invalid choice! Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print_panel("\n\n❌ Process interrupted!")
            return False
        except Exception as e:
            print_panel(f"❌ Error: {e}")
            continue
        
        if payer["money"] >= amount:
            break

    if payer["money"] >= amount:
        payer["money"] -= amount
        receiver["money"] += amount
        
        print_panel("\n" + "🎉" * 20)
        print_panel("✅ FINAL PAYMENT COMPLETED!")
        print_panel("🎉" * 20)
        
        show_success()
        return True
    
    print_panel("\n💀 STILL NOT ENOUGH MONEY!")
    payer["bankrupt"] = True
    
    if state:
        clean_dead(payer, state)
    return False

