import os
import json
from features.scoreboard import update_scoreboard

def run_test():
    print("🚀 Running Scoreboard Test (4 Players)...\n")
    
    p1 = {
        "name": "SHAHROOZ_Winner",
        "money": 3000,
        "bankrupt": False,
        "properties": [
            {"name": "Park Place", "price": 350, "type": "property"},
            {"name": "Boardwalk", "price": 400, "type": "property"}
        ]
    }

    p2 = {
        "name": "REZA_Loser_1",
        "money": 0,
        "bankrupt": True,
        "properties": []
    }

    p3 = {
        "name": "ISUN_Loser_2",
        "money": 0,
        "bankrupt": True,
        "properties": []
    }
    
    p4 = {
        "name": "HADI_Loser_3",
        "money": 0, 
        "bankrupt": True,
        "properties": []
    }

 
# این تابع وظیفه داره جمع پول + ارزش ملک رو انجام بده و فایل خروجی را بسازه.

    all_players = [p1, p2, p3, p4]

    print(f"👥 Players: {[p['name'] for p in all_players]}")

    update_scoreboard(all_players)
    
# اعتبار سنجی
# برای اینکه بفهمیم آیا فایل Scoreboard.json در پوشه data ساخته شده یا خیر

    if os.path.exists("data/Scoreboard.json"):
        print("\n✅ Scoreboard.json updated successfully!")
    else:
        print("\n❌ File not found.")

if __name__ == "__main__":
    run_test()