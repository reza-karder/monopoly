from utils.utils import print_alert, print_panel, clear_console
from random import randint
from prompt_toolkit.shortcuts import choice
from data.tiles import tiles as ti
import copy
from models.models import update_game
import time


colors = {"brown":2, "light_blue":3, "pink":3, "orange":3, "red":3, "yellow":3, "green":3, "dark blue":2}

def turner(game):
    global state
    state = copy.deepcopy(game)
    board = copy.deepcopy(ti)
    players = state["players"]
    state["tiles"] = board
    state["turn"]=0    
    while not state["game_over"]:
        players[:] = [p for p in players if not p["bankrupt"]]
        if len(players) <= 1:
            state["game_over"] = True
            break
        player = players[state["turn"]]
        show_players(state["players"],player)
        global options
        options = []
        dice_num = 0
        is_double = False
        if player["in_jail"]:
            pris()
            next_turn(state, players)
            continue

        dice_num, is_double = dice()
        time.sleep(2)
        player["position"] += dice_num
        check_position(player)

        tile = state["tiles"][player["position"]]

        if is_double:
            player["doubles"] += 1
            if player["doubles"] == 3:
                player["position"] = 11
                player["in_jail"] = True
                player["doubles"] = 0
                pris()
                show_players(state["players"],player,dice=dice_num)
                next_turn(state, players)
                continue
        else:
            player["doubles"] = 0
        show_players(state["players"],player,dice=dice_num)

        check_tile(player, tile, dice_num, is_double)

        if not is_double:
            next_turn(state, players)
def next_turn(state,players):
    update_game(state["id"],state)
    time.sleep(3)
    state["turn"]= (state["turn"]+1)%len(players)
def show_players(players,current, dice=None):
    clear_console()
    for player in players:
        properties = [x for x in state["tiles"] if x.get("owner", None)==player["name"]]
        showing = ''
        for proper in properties:
            name = proper["name"]
            if proper["is_mortgaged"]:
                
                name+='#'
            showing+=name+", "
        if player==current:
            print_panel(player["name"],str(player["money"])+"$",player["position"], showing, "injail:",player["in_jail"],dice,clear=False,color="red")
            continue
        print_panel(player["name"],str(player["money"])+"$",player["position"], showing, "injail:",player["in_jail"],clear=False)
def dice():
    dice1 = randint(1,6)
    dice2 = randint(1,6)
    if dice1==dice2:
        return(dice1+dice2, True)
    return (dice1+dice2,False)

def check_tile(player, tile,dice_num, is_double):
    kind = tile["type"] 
    match kind:
        case "property":
            prop(player,tile)
        case "railroad":
            rail(player,tile)
        case "tax":
            taxs(player,tile)
        case "utilities":
            comp(player,tile, dice_num)
        case "jail":
            pris()
        case "cardcommunity" | "cardchance":
            card(state["cards"],player,kind)

def check_position(player:dict):
    pos = player["position"]
    if pos>=40:
        player["money"]+=200
        pos = pos%40
    player["position"]=pos

def prop(player, tile):
    if tile["owner"]==None:
        #buy check money and buy or auction
        command = buy_option(player,tile)
        if command == "sell":
            sell(player)
        else:
            buy(player,tile,state,tile["price"],command=command)
    elif tile["owner"]!=player["name"]:
        cost = rentcalculator(tile,player)
        move_money(player,tile["owner"], cost)
    else:
        choices = []
        try:
            if tile.get("is_mortgaged",False)==True:
                #mortagage buy back
                command = choice(message="",options=[("mortagage","Buy back"),("end_turn", "End turn")],default="end_turn")
                if command=="mortagage":
                    mortagage()
            else:
                #three option build() , sell(), end_turn()
                if tile["house_cost"]<=player["money"] and can_change_house(player,tile,+1):
                    options.append(("build", "build house"))
                if tile["houses"]>0:
                    options.append(("sell", "Sell"))
                else:
                    options.append(("mortagage", "Sell"))
                options.append(("end_turn", "End turn"))
            command = choice(message="",options=options,default="End turn")
            
            match command:
                case "build":build(player,tile)
                case "sell":sell(player,tile)
                case "mortagage":mortagage()
        except Exception as e:
            print("not doing",e)        
        
