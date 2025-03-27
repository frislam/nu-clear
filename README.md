# NU-Clear
*A one-click solution for National University result scraping and ranking*

![NU-Clear Logo](https://upload.wikimedia.org/wikipedia/en/thumb/5/58/National_University%2C_Bangladesh_crest.svg/800px-National_University%2C_Bangladesh_crest.svg.png)

## Introduction
NU-Clear is an automated Python tool that:
- Scrapes NU exam results for given registration ranges
- Calculates GPAs following official grading standards
- Generates professional ranking reports
- Handles special cases (Absent/Fail/Not Registered)

**Current Support:**
- For All Latest Examination
- For All Group ( B.A, B.S.S, B.Sc, B.B.A, B.Music, B.Sports )
- Latest Year Published Results

## Requirements

### System
- Linux (Tested on Debian 12)
- Windows
- Mac

## Dependencies
 ### Linux
```bash
# Core packages
$ sudo apt update && sudo apt upgrade -y
$ sudo apt install chromium-browser
$ sudo pip3 install selenium fpdf
$ sudo pip3 install webdriver_manager # Override the externally managed environment (not recommended): You can use the '--break-system-packages' flag to override the restriction, but this is not recommended as it may break your Python installation or OS.
```
### Windows

1. **Install Python**:
   - Download and install Python from the [official website](https://www.python.org/downloads/).

2. **Install Google Chrome**:
   - Download and install Google Chrome from the [official website](https://www.google.com/chrome/).

3. **Install Required Packages**:
   - Open Command Prompt and run:
     ```sh
     pip install selenium webdriver_manager fpdf
     ```
### Mac

1. **Install Python**:
   - Download and install Python from the [official website](https://www.python.org/downloads/). Alternatively, you can use Homebrew:
     ```sh
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     brew install python
     ```
2. **Install Google Chrome**:
   - Download and install Google Chrome from the [official website](https://www.google.com/chrome/).

3. **Install Required Packages**:
   - Open Terminal and run:
     ```sh
     pip3 install selenium webdriver_manager fpdf
     ```
## Setup

 ### 1. Clone Repository
```
git clone https://frislam/nu-clear.git
cd nu-clear
```
## Usage

 ### Main Workflow
```
$ sudo python3 students.py # linux
$ python students.py # windows
$ python3 students.py # mac
```
- Follow prompts to enter registration range

## File Management
- **Backup your CSV & PDF files**- The system overwrites `nu_results.csv` & `*.pdf` on each run
- Note the PDF only overwrites for same data. Example: No overwrites if `BSc_25.pdf = BA_24.pdf` & Overwrites if `BSc_24.pdf = BSc_24.pdf`

## Version History
- 2.0 (current):
  - Initial release
  - Supports All Examination
  - All Group
  - All Departments
  - Handle Absent/Fail cases
  - Cross-Platform Support
  - Added Year in PDF header

## Disclaimer
This tool is for educational purposes only. Always verify official results from NU website.

---
***Developed by Sultan FR - KAUC***
