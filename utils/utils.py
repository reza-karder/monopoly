from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
import os

types = {
    "INFO": { "title": "Info", "color": "cyan" },
    "ERROR": { "title": "Error", "color": "red" },
    "SUCCESS": { "title": "SUCCESSFUL", "color": "green" },
}

def clear_console():
    os.system("cls")

def print_panel(text, type="INFO", clear=True):
    global types
    console = Console()
    if(clear): clear_console()
    
    content = Text(text, justify="center", style="bold")
    panel = Panel(content, box=box.MINIMAL, style=f"on {types[type]["color"]}")
    console.print(panel)


def print_alert(text, type="INFO", clear=True):
    global types
    
    console = Console()
    if(clear): clear_console()

    console.print(f"[on {types[type]["color"]}]{types[type]["title"]}:[/on {types[type]["color"]}] {text}")