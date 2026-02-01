from features.menu import run_start_menu
from utils.utils import print_alert

def main():
    try:
        run_start_menu()
    except:
        print_alert("Something went wrong... Don't Worry Everything Is Saved", type="ERROR", sleep=4)
        main()

main()