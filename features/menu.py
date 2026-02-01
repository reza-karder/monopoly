from features.Leaderboard import show_leaderboard
from utils.utils import print_alert, print_panel, show_loading
from prompt_toolkit.shortcuts import choice
from features.auth import signin, signup
from models.models import create_game, find_all_games, find_game
import time
from features.logic import turner


def new_game():
    users = []

    # sign in or sign up all four players
    while len(users) != 4:
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
            case "signin":
                user = signin()
            case "signup":
                user = signup()
            case "back":
                run_start_menu()
                break

        if user in users:
            print_alert("This User Is Already Signed In", type="INFO", clear=False, sleep=2)
            continue

        print_alert("You Have Successfully Entered Your Account", type="SUCCESS", sleep=2)

        users.append(user)

    if len(users) == 4:
        game = create_game(users)
        turner(game)


def load_game():
    games = find_all_games()
    ongoing_games = [game for game in games if not game["game_over"]]
    # if not any games saved
    if not ongoing_games:
        show_loading("No Ongoing Game - Returning To Main Menu", duration=5)

        run_start_menu()

    else:
        print_panel("Choose Your Game")
        options = []

        for i, game in enumerate(ongoing_games):
            players = [player["name"] for player in games[i]["players"]]
            options.append((game["id"], f"Game Number {i+1}: ({', '.join(players)})"))

        options.append(("back", "Back To Start Menu"))

        command = choice(
            message="",
            options=options
        )

        if command == "back":
            return run_start_menu()

        # sign in all four players of this game
        game = find_game(id=command)
        players_id = [player["id"] for player in game["players"]]
        signed_users = []

        while len(signed_users) != 4:
            user = signin()

            if user in signed_users:
                print_alert("This User Is Already Signed In", type="INFO", clear=False, sleep=2)

                continue

            if user["id"] not in players_id:
                print_alert("You Are Not A Player Of This Game", type="INFO", clear=False, sleep=2)

                continue

            print_alert("You Have Successfully Entered Your Account", type="SUCCESS", sleep=2)

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
            show_leaderboard()
            choice(message="", options=[("return", "Return to Main Menu")])
            run_start_menu()

        case "exit":
            return
