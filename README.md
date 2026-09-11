# Ullr Data Engine

![Ullr Interactive Menu](https://raw.githubusercontent.com/jshlydnzl/ullr-data-cli/master/screenshot.png)

A purely native Practice Engine for aspiring Data Analysts to generate and audit datasets.

Ullr is not an automated BI tool that does your job for you. It generates intentionally dirty data, gives you realistic business context, and audits your raw files so you can practice cleaning and analyzing data natively in Excel or SQL.

## Installation

```bash
pip install ullr-data-cli
```

## How to Practice Data Analytics with Ullr

Ullr is built with a beautiful interactive terminal menu. Just type `ullr` in your terminal to launch the engine and follow these three steps:

### Step 1: Generate the Dirty Data
Launch the interactive menu and select **Generate Data** (Option 2). 
Ullr will ask you to choose from 7 different industries (e.g., E-Commerce, Healthcare, SaaS). It will generate hundreds of rows of intentionally flawed data, and automatically output a **Stakeholder Brief** containing a realistic business scenario and the exact KPIs you need to build.

### Step 2: Audit the Damage
Now that you have your dataset, launch the menu again and select **Audit Data** (Option 1).
Ullr will auto-detect the datasets in your folder. Select your file, and Ullr will scan it to give you a full forensic report on missing values, hidden blanks, duplicates, and data type errors.

### Step 3: Clean and Analyze (Your Job!)
Now, open the dataset in Excel or SQL. Using Ullr's Stakeholder Brief and Audit Report as your guide, clean the data yourself and build out the requested dashboards. No AI crutches—just pure engineering practice.
