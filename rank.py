# version: 02
# Author: Sultan FR
import csv
import os
from fpdf import FPDF

# Configuration
INPUT_CSV = "./results/nu_results.csv"
OUTPUT_DIR = "./reports"

# Grade to point mapping (case-insensitive) with Absent added
GRADE_POINTS = {
    'a+': 4.00, 'a': 3.75, 'a-': 3.50,
    'b+': 3.25, 'b': 3.00, 'b-': 2.75,
    'c+': 2.50, 'c': 2.25, 'd': 2.00,
    'f': 0.00, 'fail': 0.00,
    'absent': -1.00  # Added Absent with lowest value
}

def normalize_grade(grade):
    """Convert grade to standard format including Absent"""
    grade = str(grade).strip().lower()
    if grade == 'fail':
        return 'f'
    elif grade == 'absent':
        return 'absent'  # Keep absent as is
    return grade

def load_student_data():
    """Load and validate student data from CSV with Absent handling"""
    students = []

    if not os.path.exists(INPUT_CSV):
        print(f"Error: CSV file not found at {INPUT_CSV}")
        return students

    with open(INPUT_CSV, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row_num, row in enumerate(reader, 1):
            try:
                # Skip not registered students
                if "This Student Is Not Registered" in row['Name']:
                    continue

                # Process grades and courses
                raw_grades = [g.strip() for g in row['Grades'].split(',')]
                grades = [normalize_grade(g) for g in raw_grades]
                courses = [c.strip() for c in row['Courses'].split(',')]

                # Validate we have exactly 7 courses and grades
                if len(courses) != 7 or len(grades) != 7:
                    print(f"Row {row_num}: Expected 7 courses/grades, got {len(courses)}/{len(grades)}")
                    continue

                # Calculate GPA with Absent handling
                try:
                    point = sum(GRADE_POINTS.get(g, -1.00) for g in grades) / 7
                except Exception as e:
                    print(f"Row {row_num}: Error calculating GPA - {str(e)}")
                    continue

                students.append({
                    'Name': row['Name'],
                    'Exam Roll': row['Exam Roll'],
                    'Registration No': row['Registration No'],
                    'Result': row['Result'],
                    'Courses': courses,
                    'Grades': grades,
                    'Raw Grades': raw_grades,  # Keep original for display
                    'Point': round(point, 2)
                })
            except Exception as e:
                print(f"Row {row_num}: Error processing record - {str(e)}")
    return students

def rank_students(students):
    """Rank students with proper tie-breaking including Absent grades"""
    if not students:
        return []

    # Sort by Point (descending) and then by all grades (for proper tie-breaking)
    students.sort(key=lambda x: (
        -x['Point'],
        [GRADE_POINTS.get(g, -1.00) for g in x['Grades']]  # Handle Absent grades
    ))

    # Assign ranks with strict tie handling
    current_rank = 1
    for i, student in enumerate(students):
        if i > 0:
            # Only give same rank if identical GPA AND identical grade distribution
            prev = students[i-1]
            if not (student['Point'] == prev['Point'] and
                    student['Grades'] == prev['Grades']):
                current_rank = i + 1

        student['Rank'] = current_rank

    return students

def generate_pdf_report(students):
    """Generate properly formatted PDF report showing Absent grades"""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "National University - Examination Results", 0, 1, 'C')
    pdf.cell(0, 10, "Ranking List By Rakib-35", 0, 1, 'C')
    pdf.ln(10)

    for student in students:
        pdf.set_font("Arial", '', 12)

        # Student info
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

        # Grades table - fixed column widths
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

def generate_reports():
    """Generate all reports"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading student data...")
    students = load_student_data()

    if not students:
        print("No valid student records found")
        return

    print(f"Processing {len(students)} records...")
    ranked_students = rank_students(students)

    # Verify ranking
    print("\nVerifying ranks...")
    rank_counts = {}
    for student in ranked_students:
        rank = student['Rank']
        rank_counts[rank] = rank_counts.get(rank, 0) + 1

    for rank, count in sorted(rank_counts.items()):
        print(f"Rank {rank}: {count} student(s)")

    print("\nGenerating PDF report...")
    generate_pdf_report(ranked_students)

    print(f"\nReport successfully generated at: {os.path.join(OUTPUT_DIR, 'ranking.pdf')}")

if __name__ == "__main__":
    generate_reports()
