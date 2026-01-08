from utils.utils import print_alert
from utils.utils import dice
from prompt_toolkit.shortcuts import choice

def jail(player):
    command = choice(
        message="",
        options=[
            ("jail free card", "Use Get Out Of Jail Free")if player["jail_cards_count"] else (),
            ("pay $50", "Pay $50 And Be Free."),
            ("roll the dice", "Roll The Dice, If It Comes Up Heads, You'll Be Free.")
        ],
        default="jail free card"
    )

    match command:
        case "jail free card":
                player["jail_cards_count"]-=1
                player["remained_jail"]=0

        case "pay $50":
                player["money"]-=50
                player["remained_jail"]=0

        case "roll the dice":
              #dice_num: sum of two dices numbers
            #is_double: true if its double(the dices numbers are equal)
            dice_num, is_double= dice()

            

            
