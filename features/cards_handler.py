from features.move_money import move_money, raise_money, clean_dead
from utils.utils import print_alert


def pick_chance_card(game):
    cards = game["cards"]["chance_cards"]
    card = cards[-1]
    cards.pop(-1)
    cards.insert(0,card)
    player = game["players"][game["turn"]]
    print_alert(f"Picked Card:\n{card}", clear=False,sleep=6)

    match card:
        case "Move to Boardwalk":
            player["position"]=39
            
        case "Pay tax of $15":
            player["money"]-=15
            
        case "Go directly to Jail":
            player["position"]=0
            player["remained_jail"]=3
            
        case "Go to GO tile and Collect $200":
            player["money"]+=200
            player["position"]=0
            
        case  "Pay $50 for visit a Doctor":
            move_money(player["name"], "game", 50, game)
            
        case  "It's your birthday receive $100 from bank":
            player["money"]+=100
            
        case  "Go back 3 tiles":
            player["position"]-=3
            
        case  "Your speeding ticket is $20":
            move_money(player["name"], "game", 20, game)
            
        case "This card may be kept until needed\nGet out of jail free":
            player["jail_cards_count"]+=1
            cards.pop(0)

    return card


def pick_treasure_card(game):
    cards = game["cards"]["treasure_cards"]
    card = cards[-1]
    cards.pop(-1)
    cards.insert(0,card)
    player = game["players"][game["turn"]]
    print_alert(f"Picked Card:\n{card}", clear=False, sleep=6)

    match card:
        case "Receive $100 from bank":
            player["money"]+=100
            
        case  "Go to jail":
            player["position"]=10
            player["remained_jail"]=3
            
        case  "Pay hospital fee of $100":
            move_money(player["name"], "game", 100, game)
        
        case   "Bank error in your account\nCollect $200":
            player["money"]+=200
            
        case   "Go to the Reading RailRoad station\nGet $200 if you cross the GO tile":
            if  player["position"]!=2:
                player["position"]=5
                player["money"]+=200
            else:                
                player["position"]=5
                
        case    "Get $50 from selling stocks":
                player["money"]+=50
                
        case   "Go to State Avenue\nIf you pass the GO tile you will receive $200":
            if  player["position"]!=3:
                player["position"]=13
                player["money"]+=200
            else:                
                player["position"]=13
                
        case   "Pay $50 to each player on the occasion of Nowruz":
                opponents = [plyr for plyr in game["players"] if not plyr["bankrupt"] and plyr["name"] != player["name"]]
                total = 50 * len(opponents)

                if player["money"] < total:
                    has_raised = raise_money(player, total - player["money"], game)
                    if not has_raised:
                        print_alert(f"{player['name']} You Have Been Bankrupted", type="ERROR", sleep=2)
                        clean_dead(player, "game", total, game)

                else:
                    for opponent in opponents:
                        opponent["money"] += 50
                        player["money"] -= 50
                       
        case   "Get a $50 subsidy":
                 player["money"]+=50