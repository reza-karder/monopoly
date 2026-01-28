import time

from rich import print
from rich.console import Console, Group
from rich.layout import Layout
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from utils.utils import clear_console

colors = {
    "red": "#E61A1A",
    "pink": "#C217B9",
    "yellow": "#F1DC1B",
    "light_blue": "#1BA3F1",
    "dark_blue": "#0A07A8",
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
        details += f" | [bold]Remained Jail[/bold]: {player['remained_jail']}"

    console = Console()
    table = Table(width=console.size.width, title="estates")

    table.add_column("Name", justify="center", header_style="cyan")
    table.add_column("Color", justify="center", header_style="cyan")
    table.add_column("Position", justify="center", header_style="cyan")
    table.add_column("Price", justify="center", header_style="cyan")
    table.add_column("Mortgaged", justify="center", header_style="cyan")
    table.add_column("Houses", justify="center", header_style="cyan")
    table.add_column("Hotels", justify="center", header_style="cyan")

    estates = list(
        filter(lambda estate: estate["id"] in player["estates"], game["tiles"])
    )

    for estate in estates:
        houses = (
            "0"
            if estate["type"] != "avenue"
            else str((estate["houses"] + estate["hotels"] % 5))
        )
        hotels = "0" if estate["type"] != "avenue" else str(estate["hotels"])
        table.add_row(
            estate["name"],
            estate["color"],
            str(estate["position"]),
            str(estate["price"]),
            "Yes" if estate["is_mortgaged"] else "No",
            houses,
            hotels,
        )

    return Panel(
        Group(details, Padding(table, (1, 0, 5, 0))),
        border_style="red" if player["is_bankrupted"] else "cyan",
        title=player["name"],
    )


def show_board(game):
    global colors
    tiles = game["tiles"]

    layout = Layout()
    layout.split_column(*[Layout(name=str(i)) for i in range(1, 12)])

    # shape of each tile
    def render_tile(index):
        tile = tiles[index]
        players_in_tile = list(
            filter(lambda player: player["position"] == index + 1, game["players"])
        )
        players_name = ",".join([f'🙎({player["name"]})' for player in players_in_tile])
        details = ""

        if tile["type"] == "avenue":
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
                border_style=(f"{colors[tile['color']]}" if tile["color"] else ""),
            ),
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
            f"{game['players'][game['current_turn'] - 1]['name']}'s Turn", style="bold"
        ),
        *([" "] * 4),
        render_tile(35),
    )

    layout["11"].split_row(*[render_tile(i) for i in range(10, -1, -1)])

    print(layout)


def show_score_board(game):
    console = Console()
    table = Table(title="Score Board", width=console.size.width)
    table.add_column("Rank", justify="center", header_style="cyan")
    table.add_column("Name", justify="center", header_style="cyan")
    table.add_column("Score", justify="center", header_style="cyan")
    table.add_column("Money", justify="center", header_style="cyan")
    table.add_column("Estates Count", justify="center", header_style="cyan")
    table.add_column("Bankrupted", justify="center", header_style="cyan")
    table.add_column("Time", justify="center", header_style="cyan")

    players = game["players"]
    players.sort(key=lambda player: player["score"] or player["time_play"], reverse=True)

    rank = 1
    for i in range(len(players)):
        player = players[i]
        time_play = player["time_play"]
        formatted_time = ""
        if i > 0 and players[i]["score"] != players[i - 1]["score"]:
            rank += 1

        elif player["is_bankrupted"]:
            rank += 1

        if time_play < 60:
            formatted_time = f"{time_play}s"

        elif time_play < (60 * 60):
            formatted_time = f"{round(time_play / 60)}m"

        else:
            formatted_time = f"{round(time_play / (60 * 60))}h"

        table.add_row(
            str(rank),
            player["name"],
            str(int(players[i]["score"])),
            str(int(player["money"])),
            str(len(player["estates"])),
            "Yes" if player["is_bankrupted"] else "No",
            formatted_time,
            style="on red" if player["is_bankrupted"] else "",
            end_section=True
        )

    print(table)


def show_status(game):
    clear_console()

    for player in game["players"]:
        print(status(player, game))
        print("\n")

    show_score_board(game)
    print("\n")

    show_board(game)
    print("\n\n")