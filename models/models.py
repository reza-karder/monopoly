import json
import time
import uuid
import random
from data.tiles import tiles


user_model = {
    "name": "",
    "password": "",
    "email": "",
    "games": [],
    "score": 0,
    "id": ""
}

player_model = {
    "name" : "",
    "money" : 1500,
    "position": 0,
    "bankrupt" : False,
    "doubles": 0,
    "score": 0,
    "debt": 0,
    "remained_jail" : 0,
    "jail_cards_count": 0
}

game_model = {
    "turn": 1,
    "houses" : 32,
    "hotels" : 12,
    "game_over": False,
    "money": 100000,
    "tiles": tiles,
    "cards": {
        "chance_cards": [],
        "treasure_cards": []
    }
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


def update_user(user_id, updates):
    users = find_all_users()
    user = next(user for user in users if user["id"] == user_id)
    user = user.update(updates)

    with open("data/users.json", "w", encoding="utf-8") as write_file:
        json.dump(users, write_file)

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
        **game_model, "id": str(uuid.uuid1()),
        "players": players,
        "cards": cards,
    }
    games.append(new_game)

    with open("data/games.json", "w", encoding="utf-8") as write_file:
        json.dump(games, write_file)

    return new_game


def find_all_games():
	with open("data/games.json", "r", encoding="utf-8") as read_files:
		games = json.load(read_files)

	return games or []

def find_game(id):
    games = find_all_games()
    game = list(filter(lambda game: game["id"] == id, games))[0]

    return game


def update_game(id, updates):
    games = find_all_games()
    game = next(game for game in games if game["id"] == id)
    game = game.update(updates)

    with open("data/games.json", "w", encoding="utf-8") as write_file:
        json.dump(games, write_file, indent=4)

    return games


def find_all_cards():
    with open("data/cards.json", "r", encoding="utf-8") as read_file:
        cards = json.load(read_file)
        return cards
