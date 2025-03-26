import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from fpdf import FPDF

# Configuration
INPUT_CSV = "./results/nu_results.csv"
OUTPUT_DIR = "./reports"
GRADE_POINTS = {
    'a+': 4.00, 'a': 3.75, 'a-': 3.50,
    'b+': 3.25, 'b': 3.00, 'b-': 2.75,
    'c+': 2.50, 'c': 2.25, 'd': 2.00,
    'f': 0.00, 'fail': 0.00,
    'absent': -1.00  # Added Absent with lowest value
}

# Chrome Configuration
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1200,800")
chrome_options.add_argument("--no-sandbox")
service = Service("./chromedriver-linux64/chromedriver")

def main():
    """Main program flow with user prompts"""
    if run_data_collection():
        while True:
            choice = input("\nWould you like to generate ranking reports? (yes/no): ").strip().lower()
            if choice in ['yes', 'y']:
                generate_rankings()
                break
            elif choice in ['no', 'n']:
                print("\nResults saved without ranking reports.")
                break
            else:
                print("Please enter 'yes' or 'no'")

def run_data_collection():
    """Run the data collection process"""
    print("\n" + "="*50)
    print("Starting National University Result Collection")
    print("---------------------FR-----------------------")
    print("="*50 + "\n")

    start_reg = input("Enter starting registration number (e.g., 123456789): ").strip()
    end_reg = input("Enter ending registration number (e.g., 987654321): ").strip()

    if not start_reg.isdigit() or not end_reg.isdigit():
        print("❌ Error: Registration numbers must be numeric")
        return False

    start_reg = int(start_reg)
    end_reg = int(end_reg)

    if start_reg > end_reg:
        print("❌ Error: Starting number must be less than ending number")
        return False

    print(f"\nScraping results from {start_reg} to {end_reg}...")
    results = scrape_results(start_reg, end_reg)

    if results:
        if save_to_csv(results):
            print("\n" + "="*50)
            print(f"Successfully collected results to {INPUT_CSV}")
            print("="*50 + "\n")
            return True
    print("❌ No results were collected")
    return False

def scrape_results(start_reg, end_reg):
    """Scrape results for range of registration numbers"""
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
            else:
                print(f"✅ Successfully accessed result for {current_reg}")

            current_reg += 1
            time.sleep(2)
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
    finally:
        driver.quit()
        return all_results

def process_registration(driver, wait, reg_no):
    """Process single registration - retry until result_show.php is accessed"""
    while True:
        try:
            driver.get("http://result.nu.ac.bd")
            time.sleep(1)

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

            submit_button = driver.find_element(By.NAME, "submit")
            submit_button.click()

            try:
                wait.until(EC.url_contains("result_show.php"))
                page_source = driver.page_source

                if "ERROR ! YOU'VE PROVIDED WRONG INFORMATION" in page_source:
                    return {
                        "Registration No": str(reg_no),
                        "Name": "This Student Is Not Registered",
                        "Exam Roll": "",
                        "Result": "",
                        "Grades": [],
                        "Published Date": ""
                    }

                try:
                    result_element = driver.find_element(By.XPATH, "//div[contains(@class,'result') or contains(@id,'result') or //table]")
                    return extract_result_data(result_element.text, str(reg_no))
                except:
                    return {
                        "Registration No": str(reg_no),
                        "Name": "Result Format Not Recognized",
                        "Exam Roll": "",
                        "Result": "",
                        "Grades": [],
                        "Published Date": ""
                    }

            except TimeoutException:
                print(f"⌛ Timeout for {reg_no} - retrying...")
                time.sleep(3)
                continue

        except WebDriverException as e:
            print(f"⚠️ WebDriver error for {reg_no}: {str(e)} - retrying...")
            time.sleep(5)
            continue
        except Exception as e:
            print(f"⚠️ Unexpected error for {reg_no}: {str(e)} - retrying...")
            time.sleep(5)
            continue

def extract_result_data(text, reg_no):
    """Extract data from successful result page"""
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
                        "Grade": parts[1].lower()  # Convert to lowercase for consistency
                    })
                else:
                    break
    return data

