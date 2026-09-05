# CodeAlpha Task 2 — Exploratory Data Analysis
### Online Retail Dataset (UCI Machine Learning Repository)

**Author:** Ali Rashid (Chaudhary) — BSCS, University of Engineering and Technology (UET) Taxila
**Internship:** CodeAlpha Data Analytics Internship
**Task:** Task 2 — Exploratory Data Analysis (EDA)

---
## Demo Link: https://drive.google.com/file/d/1bDmRvn4fFLo0EgcEP3CH6OLoEbUXTsIm/view?usp=sharing

## Overview

This project is a complete, evidence-based exploratory data analysis of the
**Online Retail Dataset** — 541,909 real transaction records from a
UK-based online gift retailer (Dec 2010 – Dec 2011). It fulfills every
requirement of the CodeAlpha Task 2 brief: meaningful questions, structural
exploration, trend/pattern/anomaly detection, hypothesis-driven statistical
testing, and explicit data-quality assessment — all grounded in numbers
computed directly from the real dataset (no fabricated statistics).

## CodeAlpha Internship Context

This repository was built as the deliverable for **Task 2** of the
CodeAlpha Data Analytics Internship, which requires selecting a real-world
dataset, asking meaningful analytical questions, exploring its structure,
identifying trends/patterns/anomalies, validating assumptions with
statistics and visualization, and surfacing data-quality issues for
further analysis.

## Objectives

- Select a portfolio-worthy, real-world dataset with genuine data-quality issues.
- Formulate 12 meaningful, dataset-specific analytical questions.
- Explore structure, types, and quality of every column.
- Clean the data with fully justified, non-destructive methods.
- Perform univariate, bivariate, multivariate, correlation, trend, and anomaly analysis.
- Validate findings using appropriate statistical hypothesis tests.
- Visualize every insight with clear, labeled, professional charts.
- Summarize findings into actionable, evidence-based recommendations.

## Dataset Source

