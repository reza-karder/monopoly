from utils.utils import print_alert, print_panel
from random import randint
from prompt_toolkit.shortcuts import choice
from tiles import tiles
import copy
from models.models import update_game

colors = {"brown":2, "light_blue":3, "pink":3, "orange":3, "red":3, "yellow":3, "green":3, "dark blue":2}
state = {
    "players" : players,
    "tiles" : tiles,
    "id": None,
    "turn": 1,
    "houses" : 32,
    "hotels" : 12,
    "game_over": False,
    "money": 10000000
}
def turner(state):
    board = copy.deepcopy(tiles)
    players = state["players"]
    state["tiles"] = board
    if state["turn"] >= len(players):
        state["turn"] = 0
    while not state["game_over"]:
        players[:] = [p for p in players if not p["bankrupt"]]
        if len(players) <= 1:
            state["game_over"] = True
            break
        player = players[state["turn"]]
        show_players(players)
        dice_num = 0
        is_double = False
        if player["in_jail"]:
            pris(player)
            next_turn(state, players)
            continue

        dice_num, is_double = dice()
        player["position"] += dice_num
        check_position(player)

        tile = state["tiles"][player["position"]]
        if is_double:
            player["doubles"] += 1
            if player["doubles"] == 3:
                player["position"] = 11
                player["in_jail"] = True
                player["doubles"] = 0
                pris(player)
                next_turn(state, players)
                continue
        else:
            player["doubles"] = 0

        check_tile(player, tile, dice_num, is_double)

        if not is_double:
            next_turn(state, players)
def next_turn(state,players):
    update_game(state["id"],state)
    state["turn"]= (state["turn"]+1)%len(players)
def show_players(players):
    for player in players:
        print_panel(player["name"],player["money"],player["position"], player["properties"], player["in_jail"])
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
            prop(player,tile, state)
        case "railroad":
            rail(player,tile)
        case "tax":
            taxs(player,tile)
        case "company":
            comp(player,tile, dice_num)
        case "prison":
            pris()
        case "cardcommunity" | "cardchance":
            card(cards,player,kind)

def check_position(player:dict):
    pos = player["position"]
    if pos>=40:
        player["money"]+=200
        pos = pos%40
    player["position"]=pos

def prop(player, tile, state):
    if tile["owner"]==None:
        #buy check money and buy or auction
        command = buy_option(player,tile)
        buy(player,tile,state,tile["price"],command=command)
    elif tile["owner"]!=player:
        cost = rentcalculator(tile,player)
        move_money(player,tile["owner"], cost)
    else:
        choices = []
        if tile["mortagaged"]==True:
            #mortagage buy back
            command = choice(message="",options=[("mortagage","Buy back"),("end_turn", "End turn")],default="end_turn")
            if command=="mortagage":
                mortagage()
            
        else:
            options = []
            #three option build() , sell(), end_turn()
            if tile["house_cost"]<=player["money"] and can_change_house(player,tile,+1):
                options.append(("build", "build house"))
            if tile["houses"]>0:
                options.append(("sell", "selling"))
            else:
                options.append(("mortagage", "selling"))
            options.append(("end_turn", "End turn"))
            command = choice(message="",options=options,default="End turn")
            match command:
                case "build":build(player,tile)
                case "sell":sell(player,tile)
                case "mortagage":mortagage()
def mortagage():
    #todo
    pass
def buy_option(player, tile):
    if tile["price"]>player["money"]:
        command="auction"
    else:
        command=choice(message='choose:',options=[
            ("buy", f"Buy {tile['name']} {tile['price']}"),
            ("auction", f"auction {tile['name']}")
        ])
    return command
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
        if property["type"]=="property" and property["color"]==color and property["owner"]==player:
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
        for property in state["tiles"]:
            if property["type"]=="railroad" and property["owner"]==player:
                num+=1
        return 25*(2**(num-1))
    elif tile["type"]=="company":
        opponent = tile["owner"]
        num =0
        for property in opponent["properties"]:
            if property["type"]=="company":
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
        properties = player["properties"]    
        if not properties:
            player["bankrupt"]=True
            clean_dead(player,state)
            return []
        sold = show_property(properties,player,opponent)
        player["properties"].remove(sold)
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
    tax = tile["tax"]
    move_money(player,state,tax)
def rail(player, tile):
    if tile["owner"]==None:
        buy(player,tile,state,price=200)
    elif tile["owner"]!=player:
        rent = rentcalculator(tile, player=tile["owner"])
        move_money(player,tile["owner"], rent)
def comp(player, tile,dice_num):
    if tile["owner"]==None:
        buy(player,tile,state,price=150)
    elif tile["owner"]!=player:
        rent = rentcalculator(tile,player, dice=dice_num)
        move_money(player,tile["owner"], rent)
def move_money(player, opponent, amount):
    if player["money"]>=amount:
        player["money"]-=amount
        opponent["money"]+=amount
    else:
        bankrupcy(player,amount,opponent)
def buy(player,tile,opponent, price, command=''):
    if command=="buy":
        move_money(player,opponent,tile["price"])
        tile["owner"]=player
        player["properties"].append(tile)
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
def sell(player,tile,opponent):
    if tile["houses"]==0:
        mortagage()
    else:
        if can_change_house(player,tile,-1):
            #sell option
            sell = True
            if sell:
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
def pris(player):
    
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
        if tile.get("owner") == player:
            tile["owner"]=None
            tile["houses"]=0
            tile["mortagaged"]=False
    player["properties"].clear()