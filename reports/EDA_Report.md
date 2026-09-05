# EDA Report — Online Retail Dataset
**CodeAlpha Data Analytics Internship — Task 2: Exploratory Data Analysis**
**Author:** Ali Rashid (Chaudhary)

---

## 1. Dataset

| Field | Detail |
|---|---|
| Name | Online Retail Dataset |
| Source | UCI Machine Learning Repository (`archive.ics.uci.edu/dataset/352/online+retail`), donated by Dr. Daqing Chen, London South Bank University |
| Period | 01 Dec 2010 – 09 Dec 2011 |
| Raw size | 541,909 rows × 8 columns |
| License | CC BY 4.0 |
| Description | Transactions of a UK-based, non-store online retailer selling all-occasion gifts; a large share of customers are wholesalers |

## 2. Structure & Data Types

- 8 raw columns: `InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, `Country`.
- 38 unique countries, ~4,070 unique product codes, ~4,372 unique customers.
- `Quantity` and `UnitPrice` are numeric and heavily right-skewed; `InvoiceDate` spans just over a year.

## 3. Data Quality Findings

| Issue | Extent | Resolution |
|---|---|---|
| Missing `CustomerID` | 135,080 rows (24.93%) | Retained for revenue/product/time analysis; excluded only from customer-level RFM analysis |
| Missing `Description` | 1,454 rows (0.27%) | Filled with `"UNKNOWN ITEM"` |
| Exact duplicate rows | 5,268 rows (0.97%) | Dropped (logging/export artifact) |
| Cancellation invoices (`InvoiceNo` starts with "C") | 9,288 invoices (1.71% of rows) | Flagged with `IsCancelled`, retained and analyzed separately |
| Negative quantity without a cancellation flag | 1,336 rows | Flagged as not a valid sale; retained in full data, excluded from revenue metrics |
| Zero/negative `UnitPrice` | 2,517 rows | Excluded from the "valid sale" revenue view (non-product administrative entries) |

No rows were deleted without justification. The only unconditional removal was of exact duplicate rows, which carry no additional information.

## 4. Key Statistics (post-cleaning, valid sales only, n = 524,878 line items)

- **Quantity:** median 4, mean 10.62, max 80,995 (skew far above 1 — right-skewed).
- **UnitPrice:** median £2.08, mean £3.92, max £13,541.33 (also strongly right-skewed).
- **Total UK revenue share:** 84.59% of total revenue.
- **Peak revenue month:** November 2011 (£1,503,866.78).
- **No Saturday trading** recorded anywhere in the dataset.

## 5. Statistical Test Results

| Test | Hypothesis | Result | p-value | Conclusion |
|---|---|---|---|---|
| Independent t-test | Mean line-item revenue equal for UK vs non-UK | t = -30.46 | 3.30 × 10⁻²⁰³ | Reject H0 — non-UK revenue per line (£36.54) significantly exceeds UK (£18.75) |
| One-way ANOVA | Mean invoice revenue equal across quarters | F = 2.95 | 0.0191 | Reject H0 — invoice revenue differs significantly by quarter (Q4 highest at £585.10 avg) |
| Chi-square | Cancellation independent of country (top 6) | χ² = 795.12, df = 5 | 1.31 × 10⁻¹⁶⁹ | Reject H0 — cancellation rate is significantly associated with country |
| Pearson correlation | No linear relationship between Quantity and UnitPrice | r = -0.0038 | 0.0061 | Statistically significant but practically negligible — essentially no linear relationship |
| 95% CI (mean invoice value) | — | Mean = £533.17 | CI: (£508.47, £557.87) | Based on n = 19,960 invoices |

## 6. Anomaly Detection

Using a conservative 3×IQR rule:
- **Quantity outliers:** 19,323 rows (3.68% of valid sales); threshold > 41 units; max observed 80,995 units — consistent with genuine wholesale bulk orders given this retailer's wholesaler customer base.
- **UnitPrice outliers:** 12,187 rows (2.32% of valid sales); threshold > £12.77; max observed £13,541.33 — largely non-product administrative charges (e.g. postage, manual adjustments) rather than product mispricing.

## 7. Trend & Seasonality

Monthly revenue rises steadily from August 2011, peaking sharply in November 2011 ahead of the Christmas gifting season, then appears to fall in December — an artifact of the dataset ending December 9, 2011, not a genuine decline. Cancellation rate fluctuates month to month without a runaway upward trend.

## 8. Customer Segmentation (RFM)

4,338 customers with a valid `CustomerID` were analyzed:
- **Recency:** median 51 days since last purchase (mean 92.5, highly variable).
- **Frequency:** median 2 distinct invoices (mean 4.27, max 209).
- **Monetary:** median £668.57 spent (mean £2,048.69, max £280,206.02).

Spend is highly unequal — a small set of high-frequency, high-monetary customers (likely wholesale accounts) accounts for a disproportionate share of total revenue.

## 9. Insights & Recommendations

- **Geographic concentration risk:** ~85% of revenue comes from the UK; diversifying into the next-largest markets (Netherlands, EIRE, Germany, France) would reduce single-market dependency.
- **Seasonal planning:** inventory, staffing, and marketing spend should be weighted toward the September–November ramp-up; the December dip in this dataset should not be read as a real seasonal decline.
- **Product reporting hygiene:** exclude non-product charges (postage, adjustments) from "top product" revenue reporting to avoid overstating merchandise performance.
- **Country-specific cancellation follow-up:** Germany's cancellation share is disproportionate to its transaction volume relative to peers — worth investigating shipping, fit, or checkout friction.
- **Retention focus on high-value customers:** the RFM segmentation identifies a small, highly valuable customer group meriting a dedicated loyalty or account-management approach.

## 10. Limitations

- The dataset covers a single company over roughly one year — findings (e.g., seasonality, country patterns) may not generalize to other retailers or years.
- ~25% of transactions cannot be tied to an individual customer, limiting the completeness of the RFM segmentation to the remaining ~75%.
- `StockCode`/`Description` inconsistencies (e.g., non-product codes like postage) required manual judgment to separate from genuine merchandise, which is a source of interpretive (not statistical) uncertainty.

All figures in this report were computed directly from the dataset via `src/analysis.py` / `notebooks/EDA_Analysis.ipynb` — none are estimated or fabricated.