- **Name:** Online Retail Dataset
- **Source:** [UCI Machine Learning Repository, ID 352](https://archive.ics.uci.edu/dataset/352/online+retail) (donor: Dr. Daqing Chen, London South Bank University)
- **Size:** 541,909 rows × 8 columns (raw)
- **Period:** 1 December 2010 – 9 December 2011
- **License:** CC BY 4.0
- **Citation:** Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33

## Technologies Used

- Python 3.12
- pandas, numpy — data manipulation
- matplotlib, seaborn — visualization
- scipy.stats — hypothesis testing (t-test, ANOVA, chi-square, Pearson correlation, confidence intervals)
- Jupyter Notebook — analysis narrative and reproducible workflow
- openpyxl — Excel file I/O

## Analytical Questions

1. What is the overall distribution of order quantities and unit prices, and what does the skew imply about typical vs. bulk/wholesale transactions?
2. Which countries generate the most revenue, and how concentrated is that revenue?
3. Is there a seasonal/monthly trend in sales, particularly around the winter holiday season?
4. Which products are most frequently purchased vs. which generate the most revenue — are they the same products?
5. Do UK and non-UK transactions differ significantly in average line-item revenue?
6. Does average invoice revenue differ significantly across quarters of the year?
7. Is cancellation status associated with the customer's country?
8. How correlated are Quantity and UnitPrice with each other and with total revenue?
9. What proportion of transactions are cancellations, and does the cancellation rate change over time?
10. Are there anomalous transactions (extreme quantity/price outliers) that deserve investigation?
11. What does customer purchase behavior look like through an RFM (Recency, Frequency, Monetary) lens?
12. What data-quality issues exist in the raw data, and how significant are they?

## Methodology

1. **Data Exploration** — dimensions, dtypes, unique values, numerical/categorical summaries, missing-value and duplicate analysis, business-rule quality checks.
2. **Data Cleaning** — every decision documented (problem → why it matters → method → why appropriate); no data deleted without justification.
3. **Exploratory Analysis** — univariate, bivariate, multivariate, correlation, trend, and anomaly analysis, each paired with a chart and a written finding.
4. **Statistical Testing** — t-test, one-way ANOVA, chi-square test of independence, Pearson correlation significance, and a 95% confidence interval — each with a stated hypothesis, justification, result, and plain-language interpretation.
5. **Insight Synthesis** — key findings, trends, patterns, anomalies, and data-quality issues consolidated into business-relevant recommendations.

## Data-Cleaning Process (Summary)

| Issue | Extent | Action Taken |
|---|---|---|
| Missing `CustomerID` | 24.93% of rows | Kept for revenue/time/product analysis; excluded only from customer-level RFM analysis |
| Missing `Description` | 0.27% of rows | Filled with `"UNKNOWN ITEM"` |
| Exact duplicate rows | 0.97% of rows | Dropped (logging/export artifact) |
| Cancellation invoices | 1.71% of rows | Flagged (`IsCancelled`), retained, analyzed separately |
| Negative quantity w/o cancellation flag | 1,336 rows | Flagged as invalid sale; retained with flag for transparency |
| Zero/negative `UnitPrice` | 2,517 rows | Excluded from revenue analysis (non-product administrative entries) |

Full detail and code are in `notebooks/EDA_Analysis.ipynb` (Section 5) and `reports/EDA_Report.md`.

## Key Findings

1. Quantity and UnitPrice are both strongly right-skewed — most transactions are small, low-value purchases with a long tail of bulk/wholesale orders.
2. The UK accounts for **84.59%** of total revenue — heavy geographic concentration.
3. **November 2011** is the clear seasonal peak (£1,503,866.78 in revenue), consistent with pre-Christmas gift buying.
4. There is **no Saturday trading** anywhere in the dataset — a genuine operational pattern.
5. The top-revenue product list differs from the top-quantity list; "DOTCOM POSTAGE" (a shipping charge, not a product) ranks among the highest-revenue line items.
6. Quantity and UnitPrice are essentially uncorrelated (Pearson r = -0.0038).
7. Non-UK transactions have significantly higher average line-item revenue than UK transactions (t = -30.46, p < 0.001).
8. Invoice revenue differs significantly by quarter (ANOVA F = 2.95, p = 0.019), peaking in Q4.
9. Cancellation status is significantly associated with country (χ² = 795.12, p < 0.001).
10. Customer value is highly unequal — median customer spend is £668.57 across 2 orders, vs. a maximum of £280,206.02 across 209 orders.

Full findings, all 12 answered questions, and every supporting statistic are in `reports/EDA_Report.md` and the executed notebook.

## Insights

Revenue is concentrated in a single country and a small set of high-value customers, sales are strongly seasonal around the winter holidays, and a portion of "revenue" is actually non-merchandise administrative charges — each of these has direct implications for how this retailer should plan inventory, marketing spend, and customer retention.

## Recommendations

- Diversify revenue geography beyond the UK to reduce single-market dependency.
- Plan inventory/staffing around the September–November demand ramp-up.
- Exclude non-product charges (postage, adjustments) from merchandise performance reporting.
- Investigate country-specific cancellation drivers (e.g., Germany's disproportionate cancellation share).
- Build a retention program targeting the high-Monetary, high-Frequency customer segment identified via RFM.

## Project Structure

```
codealpha-task-2-eda/
│
├── data/
│   ├── raw/                       # Original, unmodified dataset (OnlineRetail.xlsx)
│   └── processed/                 # Cleaned dataset output (online_retail_cleaned.csv)
│
├── notebooks/
│   └── EDA_Analysis.ipynb         # Full, executed, narrated EDA notebook
│
├── src/
│   └── analysis.py                # Reusable, scriptable EDA pipeline (mirrors the notebook)
│
├── visualizations/                # 14 exported PNG charts referenced throughout the analysis
│
├── reports/
│   ├── EDA_Report.md              # Standalone written report of all findings
│   └── findings.json              # Machine-readable export of every computed statistic
│
├── README.md
├── requirements.txt
└── .gitignore
```

## Installation

```bash
git clone <your-repo-url>
cd codealpha-task-2-eda
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> **Note on the data file:** `data/raw/OnlineRetail.xlsx` is excluded from
> version control via `.gitignore` due to its size (~23.7 MB). Download it
> from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/352/online+retail)
> and place it at `data/raw/OnlineRetail.xlsx` before running the analysis.

## How to Run

**Option 1 — Jupyter Notebook (recommended, includes narrative):**
```bash
jupyter notebook notebooks/EDA_Analysis.ipynb
```

**Option 2 — Script (regenerates all visualizations, the cleaned CSV, and `findings.json`):**
```bash
python src/analysis.py
```

Both reproduce the identical analysis — the notebook adds markdown narrative and inline chart display; the script is designed for automation/CI use.

## Results

- 14 professional, labeled visualizations in `visualizations/`.
- A fully executed, 79-cell notebook with zero execution errors.
- 5 statistical hypothesis tests, each interpreted in plain language.
- A cleaned dataset (`data/processed/online_retail_cleaned.csv`) with explicit quality flags (`IsCancelled`, `HasCustomerID`, `IsValidSale`) rather than silently dropped rows.
- A standalone written report (`reports/EDA_Report.md`) and machine-readable findings export (`reports/findings.json`).

## Future Improvements

- Extend RFM segmentation into explicit customer tiers (e.g., k-means clustering) for a marketing-ready segmentation deliverable.
- Incorporate the newer "Online Retail II" dataset (extending into 2011) for a longer seasonal baseline.
- Build an interactive dashboard (e.g., Plotly Dash or Streamlit) on top of `data/processed/online_retail_cleaned.csv`.
- Add product-category tagging (via `StockCode`/`Description` parsing) to enable category-level trend analysis.

---

## CodeAlpha Task 2 Requirement Mapping

| Requirement | Where It's Satisfied |
|---|---|
| ✓ Meaningful questions | 12 dataset-specific questions in "Analytical Questions" above and notebook Section 0 |
| ✓ Data structure exploration | Notebook Section 3 (dimensions, columns, head/tail, unique values) |
| ✓ Variable/data-type analysis | Notebook Section 3.1 (`df.dtypes`, correction of `InvoiceNo`/`StockCode`/`CustomerID`/`Country` types in Section 5) |
| ✓ Trend identification | Notebook Section 10 — monthly revenue, day-of-week, hour-of-day trends |
| ✓ Pattern identification | Notebook Sections 6–8 — univariate, bivariate, multivariate analysis |
| ✓ Anomaly detection | Notebook Section 11 — IQR-based outlier detection on Quantity/UnitPrice, cancellation-rate anomalies |
| ✓ Hypothesis testing | Notebook Section 13 — t-test, ANOVA, chi-square, correlation significance, confidence interval |
| ✓ Assumption validation | Each statistical test in Section 13 states H0, justifies the test choice, and interprets the result |
| ✓ Data-quality issue detection | Notebook Section 4 (missing values, duplicates, business-rule checks) and Section 16 of `reports/EDA_Report.md` |

## CodeAlpha Task 2 Submission Checklist

- ✓ EDA completed (structure, cleaning, univariate/bivariate/multivariate/correlation/trend/anomaly analysis)
- ✓ Notebook completed (`notebooks/EDA_Analysis.ipynb`, executed end-to-end with zero errors)
- ✓ Source code completed (`src/analysis.py`, reusable pipeline mirroring the notebook)
- ✓ README completed (this file)
- ✓ Visualizations included (14 PNG charts in `visualizations/`)
- ✓ Report completed (`reports/EDA_Report.md`)
- ✓ GitHub-ready (clean folder structure, `.gitignore`, `requirements.txt`)
- ✓ Tested successfully (notebook executed in-place with `jupyter nbconvert --execute`, zero cell errors)
- ✓ Ready for internship submission
