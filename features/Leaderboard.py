import json
import os
from utils.utils import print_alert, print_panel

SCOREBOARD_FILE = "data/Scoreboard.json"

def calculate_player_score(player):
    
    final_cash = player.get("money", 0)
    total_assets = final_cash
    valid_property_count = 0
    
    # بررسی لیست املاک
    if "properties" in player:
        for tile in player["properties"]:
            total_assets += tile.get("price", 0)
            if tile.get("type") == "property":
                valid_property_count += 1
            
    return {
        "total_assets": total_assets,
        "property_count": valid_property_count,
        "final_cash": final_cash
    }

def update_scoreboard(all_players):
    game_results = []
    
    for player in all_players:
        scores = calculate_player_score(player)
        
        # تعیین وضعیت بازیکن
        status = "Playing"
        if player.get("bankrupt", False) is True:
            status = "Bankrupt"
        entry = {
            "name": player.get("name", "Unknown"), 
            "total_assets": scores["total_assets"],
            "property_count": scores["property_count"],
            "final_cash": scores["final_cash"],
            "status": status
        }
        game_results.append(entry)
    
    # مرتب‌سازی لیست همین بازی
    # اولویت‌ها: ۱. ارزش کل ۲. تعداد ملک ۳. پول نقد
    game_results.sort(key=lambda x: (
        x['total_assets'],      
        x['property_count'],    
        x['final_cash']         
    ), reverse=True)

    existing_data = []
    if os.path.exists(SCOREBOARD_FILE):
        try:
            with open(SCOREBOARD_FILE, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except:
            existing_data = []
    existing_data.extend(game_results)
    
    # ذخیره فایل JSON
    try:
        os.makedirs(os.path.dirname(SCOREBOARD_FILE), exist_ok=True)
        
        with open(SCOREBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)

        print_alert("Results successfully saved to Leaderboard", type="SUCCESS", clear=False)
        
    except Exception as e:
        print_alert(f"Error saving leaderboard: {e}", type="ERROR", clear=False)

def show_leaderboard():
    print_panel("🏆 LEADERBOARD 🏆")

    if not os.path.exists(SCOREBOARD_FILE):
        print_alert("No records found yet.", type="INFO", clear=False)
        input("\nPress Enter to return...")
        return

    try:
        with open(SCOREBOARD_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        print_alert("Error reading leaderboard file.", type="ERROR", clear=False)
        input("\nPress Enter to return...")
        return

    data.sort(key=lambda x: (x['total_assets'], x['property_count'], x['final_cash']), reverse=True)

    # نمایش جدول با فرمت منظم
    print(f"{'Rank':<5} {'Name':<15} {'Total Value':<12} {'Props':<6} {'Cash':<8} {'Status':<10}")
    print("-" * 65)

    # نمایش ۱۰ رکورد برتر
    for i, entry in enumerate(data[:10]): 
        stat = entry.get('status', '-')
    
        status_display = stat
        if stat == "Bankrupt":
            status_display = "❌ Lost"
        elif stat == "Playing" or stat == "Winner": 
            status_display = "✅ Active"

        print(f"{i+1:<5} {entry['name']:<15} {entry['total_assets']:<12} {entry['property_count']:<6} {entry['final_cash']:<8} {status_display:<10}")
    
    print("-" * 65)
    print("\n")
    input("Press Enter to return to menu...")