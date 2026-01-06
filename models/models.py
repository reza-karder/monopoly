import json
import uuid
import random


user_model = {
    "name": "",
    "password": "",
    "email": "",
    "games": [],
    "time_play": 0,
    "id": ""
}

player_model = {
    "username" : "yasin2007",
    "money" : 1500,
    "in_jail" : False,
    "position": 1,
    "properties": [],
    "jail_pass": 0,
    "dice_turn" : 3,
    "bankrupt" : False,
    "value" : 0,
    "selling_power" : 0,
    "doubles": 0
}

state_model = {
    "turn": 1,
    "houses" : 32,
    "hotels" : 12,
    "game_over": False,
    "money": 100000
}


def create_user(email, password, name):
    global user_model

    users = find_all_users()
    user = {
        **user_model, "email": email,
        "password": password,
        "name": name,
        "id": str(uuid.uuid1())
    }
    users.append(user)

    with open("data/users.json", "w", encoding="utf-8") as write_file:
        json.dump(users, write_file)

    return user


def find_all_users():
    with open("data/users.json", "r", encoding="utf-8") as read_files:
        users = json.load(read_files)
        return users or []


def find_user(id):
    users = find_all_users()
    user = list(filter(lambda user: user["id"] == id, users))[0]

    return user


def create_game(users):
    cards = find_all_cards()
    games = find_all_games()
    random.shuffle(users)
    random.shuffle(cards["chance_cards"])
    random.shuffle(cards["treasure_cards"])

    players = [{
        **player_model, "id": users[i]["id"],
        "name": users[i]["name"]
    } for i in range(len(users))]
    new_game = {
        **state_model, "id": str(uuid.uuid1()),
        "players": players,
        "cards": cards,
    }
    games.append(new_game)

    with open("data/games.json", "w", encoding="utf-8") as write_file:
        json.dump(games, write_file)

    return new_game


def find_all_games():
    try:
        with open("data/games.json", "r", encoding="utf-8") as read_files:
            read = read_files.read().strip()
            if not read:
                print("dsflhfs")
                return []
            games = json.loads(read)
            return games
    except json.JSONDecodeError as e:
        print(e, "jkfshskf")
        return []
    except Exception as e:
        print("its", e)
        return []

def find_game(id):
    games = find_all_games()
    game = list(filter(lambda game: game["id"] == id, games))[0]

    return game


def update_game(id, updates):
    games = find_all_games()
    game = list(filter(lambda game: game["id"] == id, games))[0]
    index = games.index(game)
    updated_game = updates
    games[index] = updated_game

    with open("data/games.json", "w", encoding="utf-8") as write_file:
        json.dump(games, write_file, indent=4)

    return games


def find_all_cards():
    with open("data/cards.json", "r", encoding="utf-8") as read_file:
        cards = json.load(read_file)
        return cards
