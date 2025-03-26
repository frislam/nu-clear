# NU-Clear
**Version 1.0**  
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
- Chrome Browser 115 or later

### Dependencies
```bash
# Core packages
sudo apt update
sudo apt install python3 python3-pip python3-venv git unzip

# Python libraries
sudo apt install python3-pandas
pip3 install selenium
sudo apt install python3-fpdf python3-markdown
pip3 install webdriver-manager
```
## Setup

 ### 1. Clone Repository
```
git clone https://frislam/nu-clear.git
cd nu-clear
```
 ### 2. ChromeDriver Setup
```
# Check Chrome version first
google-chrome --version  # Should show 134.0.6998.165 or higher

# Download matching driver (example for v115)
wget https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.165/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip -d chromedriver-linux64
rm chromedriver-linux64.zip
```
## Usage

 ### Main Workflow
```
sudo python3 students.py
```
- Follow prompts to enter registration range

## File Management
- **Backup your CSV files**- The system overwrites `nu_results.csv` on each run
- Recommended backup command:
  ```
  cp ./results/nu_results.csv ./results/backup_$(date +%Y-%m-%d).csv
  ```

## Troubleshooting
  
  ### Common Issues
  - **ChromeDriver Mismatch**

## Version History
- 1.2 (current):
  - Initial release
  - Supports All Examination
  - All Group
  - All Departments
  - Handle Absent/Fail cases

## Disclaimer
This tool is for educational purposes only. Always verify official results from NU website.

---
***Developed by Sultan FR - KAUC***