def mortagage():
    #todo
    pass
def buy_option(player, tile):
    if tile["price"]>player["money"]:
        options.append(("auction", f"auction {tile['name']}"))
    else:
        options.append(("buy", f"Buy {tile['name']} {tile['price']}"))
        options.append(("auction", f"auction {tile['name']}"))
        
        sell_option(player)
        command=choice(message='choose:',options=options)
    return command
def sell_option(player):
    properties = [til for til in state["tiles"] if  til.get("owner", None)==player["name"]]
    if properties:
        options.append(("sell","Sell"))
        return(True)
    
def can_change_house(player,tile,change):
    houses = []
    if color_set:=own_color_set(player, tile):
        for land in color_set:
            if land==tile:
                houses.append(tile["houses"]+change)
                continue
            houses.append(land["houses"])
    else:
        return False
    if max(houses)-min(houses)>=2:
        return False
    else:
        return True
def own_color_set(player,tile):
    color = tile["color"]
    color_set = []
    for property in state["tiles"]:
        if property["type"]=="property" and property["color"]==color and property["owner"]==player["name"]:
            color_set.append(property)
    if len(color_set)==colors[color]:
        return color_set
    else: 
        return None
def rentcalculator(tile,player:dict,dice=0):
    if tile["type"]=="property":
        return tile["rent"][tile["houses"]]
    elif tile["type"]=="railroad":
        num = 0
        for proper in state["tiles"]:
            if proper["type"]=="railroad" and proper["owner"]==player["name"]:
                num+=1
        return 25*(2**(num-1))
    elif tile["type"]=="company":
        num =0
        properties = [x for x in state["tiles"] if x["owner"]==tile["owner"]]
        for proper in properties:
            if proper["type"]=="company":
                num+=1
        if num==1:
            return dice*4
        elif num==2:
            return dice*10
        else:
            ValueError("wrong number of railroad")
    else:
        raise ValueError("wrong type")
def bankrupcy(player,price,opponent):
    global state
    while price>player["money"]:
        properties = [x for x in state["tiles"] if x["owner"]==opponent]   
        if not properties:
            player["bankrupt"]=True
            clean_dead(player,state)
            return []
        sold = show_property(properties,player,opponent)
def sell_value(tile):
    if tile["houses"]==0:
        return tile["price"]/2
    elif tile["houses"]==4:
        return tile["hotel_cost"]/2
    else:
        return tile["house_cost"]/2
def show_property(properties,player,opponent):
    options = []
    for property in sorted(properties,key=sell_value):
        text = ''
        text+=property["name"]+" "
        for _ in range(property["houses"]):
            text+="*"
        text+=" " + sell_value(property)
        options.append((property,text))
    sold = choice(message="select",options=options)
    sell(player,sold,opponent)
    return sold   
def card(cards,player,kind):
    if not cards:
        return
    _community_card_number = 10
    random_card = randint(1,_community_card_number)
    if kind=="cardchance":
        random_card+=_community_card_number
    card_func = globals()[f"{cards[random_card-1]}_func"]
    card_func(player)
def taxs(player,tile):
    tax = tile["amount"]
    move_money(player,state,tax)
def rail(player, tile):
    if tile["owner"]==None:
        buy_option(player, tile)
        buy(player,tile,state,price=200,command="buy")
    elif tile["owner"]!=player["name"]:
        for user in state["players"]:
            if user["name"]==tile["owner"]:
                owner = user
                break
        rent = rentcalculator(tile, player=owner)
        move_money(player,tile["owner"], rent)
def comp(player, tile,dice_num):
    if tile["owner"]==None:
        buy(player,tile,state,price=150)
    elif tile["owner"]!=player["name"]:
        rent = rentcalculator(tile,player, dice=dice_num)
        move_money(player,tile["owner"], rent)
