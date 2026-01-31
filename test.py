users = [
    {"name": "reza"},
    {"name": "ali"}
]

users2 = [user for user in users]

for user in users2:
    user["name"] = 'hi'

print(users)