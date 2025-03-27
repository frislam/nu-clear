# version: 2.0

import os
import csv
import time
import sys
from threading import Thread
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from colorama import init, Fore, Style
from rich.console import Console
from rich.progress import track, Progress, SpinnerColumn, BarColumn, TextColumn

init(autoreset=True)
console = Console()

class ResultScraper:
    def __init__(self, input_csv="./results/nu_results.csv"):
        self.INPUT_CSV = input_csv
        self.service = Service(ChromeDriverManager().install())
        self.group_options = {
            '1': 'B.A',
            '2': 'B.S.S',
            '3': 'B.Sc',
            '4': 'B.B.A',
            '5': 'B.Music',
            '6': 'B.Sports'
        }

        # Chrome Configuration
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1200,800")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")

    def get_user_inputs(self):
        """Get all required inputs from user in correct order"""
        console.print("\n" + "="*50, style="bold blue")
        console.print("National University Result Collection System", style="bold yellow")
        console.print("="*50 + "\n", style="bold blue")

        # 1. Get Group selection first
        console.print("Available Group Options:", style="bold green")
        for key, value in self.group_options.items():
            console.print(f"{key}. {value}", style="bold cyan")

        while True:
            group_choice = input("\nSelect group number (1-6): ").strip()
            if group_choice in self.group_options:
                group = self.group_options[group_choice]
                break
            console.print("Invalid choice. Please enter a number between 1 and 6", style="bold red")

        # 2. Get Registration range
        while True:
            start_reg = input("\nEnter starting registration number (e.g., 123456789): ").strip()
            end_reg = input("Enter ending registration number (e.g., 987654321): ").strip()

            if not start_reg.isdigit() or not end_reg.isdigit():
                console.print("❌ Error: Registration numbers must be numeric", style="bold red")
                continue

            start_reg = int(start_reg)
            end_reg = int(end_reg)

            if start_reg > end_reg:
                console.print("❌ Error: Starting number must be less than ending number", style="bold red")
                continue

            break

        # 3. Get Exam Year
        while True:
            year = input("\nEnter examination year (e.g., 2023): ").strip()
            if year.isdigit() and len(year) == 4 and int(year) > 2000:
                break
            console.print("Invalid year. Please enter a valid 4-digit year (e.g., 2023)", style="bold red")

        return group, start_reg, end_reg, year

    def run_data_collection(self):
        """Main execution flow"""
        group, start_reg, end_reg, year = self.get_user_inputs()

        # Show summary
        console.print(f"\nStarting scraping from {start_reg} to {end_reg}", style="bold green")
        console.print(f"Group: {group}", style="bold green")
        console.print(f"Exam Year: {year}", style="bold green")

        # Perform scraping with progress bar
        results = self.scrape_results(start_reg, end_reg, group, year)

        if results:
            if self.save_to_csv(results):
                console.print("\n" + "="*50, style="bold blue")
                console.print(f"Successfully collected results to {self.INPUT_CSV}", style="bold green")
                console.print("="*50 + "\n", style="bold blue")
                return True

        console.print("❌ No results were collected", style="bold red")
        return False

    def scrape_results(self, start_reg, end_reg, group, year):
        """Scrape results with proper error handling"""
        driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        wait = WebDriverWait(driver, 30)  # Increased timeout
        all_results = []

        try:
            with Progress(
                SpinnerColumn(),
                "[progress.description]{task.description}",
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console,
            ) as progress:
                task = progress.add_task("Scraping...", total=end_reg - start_reg + 1)
                current_reg = start_reg
                while current_reg <= end_reg:
                    result_data = self.process_registration(driver, wait, current_reg, group, year)
                    all_results.append(result_data)

                    # Single output per registration
                    status = "Not registered" if "This Student Is Not Registered" in result_data["Name"] else "Success"
                    console.print(f"✅ {current_reg}: {status}", style="bold green")

                    current_reg += 1
                    progress.advance(task)
                    time.sleep(2)  # Be polite to the server
        except Exception as e:
            console.print(f"❌ Critical error: {str(e)}", style="bold red")
        finally:
            driver.quit()
            return all_results

    def process_registration(self, driver, wait, reg_no, group, year):
        """Process single registration with retries"""
        attempts = 0
        max_attempts = 3

        while attempts < max_attempts:
            try:
                driver.get("http://result.nu.ac.bd")
                time.sleep(1)

                # Fill the form
                exam_select = wait.until(EC.element_to_be_clickable((By.ID, "exm_code")))
                exam_select.send_keys("Bachelor Degree (Honours) 1st Year")

                group_select = driver.find_element(By.ID, "course")
                group_select.send_keys(group)

                reg_input = driver.find_element(By.ID, "reg_no")
                reg_input.clear()
                reg_input.send_keys(str(reg_no))

                year_input = driver.find_element(By.ID, "exm_year")
                year_input.clear()
                year_input.send_keys(year)

                submit_button = driver.find_element(By.NAME, "submit")
                submit_button.click()

                # Wait for result
                wait.until(EC.url_contains("result_show.php"))
                page_source = driver.page_source

                if "ERROR ! YOU'VE PROVIDED WRONG INFORMATION" in page_source:
                    return {
                        "Registration No": str(reg_no),
                        "Name": "This Student Is Not Registered",
                        "Exam Roll": "",
                        "Result": "",
                        "Grades": [],
                        "Published Date": "",
                        "Group": group,
                        "Year": year
                    }

                # Extract result data
                try:
                    result_element = driver.find_element(By.XPATH, "//div[contains(@class,'result') or contains(@id,'result') or //table]")
                    result_data = self.extract_result_data(result_element.text, str(reg_no))
                    result_data.update({
                        "Group": group,
                        "Year": year
                    })
                    return result_data
                except:
                    return {
                        "Registration No": str(reg_no),
                        "Name": "Result Format Not Recognized",
                        "Exam Roll": "",
                        "Result": "",
                        "Grades": [],
                        "Published Date": "",
                        "Group": group,
                        "Year": year
                    }

            except (TimeoutException, WebDriverException) as e:
                attempts += 1
                if attempts == max_attempts:
                    console.print(f"⚠️ Failed after {max_attempts} attempts for {reg_no}", style="bold red")
                    return {
                        "Registration No": str(reg_no),
                        "Name": "Failed to retrieve",
                        "Exam Roll": "",
                        "Result": "",
                        "Grades": [],
                        "Published Date": "",
                        "Group": group,
                        "Year": year
                    }
                time.sleep(3)  # Wait before retrying

    def extract_result_data(self, text, reg_no):
        """Extract data from result page"""
        data = {
            "Name": "",
            "Exam Roll": "",
            "Registration No": reg_no,
            "Result": "",
            "Grades": [],
            "Published Date": ""
        }

        lines = text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if "Name of Student" in line:
                data["Name"] = line.replace("Name of Student", "").strip()
            elif "Exam. Roll" in line:
                data["Exam Roll"] = line.replace("Exam. Roll", "").strip()
            elif "Result" in line and len(line.split()) < 4:
                data["Result"] = line.replace("Result", "").strip()
            elif "Published on:" in line:
                data["Published Date"] = line.replace("Published on:", "").strip()
            elif "Course Code" in line and "Obtained Grade" in line:
                for grade_line in lines[i+1:]:
                    if grade_line.strip() and len(grade_line.split()) >= 2:
                        parts = grade_line.split()
                        data["Grades"].append({
                            "Course Code": parts[0],
                            "Grade": parts[1].lower()
                        })
                    else:
                        break
        return data

    def save_to_csv(self, data):
        """Save data to CSV with all fields"""
        self.ensure_directory_exists(os.path.dirname(self.INPUT_CSV))
        try:
            with open(self.INPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'Registration No', 'Name', 'Exam Roll', 'Result',
                    'Published Date', 'Courses', 'Grades', 'Group', 'Year'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for student in data:
                    courses = ", ".join([grade['Course Code'] for grade in student['Grades']])
                    grades = ", ".join([grade['Grade'] for grade in student['Grades']])

                    writer.writerow({
                        'Registration No': student['Registration No'],
                        'Name': student['Name'],
                        'Exam Roll': student['Exam Roll'],
                        'Result': student['Result'],
                        'Published Date': student['Published Date'],
                        'Courses': courses,
                        'Grades': grades,
                        'Group': student.get('Group', ''),
                        'Year': student.get('Year', '')
                    })
            return True
        except Exception as e:
            console.print(f"❌ Error saving CSV: {str(e)}", style="bold red")
            return False

    def ensure_directory_exists(self, directory):
        """Ensure directory exists"""
        os.makedirs(directory, exist_ok=True)
        return directory

if __name__ == "__main__":
    scraper = ResultScraper()
    scraper.run_data_collection()
