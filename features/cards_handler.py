from utils.utils import print_alert


def pick_chance_card(game):
    cards = game["cards"]["chance_cards"]
    card = cards[-1]
    cards.pop(-1)
    cards.insert(0,card)
    print_alert(f"Picked Card:\n{card}",clear=False)
    match card:
        case "Move to Boardwalk":
            game["players"][game["current_turn"]-1]["position"]=40
            
        case "Pay poor tax of $15":
            game["players"][game["current_turn"]-1]["money"]-=15
            
        case "Go directly to Jail":
            game["players"][game["current_turn"]-1]["position"]=11
            game["players"][game["current_turn"]-1]["remained_jail"]=3
            
        case "Go to GO tile and Collect $200":
            game["players"][game["current_turn"]-1]["money"]+=200
            game["players"][game["current_turn"]-1]["position"]=1
            
        case  "Pay $50 for visit a Doctor":
            game["players"][game["current_turn"]-1]["money"]-=50
            
        case  "It's your birthday receive $100 from bank":
            game["players"][game["current_turn"]-1]["money"]+=100
            
        case  "Go back 3 tiles":
            game["players"][game["current_turn"]-1]["position"]-=3
            
        case  "Your speeding ticket is $20":
            game["players"][game["current_turn"]-1]["money"]-=20
            
        case "This card may be kept until needed\nGet out of jail free":
            game["players"][game["current_turn"]-1]["jail_cards_count"]+=1
            
def pick_treasure_card(game):
    cards = game["cards"]["treasure_cards"]
    card = cards[-1]
    cards.pop(-1)
    cards.insert(0,card)
    print_alert(f"Picked Card:\n{card}",clear=False)
    match card:
        case "Receive $100 from bank":
            game["players"][game["current_turn"]-1]["money"]+=100
            
        case  "Go to jail":
            game["players"][game["current_turn"]-1]["position"]=11
            game["players"][game["current_turn"]-1]["remained_jail"]=3
            
        case  "Pay hospital fee of $100":
            game["players"][game["current_turn"]-1]["money"]-=100
        
        case   "Bank error in your account\nCollect $200":
            game["players"][game["current_turn"]-1]["money"]+=200
            
        case   "Go to the Reading RailRoad station\nGet $200 if you cross the GO tile":
            if  game["players"][game["current_turn"]-1]["position"]!=3:
                game["players"][game["current_turn"]-1]["position"]=6
                game["players"][game["current_turn"]-1]["money"]+=200
            else:                
                game["players"][game["current_turn"]-1]["position"]=6
                
        case    "Get $50 from selling stocks":
                game["players"][game["current_turn"]-1]["money"]+=50
                
        case   "Go to State Avenue\nIf you pass the GO tile you will receive $200":
            if  game["players"][game["current_turn"]-1]["position"]!=3:
                game["players"][game["current_turn"]-1]["position"]=14
                game["players"][game["current_turn"]-1]["money"]+=200
            else:                
                game["players"][game["current_turn"]-1]["position"]=14
                
        case    "Pay $50 to each player on the occasion of Nowruz":
               for player in (game["players"]):
                   if player== game["players"][game["current_turn"]-1]:
                       continue
                   else:
                       game["players"][game["current_turn"]-1]["money"]-=50
                       game["players"][game["players"].index(player)]["money"]+=50
                       
        case   "Get a $50 subsidy":
                 game["players"][game["current_turn"]-1]["money"]+=50

            


            


            


                

                


            



            


            

    
            


            






            


            
        

            


        

