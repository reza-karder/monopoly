from utils.utils import print_alert, print_panel, clear_console
from prompt_toolkit.shortcuts import choice
from data.tiles import tiles as ti
import copy
from models.models import update_game
from utils.common import dice
#from features.auction import auction, mortagage
import time


colors = {"brown":2, "light_blue":3, "pink":3, "orange":3, "red":3, "yellow":3, "green":3, "dark blue":2}

def turner(game):
    global state
    global turning
    turning = True
    state = copy.deepcopy(game)
    board = copy.deepcopy(ti)
    players = state["players"]
    state["tiles"] = board
    state["turn"]=0
    global lengths 
    lengths = 4   
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
        check_position(player, dice_num)

        tile = state["tiles"][player["position"]]

        if is_double:
            player["doubles"] += 1
            if player["doubles"] == 3:
                player["position"] = 10
                player["in_jail"] = True
                player["doubles"] = 0
                pris()
                show_players(state["players"],player,dice=dice_num)
                next_turn(state, players)
                continue
        else:
            player["doubles"] = 0
        show_players(state["players"],player,dice=dice_num)
        if player["money"]<0:
            bankrupcy(player,0,state)
        check_tile(player, tile, dice_num, is_double)

        while turning:
            options = []
            show_players(players,player,)
            time.sleep(2)
            command = make_turn(player,tile)
            if command == "end_turn":
                break
            make_choice(command, player,tile)
        if player["money"]<0:
            bankrupcy(player,0,state)
        if not is_double:
            next_turn(state, players)
def next_turn(state,players):
    update_game(state["id"],state)
    time.sleep(3)
    turning = True
    time.sleep(2)
    if len(players)==lengths:
        state["turn"]= (state["turn"]+1)%len(players)
def make_turn(player,tile):
    build_option(player,tile)
    buy_option(player, tile)
    sell_option(player)
    options.append(("end_turn","End_turn"))
    
    print_panel("choose", clear=False)
    if len(options)==1:
        return "end_turn"
    command =choice(message='',options=options)
    return command
def make_choice(command, player, tile):
    match command:
        case "build":built_list_maker(player,tile["color"])
        case "sell":sell(player,state)
        case "mortagage":mortagage()
        case "buy":buy(player,tile,state)
        case "auction": auction(tile,state["players"],state)
def show_players(players,current, dice=None):
    clear_console()
    for player in players:
        properties = player["properties"]
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
        case "cards" | "cards":
            card(state["cards"],player,kind)

def check_position(player:dict, dice_num):
    player["position"] += dice_num
    pos = player["position"]
    if pos>=40:
        player["money"]+=200
        pos = pos%40
    player["position"]=pos
def prop(player, tile):
    if tile["owner"]==None:
        #buy check money and buy or auction
        pass
        
    elif tile["owner"]!=player["name"]:
        cost = rentcalculator(tile,player)
        move_money(player["name"],tile["owner"], cost)
    else:
        choices = []
        try:
            if tile.get("is_mortgaged",False)==True:
                #mortagage buy back
                options.append(("end_turn","End_turn"))
                command = choice(message="",options=[("mortagage","Buy back"),("end_turn", "End turn")],default="end_turn")
                if command=="mortagage":
                    mortagage()
        except Exception as e:
            print_alert("not doing",e)        
def build_option(player, tile):
    if own_color_set(player,tile):
        try:
            if tile.get("house_cost",None)<=player["money"]:
                options.append(("build", "build house"))
        except Exception:
            pass
def mortagage():
    #todo
    pass
def buy_option(player, tile):
    if tile.get("owner","not buyable")==None:
        if tile["price"]>player["money"]:
            options.append(("auction", f"auction {tile['name']}"))
        else:
            options.append(("buy", f"Buy {tile['name']} {tile['price']}"))
            options.append(("auction", f"auction {tile['name']}"))

def end_turn():
    turning =False
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
    color = tile.get("color",None)
    if not color:
        return False
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
def bankrupcy(player,price,opponent:dict):
    global lengths
    if player["bankrupt"]==True:
        return []
    while price>player["money"]:
        properties = [x for x in state["tiles"] if x.get("owner",None)==player["name"]]   
        if not properties:
            player["bankrupt"]=True
            clean_dead(player,state)
            lengths-=1
            return []
        sell(player,opponent)