def move_money(player, opponent, amount):
    opponent = next((x for x in state["players"] if x["name"]==opponent), state)
    if player["money"]>=amount:
        player["money"]-=amount
        opponent["money"]+=amount
    else:
        bankrupcy(player,amount,opponent)
def buy(player,tile,opponent, price, command=''):
    if command=="buy":
        move_money(player,opponent,tile["price"])
        tile["owner"]=player["name"]
        player["value"]+=tile["price"]
    else:
        #auction
        pass
def build(player,tile):
    if tile["houses"]==4 and state["hotels"]!=0 and player["money"]>=tile["hotel_cost"]:
        state["houses"]+=4
        state["hotels"]-=1
        tile["houses"]+=1
        player["money"]-=tile["hotel_cost"]
    elif (0<tile["houses"]<4) and state["houses"]!=0 and player["money"]>=tile["house_cost"]:
        state["houses"]-=1
        tile["houses"]+=1
        player["money"]-=tile["house_cost"]
    else:
        print_alert("problem")
def sell(player):
    opponent = state
    properties = [til for til in state["tiles"] if til.get("owner",None)==player["name"]]
    sell_list = [(pro["name"],pro["name"]+" "+str(sell_value(pro))) for pro in properties]
    clear_console()
    show_players(state["players"],player)
    command = choice(message='',options=sell_list)
    tile = next((x for x in properties if x["name"]==command), None)
    if tile["houses"]==0:
        mortagage()
    else:
        if can_change_house(player,tile,-1):
            #sell option

            if tile["houses"]==4:
                state["houses"]-=4
                state["hotels"]+=1
                tile["houses"]-=1
                move_money(opponent,player,sell_value(tile))       
            elif (tile["houses"]<4):
                state["houses"]+=1
                tile["houses"]-=1
                move_money(opponent,player,sell_value(tile))
            else:
                print_alert("problem")
def pris():
    
    #todo
    """
    player["jail"]=True
    if player["jail_pass"]>0:
        player["jail"]=False
    if player["dice_turn"]>0:
        options = [("roll", "roll dice"),("pay", "Pay 50$")]
    command = ''
    if command == "roll":
        dice_num, is_double=dice()        
    """
def clean_dead(player,state):
    for tile in state["tiles"]:
        if tile.get("owner") == player["name"]:
            tile["owner"]=None
            tile["houses"]=0
            tile["is_mortgaged"]=False
game = {"turn": 1, "houses": 32, "hotel": 12, "game_over": False, "money": 100000, "id": "98022629-e66d-11f0-8c56-dcf5059026fa", "players": [{"username": "yasin2007", "money": 1500, "in_jail": False, "position": 1, "jail_pass": 0, "dice_turn": 3, "bankrupt": False, "value": 0, "selling_power": 0, "doubles": 0, "id": "5c7c26aa-e65d-11f0-895b-dcf5059026fa", "name": "1"}, {"username": "yasin2007", "money": 1500, "in_jail": False, "position": 1, "jail_pass": 0, "dice_turn": 3, "bankrupt": False, "value": 0, "selling_power": 0, "doubles": 0, "id": "94cd065b-e65f-11f0-acb4-dcf5059026fa", "name": "aeen"}, {"username": "yasin2007", "money": 1500, "in_jail": False, "position": 1,  "jail_pass": 0, "dice_turn": 3, "bankrupt": False, "value": 0, "selling_power": 0, "doubles": 3, "id": "bd4fb0b6-e65f-11f0-895d-dcf5059026fa", "name": "leila"}, {"username": "yasin2007", "money": 1500, "in_jail": False, "position": 1, "jail_pass": 0, "dice_turn": 3, "bankrupt": False, "value": 0, "selling_power": 0, "doubles": 0, "id": "7d4d7d97-e65b-11f0-a086-dcf5059026fa", "name": "yasin"}], "cards": {"chance_cards": [], "treasure_cards": []}}
if __name__ == "__main__":
    turner(game)