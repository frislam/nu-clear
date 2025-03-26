# NU-Clear
**Version 1.0**  
*A one-click solution for National University result scraping and ranking*

![NU-Clear Logo](https://images.app.goo.gl/uYmncL3jv77n52xw6) *(optional: add actual logo later)*

## Introduction
NU-Clear is an automated Python tool that:
- Scrapes NU exam results for given registration ranges
- Calculates GPAs following official grading standards
- Generates professional ranking reports
- Handles special cases (Absent/Fail/Not Registered)

**Current Support:**
- Bachelor Degree (Honours) 1st Year Results
- B.Sc Program (Psychology Department)
- 2023 Published Results

## Requirements

### System
- Linux (Tested on Debian 12)
- Chrome Browser 115.0.5790.114 or later
- Minimum 2GB RAM

### Dependencies
```bash
# Core packages
sudo apt install python3 python3-pip python3-venv git unzip

# Python libraries
pip install selenium==4.15.0 fpdf2==1.7.2 webdriver-manager==3.8.6
