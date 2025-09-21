# password_tester_final_persistent.py
import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn

API_URL = "http://127.0.0.1:8000/predict"
console = Console()

def print_result(data):
    password = data["password"]
    strength = data["strength"]
    score = data["strength_score"]
    breached = data["breached"]
    message = data["message"]

    # Strength color mapping
    strength_color = {
        "Weak": "red",
        "Medium": "yellow",
        "Strong": "green"
    }.get(strength, "white")

    # Persistent Strength Meter Bar
    bar_value = score + 1  # scale 0-2 to 1-3
    with Progress(
        TextColumn("[bold blue]Strength Meter:[/bold blue]"),
        BarColumn(bar_width=30, complete_style=strength_color),
        TextColumn(f"[{strength_color}]{strength}[/{strength_color}]"),
        transient=False  # Bar stays on screen
    ) as progress:
        task = progress.add_task("", total=3)
        progress.update(task, completed=bar_value)
        progress.refresh()

    # Display password info
    console.print(Panel.fit(f"[bold]Password:[/bold] {password}", title="🔑 Input Password"))

    # Display breach info
    breach_color = "red" if breached else "green"
    console.print(Panel.fit(
        f"[bold]Breach Status:[/bold] [{breach_color}]{'⚠️ Compromised' if breached else '✅ Safe'}[/{breach_color}]\n{message}",
        title="🛡️ Security Check"
    ))

def main():
    console.print("[bold cyan]Welcome to AI-Powered Password Strength Tester 🔐[/bold cyan]")
    console.print("Type 'exit' to quit anytime.\n")

    while True:
        pwd = console.input("[bold]Enter password:[/bold] ")
        if pwd.lower() == "exit":
            console.print("\n[bold green]👋 Exiting. Stay safe![/bold green]")
            break

        payload = {"password": pwd}
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                data = response.json()
                print_result(data)
            else:
                console.print(f"[bold red]Error {response.status_code}: {response.text}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Error connecting to API: {e}[/bold red]")

if __name__ == "__main__":
    main()
