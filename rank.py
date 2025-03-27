# version: 2.1
import os
import csv
from fpdf import FPDF

# Configuration
INPUT_CSV = os.path.join(".", "results", "nu_results.csv")
OUTPUT_DIR = os.path.join(".", "reports")
GRADE_POINTS = {
    'a+': 4.00, 'a': 3.75, 'a-': 3.50,
    'b+': 3.25, 'b': 3.00, 'b-': 2.75,
    'c+': 2.50, 'c': 2.25, 'd': 2.00,
    'f': 0.00, 'fail': 0.00,
    'absent': -1.00  # Added Absent with lowest value
}

class RankingCreator:
    def __init__(self, input_csv=INPUT_CSV, output_dir=OUTPUT_DIR):
        self.INPUT_CSV = input_csv
        self.OUTPUT_DIR = output_dir

    def generate_rankings(self):
        """Generate ranking reports for all groups"""
        print("\nGenerating ranking reports for all groups...")

        # Load and filter student data
        all_students = self.load_student_data()

        if not all_students:
            print("No valid student records found")
            return

        # Group students by their group
        grouped_students = {}
        for student in all_students:
            group = student.get('Group', 'Unknown')
            if group not in grouped_students:
                grouped_students[group] = []
            grouped_students[group].append(student)

        # Generate separate PDFs for each group
        for group, students in grouped_students.items():
            if students:
                ranked_students = self.rank_students(students)
                year = students[0].get('Year', '')
                self.generate_pdf_report(ranked_students, group, year)
                print(f"Generated ranking report for {group} group")

        print(f"\nAll ranking reports generated in: {self.OUTPUT_DIR}")

    def load_student_data(self):
        """Load and filter student data from CSV"""
        students = []
        if not os.path.exists(self.INPUT_CSV):
            print(f"Error: CSV file not found at {self.INPUT_CSV}")
            return students

        with open(self.INPUT_CSV, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row_num, row in enumerate(reader, 1):
                try:
                    # Skip unregistered and format-not-recognized students
                    if ("This Student Is Not Registered" in row['Name'] or
                        "Result Format Not Recognized" in row['Name']):
                        continue

                    raw_grades = [g.strip().lower() for g in row['Grades'].split(',')]
                    grades = [self.normalize_grade(g) for g in raw_grades]
                    courses = [c.strip() for c in row['Courses'].split(',')]
                    group = row.get('Group', 'Unknown')

                    if len(courses) != len(grades):
                        continue

                    grade_count = len(grades)
                    point = sum(GRADE_POINTS.get(g, -1.00) for g in grades) / grade_count if grade_count > 0 else 0.00

                    students.append({
                        'Name': row['Name'],
                        'Exam Roll': row['Exam Roll'],
                        'Registration No': row['Registration No'],
                        'Result': row['Result'],
                        'Courses': courses,
                        'Grades': grades,
                        'Raw Grades': raw_grades,
                        'Point': round(point, 2),
                        'Group': group,
                        'Year': row.get('Year', '')
                    })
                except Exception as e:
                    print(f"Row {row_num}: Error processing record - {str(e)}")
        return students

    def rank_students(self, students):
        """Rank students with proper tie-breaking"""
        if not students:
            return []

        students.sort(key=lambda x: (
            -x['Point'],
            [GRADE_POINTS.get(g, -1.00) for g in x['Grades']]
        ))

        current_rank = 1
        for i, student in enumerate(students):
            if i > 0:
                prev = students[i-1]
                if not (student['Point'] == prev['Point'] and
                        student['Grades'] == prev['Grades']):
                    current_rank = i + 1
            student['Rank'] = current_rank

        return students

    def generate_pdf_report(self, students, group_name, year):
        """Generate PDF report for a specific group"""
        self.ensure_directory_exists(self.OUTPUT_DIR)
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # PDF Header
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "National University - Examination Results", 0, 1, 'C')
        pdf.cell(0, 10, f"Official Ranking List - {group_name} Group {year}", 0, 1, 'C')
        pdf.cell(0, 10, f"Total Students: {len(students)}", 0, 1, 'C')
        pdf.ln(10)

        # Student Results
        for student in students:
            pdf.set_font("Arial", '', 12)

            # Student Info (without course count)
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

            # Course Grades Table
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(40, 10, "Course Code", 1)
            pdf.cell(30, 10, "Grade", 1)
            pdf.ln()
            pdf.set_font("Arial", '', 12)

            for course, grade in zip(student['Courses'], student['Raw Grades']):
                pdf.cell(40, 10, course, 1)
                pdf.cell(30, 10, grade.upper(), 1)
                pdf.ln()

            pdf.ln(10)

        # Save PDF
        year_suffix = year[-2:] if year else "00"
        filename = f"{group_name.replace('.', '').replace(' ', '_')}_{year_suffix}.pdf"
        pdf.output(os.path.join(self.OUTPUT_DIR, filename))

    def ensure_directory_exists(self, directory):
        """Ensure directory exists"""
        os.makedirs(directory, exist_ok=True)
        return directory

    def normalize_grade(self, grade):
        """Convert grade to standard format"""
        grade = str(grade).strip().lower()
        if grade == 'fail':
            return 'f'
        elif grade == 'absent':
            return 'absent'
        return grade

if __name__ == "__main__":
    creator = RankingCreator()
    creator.generate_rankings()
