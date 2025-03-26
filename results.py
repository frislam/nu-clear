import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configure Chrome for headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1200,800")
chrome_options.add_argument("--no-sandbox")
service = Service("./chromedriver-linux64/chromedriver")

def ensure_directory_exists(directory="results"):
    """Ensure the output directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def extract_result_data(text, reg_no):
    """Extract relevant data from result text"""
    if "ERROR ! YOU'VE PROVIDED WRONG INFORMATION" in text:
        return {
            "Registration No": reg_no,
            "Name": "This Student Is Not Registered",
            "Exam Roll": "",
            "Result": "",
            "Grades": [],
            "Published Date": ""
        }

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
                        "Grade": parts[1]
                    })
                else:
                    break

    return data

def save_to_csv(data, filename="nu_results.csv"):
    """Save extracted data to CSV file"""
    output_dir = ensure_directory_exists()
    filepath = os.path.join(output_dir, filename)

    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Registration No', 'Name', 'Exam Roll', 'Result',
                'Published Date', 'Courses', 'Grades'
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
                    'Grades': grades
                })
        print(f"📁 Results saved to: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error saving CSV: {str(e)}")
        return False

def process_registration(driver, wait, reg_no, max_retries=5):
    """Process a single registration number with retries"""
    for attempt in range(max_retries):
        try:
            driver.get("http://result.nu.ac.bd")
            time.sleep(1)

            # Fill form
            exam_select = wait.until(EC.element_to_be_clickable((By.ID, "exm_code")))
            exam_select.send_keys("Bachelor Degree (Honours) 1st Year")

            group_select = driver.find_element(By.ID, "course")
            group_select.send_keys("B.Sc")

            reg_input = driver.find_element(By.ID, "reg_no")
            reg_input.clear()
            reg_input.send_keys(str(reg_no))

            year_input = driver.find_element(By.ID, "exm_year")
            year_input.clear()
            year_input.send_keys("2023")

            # Submit form
            submit_button = driver.find_element(By.NAME, "submit")
            submit_button.click()

            # Wait for result page (either success or error message)
            try:
                wait.until(EC.url_contains("result_show.php"))
                result_element = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class,'result') or contains(@id,'result') or //table]")))

                return extract_result_data(result_element.text, str(reg_no))

            except TimeoutException:
                print(f"⚠️ Attempt {attempt+1}: Result page not loaded for {reg_no}")
                continue

        except WebDriverException as e:
            print(f"⚠️ Attempt {attempt+1}: Browser error for {reg_no} - {str(e)}")
            time.sleep(3)  # Longer wait after browser errors
            continue

    # If all retries failed
    return {
        "Registration No": str(reg_no),
        "Name": "Processing Failed - Max Retries Reached",
        "Exam Roll": "",
        "Result": "",
        "Grades": [],
        "Published Date": ""
    }

def scrape_results(start_reg, end_reg):
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)
    all_results = []

    try:
        current_reg = start_reg
        while current_reg <= end_reg:
            print(f"\nProcessing registration: {current_reg}")

            result_data = process_registration(driver, wait, current_reg)
            all_results.append(result_data)

            if "This Student Is Not Registered" in result_data["Name"]:
                print(f"✅ Confirmed not registered: {current_reg}")
            elif "Processing Failed" in result_data["Name"]:
                print(f"❌ Failed after retries: {current_reg}")
            else:
                print(f"✅ Successfully scraped data for {current_reg}")

            current_reg += 1
            time.sleep(2)  # Be polite with requests

    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
    finally:
        driver.quit()
        return all_results

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Starting National University Result Collection")
    print("---------------------FR-----------------------")
    print("="*50 + "\n")

    start_reg = input("Enter starting registration number (e.g., 123456789): ").strip()
    end_reg = input("Enter ending registration number (e.g., 987654321): ").strip()

    if not start_reg.isdigit() or not end_reg.isdigit():
        print("❌ Error: Registration numbers must be numeric")
    else:
        start_reg = int(start_reg)
        end_reg = int(end_reg)

        if start_reg > end_reg:
            print("❌ Error: Starting number must be less than ending number")
        else:
            print(f"\nScraping results from {start_reg} to {end_reg}...")
            results = scrape_results(start_reg, end_reg)

            if results:
                if not save_to_csv(results):
                    # Try alternative save location if default fails
                    alt_path = os.path.expanduser("~/nu_results.csv")
                    print(f"Attempting to save to alternative location: {alt_path}")
                    save_to_csv(results, alt_path)
            else:
                print("❌ No results were scraped")