def save_to_csv(data):
    """Save data to CSV"""
    ensure_directory_exists(os.path.dirname(INPUT_CSV))
    try:
        with open(INPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
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
        return True
    except Exception as e:
        print(f"❌ Error saving CSV: {str(e)}")
        return False

def generate_rankings():
    """Generate ranking reports with Absent grade handling"""
    print("\nGenerating ranking reports...")
    students = load_student_data()

    if not students:
        print("No valid student records found")
        return

    ranked_students = rank_students(students)
    generate_pdf_report(ranked_students)
    print(f"\nRanking report generated at: {os.path.join(OUTPUT_DIR, 'ranking.pdf')}")

def load_student_data():
    """Load student data from CSV with Absent grade handling"""
    students = []
    if not os.path.exists(INPUT_CSV):
        print(f"Error: CSV file not found at {INPUT_CSV}")
        return students

    with open(INPUT_CSV, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row_num, row in enumerate(reader, 1):
            try:
                if "This Student Is Not Registered" in row['Name']:
                    continue

                raw_grades = [g.strip().lower() for g in row['Grades'].split(',')]  # Convert to lowercase
                grades = [normalize_grade(g) for g in raw_grades]
                courses = [c.strip() for c in row['Courses'].split(',')]

                if len(courses) != 7 or len(grades) != 7:
                    continue

                # Calculate point with Absent handling
                point = sum(GRADE_POINTS.get(g, -1.00) for g in grades) / 7

                students.append({
                    'Name': row['Name'],
                    'Exam Roll': row['Exam Roll'],
                    'Registration No': row['Registration No'],
                    'Result': row['Result'],
                    'Courses': courses,
                    'Grades': grades,
                    'Raw Grades': raw_grades,
                    'Point': round(point, 2)
                })
            except Exception as e:
                print(f"Row {row_num}: Error processing record - {str(e)}")
    return students

def rank_students(students):
    """Rank students with proper tie-breaking including Absent grades"""
    if not students:
        return []

    # Sort by point (descending) and then by grade quality
    students.sort(key=lambda x: (
        -x['Point'],
        [GRADE_POINTS.get(g, -1.00) for g in x['Grades']]  # Handle Absent grades
    ))

    # Assign ranks with proper tie-breaking
    current_rank = 1
    for i, student in enumerate(students):
        if i > 0:
            prev = students[i-1]
            if not (student['Point'] == prev['Point'] and
                    student['Grades'] == prev['Grades']):
                current_rank = i + 1

        student['Rank'] = current_rank

    return students

def generate_pdf_report(students):
    """Generate PDF report showing Absent grades"""
    ensure_directory_exists(OUTPUT_DIR)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "National University - Examination Results", 0, 1, 'C')
    pdf.cell(0, 10, "Official Ranking List (Including Absentees)", 0, 1, 'C')
    pdf.ln(10)

    for student in students:
        pdf.set_font("Arial", '', 12)

        info = [
            f"Rank: {student['Rank']}",
            f"Name: {student['Name']}",
            f"Roll: {student['Exam Roll']}",
            f"Reg: {student['Registration No']}",
            f"Result: {student['Result']}",
            f"GPA: {student['Point']:.2f}"
        ]

        for line in info:
            pdf.cell(0, 10, line, 0, 1)
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(40, 10, "Course Code", 1)
        pdf.cell(30, 10, "Grade", 1)
        pdf.ln()
        pdf.set_font("Arial", '', 12)

        for course, grade in zip(student['Courses'], student['Raw Grades']):
            pdf.cell(40, 10, course, 1)
            pdf.cell(30, 10, grade.upper(), 1)  # Show grades in uppercase
            pdf.ln()

        pdf.ln(10)

    pdf.output(os.path.join(OUTPUT_DIR, "ranking.pdf"))

def ensure_directory_exists(directory):
    """Ensure directory exists"""
    os.makedirs(directory, exist_ok=True)
    return directory

def normalize_grade(grade):
    """Convert grade to standard format including Absent"""
    grade = str(grade).strip().lower()
    if grade == 'fail':
        return 'f'
    elif grade == 'absent':
        return 'absent'  # Keep absent as is
    return grade

if __name__ == "__main__":
    main()
