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
    "id":
    "",
    "name":
    "",
    "money":
    0,
    "properties": [{
        "id": "",
        "type": "AVENUE",
        "homes_count": 0,
        "hotels_count": 0,
        "is_mortgaged": False
    }],
    "position":
    1,
    "remained_jail":
    0,
    "has_jail_card":
    False
}

game_model = {
    "id": "",
    "current_turn": 1,
    "time_play": 0,
    "is_over": False,
    "bank": {
        "money": 0,
        "properties": [],
        "mortgaged_properties": []
    },
    "players": [],
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
        "cards": cards
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
    game = list(filter(lambda game: game["id"] == id, games))[0]
    index = games.index(game)
    game = {**game, **updates}
    games[index] = game

    with open("data/games.json", "w", encoding="utf-8") as write_file:
        json.dump(games, write_file)

    return games


def find_all_cards():
    with open("data/cards.json", "r", encoding="utf-8") as read_file:
        cards = json.load(read_file)
        return cards
