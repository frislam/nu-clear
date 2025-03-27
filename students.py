# version: 2.0
import os
import time
import tkinter as tk
from tkinter import messagebox, simpledialog
from results import ResultScraper
from rank import RankingCreator
from colorama import init, Fore, Style
from rich.console import Console
from rich.table import Table

init(autoreset=True)
console = Console()

def main():
    """Main program flow with user prompts"""
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    def show_menu():
        console.print("\n" + "="*50, style="bold blue")
        console.print("National University Result Processing System", style="bold yellow")
        console.print("="*50 + "\n", style="bold blue")

        while True:
            console.print("\nMain Menu:", style="bold green")
            console.print("1. Scrape Results", style="bold cyan")
            console.print("2. Generate Rankings", style="bold cyan")
            console.print("3. Scrape and Generate Rankings", style="bold cyan")
            console.print("4. Exit", style="bold cyan")

            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == "1":
                scrape_results()
            elif choice == "2":
                generate_rankings()
            elif choice == "3":
                scrape_and_generate_rankings()
            elif choice == "4":
                console.print("\nExiting the program. Goodbye!", style="bold red")
                break
            else:
                console.print("\nInvalid choice. Please enter a number between 1 and 4", style="bold red")

            # Add separator between operations
            console.print("\n" + "="*50, style="bold blue")

    def scrape_results():
        scraper = ResultScraper()
        if scraper.run_data_collection():
            console.print("\nResult collection completed successfully!", style="bold green")
        else:
            console.print("\nResult collection encountered issues", style="bold red")

    def generate_rankings():
        creator = RankingCreator()
        creator.generate_rankings()

    def scrape_and_generate_rankings():
        scraper = ResultScraper()
        if scraper.run_data_collection():
            time.sleep(1)  # Brief pause
            console.print("\nProceeding to generate rankings...", style="bold green")
            creator = RankingCreator()
            creator.generate_rankings()

    show_menu()

if __name__ == "__main__":
    main()
