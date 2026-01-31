import time

from rich import print
from rich.console import Console, Group
from rich.layout import Layout
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from features.Leaderboard import show_scoreboard
from utils.utils import clear_console

colors = {
    "red": "#E61A1A",
    "pink": "#C217B9",
    "yellow": "#F1DC1B",
    "light_blue": "#1BA3F1",
    "dark_blue": "#1B49A8",
    "orange": "#EE7D21",
    "green": "#33A033",
    "brown": "#69381C",
}


def status(player, game):
    details = f"\n\
	[bold]Money[/bold]: ${player['money']}     | \
	[bold]Position[/bold]: {player['position']}     | \
	[bold]Jail Card[/bold]: {player['jail_cards_count']}"

    if player["remained_jail"]:
        details += f"     | [bold]Remained Jail[/bold]: {player['remained_jail']}"

    console = Console()
    table = Table(width=console.size.width, title="Properties")

    table.add_column("Name", justify="center", header_style="cyan")
    table.add_column("Color", justify="center", header_style="cyan")
    table.add_column("Position", justify="center", header_style="cyan")
    table.add_column("Price", justify="center", header_style="cyan")
    table.add_column("Mortgaged", justify="center", header_style="cyan")
    table.add_column("Houses", justify="center", header_style="cyan")
    table.add_column("Hotels", justify="center", header_style="cyan")

    properties = [tile for tile in game["tiles"] if tile["owner"] == player["name"]]

    for property in properties:
        houses = str((property.get("houses", 0) + property.get("hotels", 0) % 5))
        hotels = property.get("hotels", 0)

        table.add_row(
            property["name"],
            property.get("color", ""),
            str(property["index"]),
            str(property["price"]),
            "Yes" if property["is_mortgaged"] else "No",
            str(houses),
            str(hotels),
        )

    return Panel(
        Group(details, Padding(table, (1, 0, 5, 0))),
        border_style="red" if player["bankrupt"] else "cyan",
        title=player["name"],
    )


def show_board(game):
    global colors
    tiles = game["tiles"]
    console = Console()

    layout = Layout()
    layout.split_column(*[Layout(name=str(i)) for i in range(1, 12)])

    # shape of each tile
    def render_tile(index):
        tile = tiles[index]
        players_in_tile = list(
            filter(lambda player: player["position"] == index, game["players"])
        )
        players_name = ",".join([f'🙎({player["name"]})' for player in players_in_tile])
        details = ""

        if tile["type"] == "property":
            details = (
                f"{tile['houses']} Houses"
                if tile["houses"] <= 4
                else f"${tile['hotels']} Hotels"
            )

        return Layout(
            Panel(
                Text(players_name, justify="center"),
                title=tile["name"],
                subtitle=details,
                border_style=f"{colors.get(tile.get("color", None), "")}",
            )
        )

    # split the rows
    layout["1"].split_row(*[render_tile(i) for i in range(20, 31)])

    for i in range(2, 11):
        layout[str(i)].split_row(
            render_tile(21 - i),
            *([" "] * 9),
            render_tile(29 + i),
        )

    # show the current turn
    layout["6"].split_row(
        render_tile(15),
        *([" "] * 4),
        Text(
            f"{game['players'][game['turn']]['name']}'s Turn", style="bold"
        ),
        *([" "] * 4),
        render_tile(35),
    )

    layout["11"].split_row(*[render_tile(i) for i in range(10, -1, -1)])

    print(layout)


def show_status(game):
    clear_console()

    for player in game["players"]:
        print(status(player, game))
        print("\n")

    show_scoreboard(game)
    print("\n")

    show_board(game)
    print("\n\n")