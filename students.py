# version: 1.2
import os
import time
from results import ResultScraper
from rank import RankingCreator

def main():
    """Main program flow with user prompts"""
    print("\n" + "="*50)
    print("National University Result Processing System")
    print("="*50 + "\n")

    while True:
        print("\nMain Menu:")
        print("1. Scrape Results")
        print("2. Generate Rankings")
        print("3. Scrape and Generate Rankings")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            # Only scrape results
            scraper = ResultScraper()
            if scraper.run_data_collection():
                print("\nResult collection completed successfully!")
            else:
                print("\nResult collection encountered issues")

        elif choice == "2":
            # Only generate rankings
            creator = RankingCreator()
            creator.generate_rankings()

        elif choice == "3":
            # Scrape first, then generate rankings
            scraper = ResultScraper()
            if scraper.run_data_collection():
                time.sleep(1)  # Brief pause
                print("\nProceeding to generate rankings...")
                creator = RankingCreator()
                creator.generate_rankings()

        elif choice == "4":
            print("\nExiting the program. Goodbye!")
            break

        else:
            print("\nInvalid choice. Please enter a number between 1 and 4")

        # Add separator between operations
        print("\n" + "="*50)

if __name__ == "__main__":
    main()
