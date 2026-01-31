from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print
from rich import box
import os
from random import randint
import time
from rich.progress_bar import ProgressBar

types = {
    "INFO": { "color": "cyan" },
    "ERROR": { "color": "red" },
    "SUCCESS": { "color": "green" },
}

def clear_console():
    os.system("cls")

def print_panel(*tex, type="INFO", clear=True, color= None, sleep=0):
    global types
    console = Console()
    if(clear): clear_console()
    text = ''
    for word in tex:
        text+= " "+ str(word)
    if not color:
        color = types[type]["color"] 
    content = Text(text, justify="center", style="bold")
    panel = Panel(content, box=box.MINIMAL, style=f"on {color}")    
    console.print(panel)

    if sleep:
        time.sleep(sleep)


def print_alert(text, type="INFO", clear=True, sleep=0):
    global types

    if clear:
        clear_console()

    content = content = Text(text, justify="center")
    panel = Panel(
        content, border_style=f"{types[type]['color']}"
    )
    print(panel)

    if sleep:
        time.sleep(sleep)

def dice():
    dice1 = randint(1,6)
    dice2 = randint(1,6)
    if dice1==dice2:
        return(dice1,dice2, True)
    return (dice1,dice2,False)


def show_loading(text, duration):
    progress = ProgressBar(total=100)

    for i in range(duration):
        time.sleep(1)
        progress.completed += round(100 / duration)
        print_panel(text)
        print(progress)