def sell_value(tile):
    if tile["type"]=="property":
        if tile["houses"]==0:
            return tile["price"]/2
        elif tile["houses"]==4:
            return tile["hotel_cost"]/2
        else:
            return tile["house_cost"]/2
    elif tile["type"]=="railroad":
        return 100
    else:
        return tile.get("price",0)/2
def show_property(sell_list):
    sold = choice(message="",options=sell_list)
    sold_tile = next(tile for tile in state["tiles"] if tile["name"]==sold)
    return sold_tile 
def card(cards,player,kind):
#    if not cards:
#        return
#    _community_card_number = 10
#    random_card = randint(1,_community_card_number)
#    if kind=="cardchance":
#        random_card+=_community_card_number
#    card_func = globals()[f"{cards[random_card-1]}_func"]
#    card_func(player)
    turning = False
def taxs(player,tile):
    tax = tile["amount"]
    move_money(player["name"],"state",tax)
    turning = False
def rail(player, tile):
    if tile["owner"]==None:
        buy_option(player, tile)
    elif tile["owner"]!=player["name"]:
        for user in state["players"]:
            if user["name"]==tile["owner"]:
                owner = user
                break
        rent = rentcalculator(tile, player=owner)
        move_money(player["name"],tile["owner"], rent)
    
def comp(player, tile,dice_num):
    if tile["owner"]==None:
        buy(player,tile,state)
    elif tile["owner"]!=player["name"]:
        rent = rentcalculator(tile,player, dice=dice_num)
        move_money(player["name"],tile["owner"], rent)
def move_money(player, opponent, amount):
    opponent = next((x for x in state["players"] if x["name"]==opponent), state)
    player = next((x for x in state["players"] if x["name"]==player), state)
    if player["money"]>=amount:
        player["money"]-=amount
        opponent["money"]+=amount
    else:
        bankrupcy(player,amount,opponent)
def buy(player,tile,opponent):
    move_money(player["name"],opponent.get("name","state"),tile["price"])
    tile["owner"]=player["name"]
    player["value"]+=tile["price"]
    player["properties"] = [x for x in state["tiles"] if x.get("owner",None)==player["name"]]
def built_list_maker(player,color):
    color_set = [til for til in state["tiles"] if (til.get("owner",None)==player["name"] and til.get('color',None)==color)]
    built_list = [(pro["name"],pro["name"]+" "+str(pro.get("house_cost"))) for pro in color_set if pro["is_mortgaged"]==False]
    built_list = []
    for pro in sorted(color_set,key=lambda x: x["index"]):
        if pro["is_mortgaged"]==True:
            continue
        text = pro["name"]
        text+= '*'*pro.get("houses",0)
        text+=str(pro.get("house_cost",0))
        built_list.append((pro["name"],text)) 
    built = show_property(built_list)
    build(player,built)
def build(player,tile):
    if can_change_house(player,tile,+1):
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
    else:
        print_alert("cant build")
def real_sell(player,opponent:dict, tile):        
    if tile["houses"]==0:
        mortagage()
    else:
        if can_change_house(player,tile,-1):
            #sell option

            if tile["houses"]==4:
                state["houses"]-=4
                state["hotels"]+=1
                tile["houses"]-=1
                move_money(opponent.get("name","state"),player["name"],sell_value(tile))       
            elif (tile["houses"]<4):
                state["houses"]+=1
                tile["houses"]-=1
                move_money(opponent.get("name","state"),player["name"],sell_value(tile))       
            else:
                print_alert("problem")
def sell(player,opponent:dict):
    
    properties = [til for til in state["tiles"] if til.get("owner",None)==player["name"]]
    sell_list = []
    for pro in sorted(properties,key=lambda x: sell_value(x)):
        text = pro["name"]
        text+= '*'*pro.get("houses",0)
        text+=str(sell_value(pro))
        sell_list.append((pro["name"],text))    
    clear_console()
    show_players(state["players"],player)
    sold = show_property(sell_list)
    real_sell(player,opponent,sold)
def pris():
    turning = False
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
if __name__ == "__main__":
    turner(game)