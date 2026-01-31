from models.models import find_all_users
from rich.table import Table
from rich.console import Console
from rich import print

from utils.utils import clear_console


def calculate_player_score(player, game):
    
    final_cash = player.get("money", 0)
    total_assets = final_cash
    valid_property_count = 0
    
    # بررسی لیست املاک
    for tile in game["tiles"]:
        if tile["owner"] == player["name"]:
            total_assets += tile.get("price", 0)
            valid_property_count += 1
            
    return {
        "total_assets": total_assets,
        "property_count": valid_property_count,
        "final_cash": final_cash,
    }

def show_scoreboard(game):
    game_results = []
    all_players = game["players"]
    
    for player in all_players:
        scores = calculate_player_score(player, game)
        
        # تعیین وضعیت بازیکن
        status = "Playing"

        if player.get("bankrupt", False) is True:
            status = "Bankrupt"

        entry = {
            "name": player.get("name", "Unknown"), 
            "total_assets": scores["total_assets"],
            "property_count": scores["property_count"],
            "final_cash": scores["final_cash"],
            "status": status,
            "debt": player["debt"],
        }
        game_results.append(entry)
    
    # مرتب‌سازی لیست همین بازی
    # اولویت‌ها: ۱. ارزش کل ۲. تعداد ملک ۳. پول نقد
    game_results.sort(key=lambda x: (
        x['total_assets'],      
        x['property_count'],    
        x['final_cash'],
        x["debt"]
    ), reverse=True)

    console = Console()
    table = Table(title="Score Board", width=console.size.width)
    table.add_column("Rank", justify="center", header_style="cyan")
    table.add_column("Name", justify="center", header_style="cyan")
    table.add_column("Score", justify="center", header_style="cyan")
    table.add_column("Cash", justify="center", header_style="cyan")
    table.add_column("Property Count", justify="center", header_style="cyan")
    table.add_column("Status", justify="center", header_style="cyan")
    table.add_column("Debt", justify="center", header_style="cyan")

    for i, entry in enumerate(game_results):
        table.add_row(
            str(i+1),
            entry["name"],
            str(entry["total_assets"]),
            str(entry["final_cash"]),
            str(entry["property_count"]),
            str(entry["status"]),
            str(entry["debt"]),
        )

    print(table)

def show_leaderboard():
    users = find_all_users()

    console = Console()
    table = Table(title="Leader Board", width=console.size.width)
    table.add_column("Rank", justify="center", header_style="cyan")
    table.add_column("Name", justify="center", header_style="cyan")
    table.add_column("Score", justify="center", header_style="cyan")

    for i, user in enumerate(users):
        table.add_row(
            str(i+1),
            user["name"],
            str(user["score"])
        )

    clear_console()
    print(table)