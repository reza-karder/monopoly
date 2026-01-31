from features.move_money import move_money
from utils.utils import print_alert, print_panel
from utils.utils import dice
from prompt_toolkit.shortcuts import choice

def jail(player, game):
    options = [
        ("roll the dice", "Roll The Dice, If It Comes Up Heads, You'll Be Free.")
    ]

    if player["money"] >= 50:
        options.append(("pay $50", "Pay $50 And Be Free."))

    if player["jail_cards_count"]:
        options.append(("jail free card", "Use Get Out Of Jail Free"))

    print_panel(f"{player['name']} You Are In Jail Choose The Action")
    command = choice(
        message="",
        options=options,
        default=""
    )

    match command:
        case "jail free card":
                player["jail_cards_count"]-=1
                player["remained_jail"]=0
                print_alert("You Got Free", type="SUCCESS", sleep=2)

        case "pay $50":
                player["money"]-=50
                player["remained_jail"]=0
                print_alert("You Got Free", type="SUCCESS", sleep=2)

        case "roll the dice":
            dice1, dice2, is_double = dice()

            if is_double:
                print_alert(f"You Have Rolled ({dice1}, {dice2}) and Got Free", type="SUCCESS", sleep=2)
                player["remained_jail"] = 0

            elif player["remained_jail"] == 1:
                print_alert(f"You Have Rolled ({dice1}, {dice2}) and Must Pay $50", sleep=2)
                is_paid = move_money(player["name"], "game", 50, game)
                if is_paid:
                    print_alert("You Paid $50 Got Free", type="SUCCESS", sleep=2)
                    player["remained_jail"] = 0

            else:
                player["remained_jail"] -= 1
                print_alert(f"You Have Rolled ({dice1}, {dice2}) and Remain In Jail", sleep=2)