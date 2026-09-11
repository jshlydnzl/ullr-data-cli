# ⚡ Ullr: The Offline Data Auditor

> *An ultra-fast, 100% offline Data Quality and Dashboard Blueprint CLI.*

[![PyPI version](https://img.shields.io/pypi/v/ullr-data-cli.svg)](https://pypi.org/project/ullr-data-cli/)

**Ullr** is a pure Python Data Engine designed for Data Analysts and Engineers who need to audit massive Excel/CSV files instantly without relying on cloud APIs, ensuring 100% data privacy. 

---

## 🚀 Installation

Install globally via PyPI:
```bash
pip install ullr-data-cli
```

---

## 🛠️ Features

### 1. 🩺 Data Health Check (`ullr audit`)
Stop blindly trusting raw data. Ullr acts as an automated forensic auditor that scans your datasets for structural flaws before you build pipelines.
*   **Duplicate Detection:** Identifies exact copy-paste errors.
*   **Missing Value Scans:** Pinpoints exactly which columns have blank cells.
*   **Messy Text Detection:** Scans text columns for invisible leading/trailing spaces requiring `TRIM()`.
*   **Data Type Enforcement:** Catches numbers trapped as text (e.g., currency symbols or commas breaking math formulas).
*   **Ghost Data Warning:** Detects completely empty structural columns caused by floating side-tables in Excel.

### 2. 📊 Dashboard Blueprint Generator (`ullr analyze`)
Turn raw numbers into a full dashboard layout in seconds. Ullr calculates your key metrics and recommends an exact dashboard architecture based on your specific column data types.
*   **Automated Executive Summary:** Calculates row counts, total sums, and dominant category percentages in plain English.
*   **Dynamic Chart Logic:** Automatically recommends Line Charts for dates, Bar Charts for categories, and Donut Charts for binary metrics.
*   **Multi-Platform Mentor:** Generates step-by-step click instructions on how to build the recommended dashboard in **Microsoft Excel, Power BI, Google Looker Studio, and Tableau**.

### 3. 🧹 Auto-Clean Engine (`ullr clean`)
Automatically fixes the errors found during the audit phase. 
*   **Ghost Purge:** Instantly deletes 100% empty columns and "Unnamed" structural columns.
*   **Regex Stripping:** Acts as a Python `=TRIM()`, vaporizing invisible leading/trailing spaces.
*   **Math Fixer:** Hunts down numbers trapped as text (currencies `$`, `£`, commas), rips out the symbols, and converts them to pure math-ready floats.
*   **Multi-Format Export:** Pauses after cleaning to ask if you want to save the output as `.xlsx` (Dashboards), `.csv` (PostgreSQL bulk imports), or `.json` (Web Apps).

### 4. 🗃️ Markdown Data Dictionary & Job Simulator (`ullr map`)
Automatically parses your dataset to identify column data types, find Primary Keys, and generate a beautiful Markdown schema dictionary. 
*   **Virtual Manager Brief:** Reads your specific columns and generates a **Simulated Stakeholder Brief** giving you exact instructions on what KPIs to calculate and what layout to build.
*   **Auto-Documentation:** Saves the `.md` dictionary file directly next to your dataset so you never lose context.

### 5. 🏭 Practice Data Engine (`ullr generate`)
A built-in data synthesizer for building your portfolio.
*   **Synthetic Generation:** Uses the `Faker` library to instantly generate up to 10,000+ rows of realistic E-commerce, Healthcare, or Real Estate data.
*   **The Sabotage Engine:** Intentionally breaks the perfect data by injecting NULL values, invisible spaces, and numbers trapped as text, giving you the perfect dirty dataset to practice cleaning in Excel or SQL.
*   **Dynamic Stakeholder Brief:** Automatically analyzes the generated dataset and prints a System Requirements Document, giving you specific KPIs and Business Questions to answer for your project scope.

---

## 📖 Quick Start

Run the interactive engine from your terminal:
```bash
ullr
```

Or pass a file directly (Ullr will automatically scan your computer to find it if it's not in the current folder):
```bash
ullr audit my_raw_data.csv
ullr analyze cleaned_data.xlsx
```

---
