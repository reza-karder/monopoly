from utils.utils import print_alert, print_panel
from prompt_toolkit.shortcuts import choice
from features.auth import signin, signup
from models.models import create_game, find_all_games, find_game
import time
from features.logic import turner

def new_game():
    users = []

    # sign in or sign up all four players
    while(len(users) != 4):
        print_panel(f"Player {len(users) + 1} Enter")
        user = {}

        command = choice(
            message="",
            options=[
                ("signin", "Sign In"), 
                ("signup", "Sign Up"),
                ("back", "Back To Start Menu")
            ],
            default="signin"
        )

        match command:
            case "signin": user = signin()
            case "signup": user = signup()
            case "back":
                run_start_menu()
                break
        
        if(user in users):
            print_alert("This User Is Already Signed In", type="INFO", clear=False)
            time.sleep(2)
            continue
        
        print_panel("You Have Successfuly Entered Your Account", type="SUCCESS")
        time.sleep(2)  
        
        users.append(user)  

    game = create_game(users)
    turner(game)

def load_game():
    games = find_all_games()

    # if not any games saved
    if (not games):
        for i in range(3, 0, -1):
            print_panel(f"There Is No Saved Games. Back In {i}")
            time.sleep(1)

        run_start_menu()

    else:
        print_panel("Choose Your Game")
        command = choice(
            message="",
            options=
                [(games[i]["id"], f"Game Number {i + 1} ({",".join([player["name"] for player in games[i]["players"]])})") for i in range(len(games))] + 
                [("back", "Back To Start Menu")],
            default=games[0]["id"]
        )
        
        if(command == "back"):
            return run_start_menu()

        # sign in all four players of this game
        game = find_game(id=command)
        players_id = [player["id"] for player in game["players"]]
        signed_users = []

        while(len(signed_users) != 4):
            user = signin()

            if(user in signed_users):
                print_alert("This User Is Already Signed In", type="INFO", clear=False)
                time.sleep(2)
                continue

            if(user["id"] not in players_id):
                print_alert("You Are Not A Player Of This Game", type="INFO", clear=False)
                time.sleep(2)
                continue
            
            print_panel("You Have Successfuly Entered Your Account", type="SUCCESS")
            time.sleep(2)   
            signed_users.append(user)
        turner(game)
                
def run_start_menu():

    print_panel("Start Menu")

    command = choice(
        message="",
        options=[
            ("new_game", "New Game"),
            ("load_game", "Load Game"),
            ("leader_board", "Leader Board"),
            ("exit", "Exit")
        ],
        default="new_game"
    )

    match command:
        case "new_game":
            new_game()

        case "load_game":
            load_game()

        case "leader_board":
            return

        case "exit":
            return