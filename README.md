# ⚡ Ullr: The Offline Data Auditor

> *An ultra-fast, 100% offline Data Quality and Dashboard Blueprint CLI.*

[![PyPI version](https://img.shields.io/pypi/v/ullr-data-cli.svg)](https://pypi.org/project/ullr-data-cli/)

**Ullr** is a pure Python Data Engine designed for Data Analysts and Engineers who need to audit massive Excel/CSV files instantly without relying on cloud APIs, ensuring 100% data privacy. 

This project was intentionally **Vibe Coded** (AI-assisted engineered) to demonstrate modern, high-velocity software development using Large Language Models alongside core Data Engineering principles.

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
