"""
CodeAlpha Task 2 - Exploratory Data Analysis
Online Retail Dataset (UCI Machine Learning Repository)

This module contains the full, reusable EDA pipeline: loading, structural
exploration, data-quality assessment, cleaning, univariate / bivariate /
multivariate analysis, correlation analysis, trend analysis, anomaly
detection, and statistical hypothesis testing.

All numbers referenced in the notebook, report, and README are produced
by running this script (or the equivalent notebook cells) against the
real dataset - nothing is fabricated.

Author: Ali Rashid (Chaudhary)
"""

import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 110
plt.rcParams["font.size"] = 11

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "OnlineRetail.xlsx"
PROCESSED_PATH = ROOT / "data" / "processed" / "online_retail_cleaned.csv"
VIZ_DIR = ROOT / "visualizations"
FINDINGS_PATH = ROOT / "reports" / "findings.json"

VIZ_DIR.mkdir(parents=True, exist_ok=True)
(ROOT / "reports").mkdir(parents=True, exist_ok=True)
(ROOT / "data" / "processed").mkdir(parents=True, exist_ok=True)

findings = {}


def savefig(name):
    path = VIZ_DIR / name
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved {path.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# PHASE 3: DATA EXPLORATION
# ---------------------------------------------------------------------------

def load_data():
    df = pd.read_excel(RAW_PATH)
    return df


def explore_structure(df):
    section = {}
    section["shape"] = df.shape
    section["columns"] = list(df.columns)
    section["dtypes"] = {c: str(t) for c, t in df.dtypes.items()}
    section["unique_counts"] = {c: int(df[c].nunique()) for c in df.columns}
    section["n_countries"] = int(df["Country"].nunique())
    section["date_min"] = str(df["InvoiceDate"].min())
    section["date_max"] = str(df["InvoiceDate"].max())
    findings["structure"] = section

    print("Shape:", df.shape)
    print("\nDtypes:\n", df.dtypes)
    print("\nUnique values per column:\n", df.nunique())
    print("\nDate range:", section["date_min"], "to", section["date_max"])
    return section


def missing_value_analysis(df):
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    summary = pd.DataFrame({"missing_count": missing, "missing_pct": missing_pct})
    summary = summary[summary["missing_count"] > 0].sort_values("missing_count", ascending=False)
    findings["missing_values"] = summary.reset_index().rename(columns={"index": "column"}).to_dict(orient="records")
    print("\nMissing values:\n", summary)
    return summary


def duplicate_analysis(df):
    n_dupes = int(df.duplicated().sum())
    pct = round(n_dupes / len(df) * 100, 2)
    findings["duplicates"] = {"count": n_dupes, "pct": pct}
    print(f"\nExact duplicate rows: {n_dupes} ({pct}% of dataset)")
    return n_dupes


def data_quality_checks(df):
    n_cancellations = int(df["InvoiceNo"].astype(str).str.startswith("C").sum())
    n_neg_qty = int((df["Quantity"] < 0).sum())
    n_zero_neg_price = int((df["UnitPrice"] <= 0).sum())
    non_cancel_neg_qty = int(((df["Quantity"] < 0) & (~df["InvoiceNo"].astype(str).str.startswith("C"))).sum())

    checks = {
        "cancellation_invoices": n_cancellations,
        "cancellation_pct": round(n_cancellations / len(df) * 100, 2),
        "negative_quantity_rows": n_neg_qty,
        "zero_or_negative_price_rows": n_zero_neg_price,
        "negative_qty_non_cancellation_rows": non_cancel_neg_qty,
    }
    findings["data_quality_checks"] = checks
    print("\nData quality checks:", json.dumps(checks, indent=2))
    return checks


# ---------------------------------------------------------------------------
# PHASE 4: DATA CLEANING
# ---------------------------------------------------------------------------

def clean_data(df):
    df = df.copy()
    before = len(df)

    # 1. Flag cancellations before removing/altering anything (preserve information)
    df["IsCancelled"] = df["InvoiceNo"].astype(str).str.startswith("C")

    # 2. Remove exact duplicate rows (data entry / export duplication, not real repeat purchases)
    dupes_removed = int(df.duplicated().sum())
    df = df.drop_duplicates()

    # 3. Missing Description: small fraction (~0.27%), and these rows are almost always
    #    UnitPrice == 0 administrative/adjustment entries rather than genuine sales.
    #    We keep them but label them, since deleting them would silently discard
    #    legitimate transactional rows for products with a known StockCode.
    df["Description"] = df["Description"].fillna("UNKNOWN ITEM")

    # 4. Missing CustomerID (~25% of rows): these are valid sales transactions
    #    (guest/unregistered checkouts) but cannot be attributed to a specific
    #    customer. Deleting them would discard ~25% of genuine revenue data,
    #    so we KEEP them for product/country/time analysis, and only EXCLUDE
    #    them from customer-level analyses (RFM, per-customer segmentation),
    #    which requires a valid CustomerID by definition.
    df["HasCustomerID"] = df["CustomerID"].notnull()

    # 5. Zero or negative UnitPrice on non-cancelled rows: these are not real
    #    sales (bank charges, samples, manual adjustments, damages) - they would
    #    distort revenue and correlation analysis, so they are excluded from the
    #    "clean sales" view used for revenue/statistical analysis, but retained
    #    in the full cleaned file with a flag for transparency.
    df["IsValidSale"] = (df["UnitPrice"] > 0) & (df["Quantity"] > 0) & (~df["IsCancelled"])

    # 6. Correct dtypes
    df["InvoiceNo"] = df["InvoiceNo"].astype(str)
    df["StockCode"] = df["StockCode"].astype(str)
    df["CustomerID"] = df["CustomerID"].astype("Int64")
    df["Country"] = df["Country"].astype(str).str.strip()

    # 7. Derived fields used throughout the analysis
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["InvoiceMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    df["InvoiceDateOnly"] = df["InvoiceDate"].dt.date
    df["InvoiceHour"] = df["InvoiceDate"].dt.hour
    df["InvoiceDOW"] = df["InvoiceDate"].dt.day_name()
    df["Quarter"] = df["InvoiceDate"].dt.to_period("Q").astype(str)

    after = len(df)
    cleaning_summary = {
        "rows_before": before,
        "rows_after_dedup": after,
        "duplicate_rows_removed": dupes_removed,
        "rows_flagged_cancelled": int(df["IsCancelled"].sum()),
        "rows_missing_customer_id": int((~df["HasCustomerID"]).sum()),
        "rows_valid_sales": int(df["IsValidSale"].sum()),
    }
    findings["cleaning_summary"] = cleaning_summary
    print("\nCleaning summary:", json.dumps(cleaning_summary, indent=2))
    return df


# ---------------------------------------------------------------------------
# PHASE 5: EXPLORATORY ANALYSIS
# ---------------------------------------------------------------------------

def univariate_analysis(df):
    sales = df[df["IsValidSale"]]

    desc_qty = sales["Quantity"].describe()
    desc_price = sales["UnitPrice"].describe()
    desc_rev = sales["Revenue"].describe()

    findings["univariate"] = {
        "quantity_describe": desc_qty.to_dict(),
        "unitprice_describe": desc_price.to_dict(),
        "revenue_describe": desc_rev.to_dict(),
        "quantity_skew": float(sales["Quantity"].skew()),
        "unitprice_skew": float(sales["UnitPrice"].skew()),
    }
    print("\nQuantity describe:\n", desc_qty)
    print("\nUnitPrice describe:\n", desc_price)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    sns.histplot(sales["Quantity"].clip(upper=sales["Quantity"].quantile(0.99)), bins=50, ax=axes[0], color="#4C72B0")
    axes[0].set_title("Distribution of Quantity per Line Item (capped at 99th pct)")
    axes[0].set_xlabel("Quantity")

    sns.histplot(sales["UnitPrice"].clip(upper=sales["UnitPrice"].quantile(0.99)), bins=50, ax=axes[1], color="#DD8452")
    axes[1].set_title("Distribution of Unit Price (capped at 99th pct)")
    axes[1].set_xlabel("Unit Price (£)")
    savefig("01_univariate_quantity_price_distributions.png")

    # Country distribution (categorical)
    top_countries = sales["Country"].value_counts().head(10)
    findings["top_countries_by_transactions"] = top_countries.to_dict()
    plt.figure(figsize=(9, 5))
    sns.barplot(x=top_countries.values, y=top_countries.index, hue=top_countries.index, palette="viridis", legend=False)
    plt.title("Top 10 Countries by Number of Transactions")
    plt.xlabel("Number of Transaction Lines")
    plt.ylabel("Country")
    savefig("02_top_countries_by_transactions.png")

    return desc_qty, desc_price, desc_rev


def bivariate_analysis(df):
    sales = df[df["IsValidSale"]]

    # Revenue by country (top 10)
    rev_by_country = sales.groupby("Country")["Revenue"].sum().sort_values(ascending=False).head(10)
    findings["revenue_by_country_top10"] = rev_by_country.round(2).to_dict()

    plt.figure(figsize=(9, 5))
    sns.barplot(x=rev_by_country.values, y=rev_by_country.index, hue=rev_by_country.index, palette="mako", legend=False)
    plt.title("Top 10 Countries by Total Revenue (£)")
    plt.xlabel("Total Revenue (£)")
    plt.ylabel("Country")
    plt.gca().xaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    savefig("03_revenue_by_country.png")

    uk_share = float(rev_by_country.loc["United Kingdom"] / sales["Revenue"].sum() * 100) if "United Kingdom" in rev_by_country.index else None
    findings["uk_revenue_share_pct"] = round(uk_share, 2) if uk_share else None

    # Top products by revenue vs by quantity
    top_products_rev = sales.groupby("Description")["Revenue"].sum().sort_values(ascending=False).head(10)
    top_products_qty = sales.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head(10)
    findings["top_products_by_revenue"] = top_products_rev.round(2).to_dict()
    findings["top_products_by_quantity"] = top_products_qty.to_dict()
    overlap = len(set(top_products_rev.index) & set(top_products_qty.index))
    findings["top10_product_overlap_rev_qty"] = overlap

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    sns.barplot(x=top_products_rev.values, y=[t[:28] for t in top_products_rev.index], ax=axes[0], hue=top_products_rev.index, palette="crest", legend=False)
    axes[0].set_title("Top 10 Products by Revenue")
    axes[0].set_xlabel("Revenue (£)")
    sns.barplot(x=top_products_qty.values, y=[t[:28] for t in top_products_qty.index], ax=axes[1], hue=top_products_qty.index, palette="flare", legend=False)
    axes[1].set_title("Top 10 Products by Quantity Sold")
    axes[1].set_xlabel("Units Sold")
    savefig("04_top_products_revenue_vs_quantity.png")

    # Quantity vs UnitPrice scatter (sampled for readability)
    sample = sales.sample(min(20000, len(sales)), random_state=42)
    plt.figure(figsize=(7, 5.5))
    plt.scatter(sample["UnitPrice"].clip(upper=sample["UnitPrice"].quantile(0.99)),
                sample["Quantity"].clip(upper=sample["Quantity"].quantile(0.99)),
                alpha=0.15, s=10, color="#4C72B0")
    plt.title("Quantity vs Unit Price (sampled, 99th-pct capped)")
    plt.xlabel("Unit Price (£)")
    plt.ylabel("Quantity")
    savefig("05_quantity_vs_price_scatter.png")

    return rev_by_country, top_products_rev


def trend_analysis(df):
    sales = df[df["IsValidSale"]]
    monthly = sales.groupby("InvoiceMonth")["Revenue"].sum().sort_index()
    findings["monthly_revenue"] = monthly.round(2).to_dict()

    plt.figure(figsize=(11, 5))
    monthly.plot(kind="line", marker="o", color="#C44E52")
    plt.title("Monthly Revenue Trend (Dec 2010 - Dec 2011)")
    plt.xlabel("Month")
    plt.ylabel("Revenue (£)")
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    savefig("06_monthly_revenue_trend.png")

    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    by_dow = sales.groupby("InvoiceDOW")["Revenue"].sum().reindex([d for d in dow_order if d in sales["InvoiceDOW"].unique()])
    findings["revenue_by_day_of_week"] = by_dow.round(2).to_dict()

    plt.figure(figsize=(8, 5))
    sns.barplot(x=by_dow.index, y=by_dow.values, hue=by_dow.index, palette="rocket", legend=False)
    plt.title("Total Revenue by Day of Week")
    plt.ylabel("Revenue (£)")
    plt.xticks(rotation=30)
    plt.gca().yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    savefig("07_revenue_by_day_of_week.png")

    by_hour = sales.groupby("InvoiceHour")["Revenue"].sum()
    findings["revenue_by_hour"] = by_hour.round(2).to_dict()
    plt.figure(figsize=(9, 5))
    sns.barplot(x=by_hour.index, y=by_hour.values, hue=by_hour.index, palette="flare", legend=False)
    plt.title("Total Revenue by Hour of Day")
    plt.xlabel("Hour (24h)")
    plt.ylabel("Revenue (£)")
    savefig("08_revenue_by_hour.png")

    # peak month
    peak_month = monthly.idxmax()
    findings["peak_revenue_month"] = peak_month
    findings["peak_revenue_month_value"] = round(float(monthly.max()), 2)
    return monthly


def correlation_analysis(df):
    sales = df[df["IsValidSale"]]
    corr_cols = ["Quantity", "UnitPrice", "Revenue"]
    corr = sales[corr_cols].corr(method="pearson")
    findings["correlation_matrix"] = corr.round(3).to_dict()

    plt.figure(figsize=(5.5, 4.5))
    sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".2f")
    plt.title("Correlation Heatmap (Quantity, UnitPrice, Revenue)")
    savefig("09_correlation_heatmap.png")

    r_qp, p_qp = stats.pearsonr(sales["Quantity"], sales["UnitPrice"])
    findings["quantity_price_pearson"] = {"r": round(float(r_qp), 4), "p_value": float(p_qp)}
    print(f"\nPearson r (Quantity vs UnitPrice): {r_qp:.4f}, p = {p_qp:.4g}")
    return corr


def multivariate_analysis(df):
    sales = df[df["IsValidSale"]]
    # Country x Month revenue heatmap for top 8 countries
    top8 = sales.groupby("Country")["Revenue"].sum().sort_values(ascending=False).head(8).index
    pivot = sales[sales["Country"].isin(top8)].pivot_table(
        index="Country", columns="InvoiceMonth", values="Revenue", aggfunc="sum", fill_value=0
    )
    pivot = pivot.loc[top8]

    plt.figure(figsize=(13, 5.5))
    sns.heatmap(pivot, cmap="YlGnBu", cbar_kws={"label": "Revenue (£)"})
    plt.title("Revenue by Country (Top 8) and Month")
    plt.xlabel("Month")
    plt.ylabel("Country")
    plt.xticks(rotation=45)
    savefig("10_country_month_revenue_heatmap.png")

    findings["country_month_pivot_top8"] = pivot.round(2).to_dict()
    return pivot


def anomaly_detection(df):
    sales_all = df.copy()

    # IQR-based outlier detection on Quantity and UnitPrice (valid sales only)
    valid = df[df["IsValidSale"]]
    q1_qty, q3_qty = valid["Quantity"].quantile([0.25, 0.75])
    iqr_qty = q3_qty - q1_qty
    upper_qty = q3_qty + 3 * iqr_qty
    qty_outliers = valid[valid["Quantity"] > upper_qty]

    q1_price, q3_price = valid["UnitPrice"].quantile([0.25, 0.75])
    iqr_price = q3_price - q1_price
    upper_price = q3_price + 3 * iqr_price
    price_outliers = valid[valid["UnitPrice"] > upper_price]

    findings["anomaly_detection"] = {
        "quantity_outlier_threshold": round(float(upper_qty), 2),
        "quantity_outlier_count": int(len(qty_outliers)),
        "quantity_outlier_pct": round(len(qty_outliers) / len(valid) * 100, 3),
        "max_quantity_observed": int(valid["Quantity"].max()),
        "unitprice_outlier_threshold": round(float(upper_price), 2),
        "unitprice_outlier_count": int(len(price_outliers)),
        "unitprice_outlier_pct": round(len(price_outliers) / len(valid) * 100, 3),
        "max_unitprice_observed": round(float(valid["UnitPrice"].max()), 2),
    }
    print("\nAnomaly detection:", json.dumps(findings["anomaly_detection"], indent=2))

    plt.figure(figsize=(6, 5))
    sns.boxplot(y=valid["Quantity"].clip(upper=valid["Quantity"].quantile(0.999)), color="#55A868")
    plt.title("Quantity Boxplot (capped at 99.9th pct for visibility)")
    savefig("11_quantity_boxplot.png")

    plt.figure(figsize=(6, 5))
    sns.boxplot(y=valid["UnitPrice"].clip(upper=valid["UnitPrice"].quantile(0.999)), color="#C44E52")
    plt.title("Unit Price Boxplot (capped at 99.9th pct for visibility)")
    savefig("12_unitprice_boxplot.png")

    # cancellations over time
    cancel_by_month = df.groupby("InvoiceMonth")["IsCancelled"].mean() * 100
    findings["cancellation_rate_by_month_pct"] = cancel_by_month.round(2).to_dict()
    plt.figure(figsize=(10, 5))
    cancel_by_month.plot(kind="line", marker="o", color="#8172B2")
    plt.title("Cancellation Rate (%) by Month")
    plt.ylabel("% of Transaction Lines Cancelled")
    plt.xticks(rotation=45)
    savefig("13_cancellation_rate_by_month.png")

    return qty_outliers, price_outliers


def rfm_segmentation(df):
    cust = df[df["IsValidSale"] & df["HasCustomerID"]].copy()
    snapshot_date = cust["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = cust.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Revenue", "sum"),
    ).reset_index()

    findings["rfm_summary"] = {
        "n_customers": int(len(rfm)),
        "recency_describe": rfm["Recency"].describe().round(2).to_dict(),
        "frequency_describe": rfm["Frequency"].describe().round(2).to_dict(),
        "monetary_describe": rfm["Monetary"].describe().round(2).to_dict(),
    }

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    sns.histplot(rfm["Recency"], bins=40, ax=axes[0], color="#4C72B0")
    axes[0].set_title("Recency (days since last purchase)")
    sns.histplot(rfm["Frequency"].clip(upper=rfm["Frequency"].quantile(0.99)), bins=40, ax=axes[1], color="#DD8452")
    axes[1].set_title("Frequency (distinct invoices, 99th pct capped)")
    sns.histplot(rfm["Monetary"].clip(upper=rfm["Monetary"].quantile(0.99)), bins=40, ax=axes[2], color="#55A868")
    axes[2].set_title("Monetary (£ spent, 99th pct capped)")
    savefig("14_rfm_distributions.png")

    top_customers = rfm.sort_values("Monetary", ascending=False).head(10)
    findings["top10_customers_by_monetary"] = top_customers.round(2).to_dict(orient="records")

    return rfm


# ---------------------------------------------------------------------------
# PHASE 6: STATISTICAL ANALYSIS
# ---------------------------------------------------------------------------

def statistical_tests(df):
    sales = df[df["IsValidSale"]].copy()
    results = {}

    # --- Test 1: Independent samples t-test ---
    # H0: mean line-item revenue is equal for UK vs non-UK transactions
    # H1: mean line-item revenue differs between UK and non-UK transactions
    uk = sales.loc[sales["Country"] == "United Kingdom", "Revenue"]
    non_uk = sales.loc[sales["Country"] != "United Kingdom", "Revenue"]
    t_stat, p_val = stats.ttest_ind(uk, non_uk, equal_var=False)
    results["ttest_uk_vs_nonuk_revenue"] = {
        "hypothesis": "H0: mean revenue per line item is equal for UK vs non-UK transactions",
        "uk_mean": round(float(uk.mean()), 3),
        "non_uk_mean": round(float(non_uk.mean()), 3),
        "t_statistic": round(float(t_stat), 4),
        "p_value": float(p_val),
        "significant_at_0.05": bool(p_val < 0.05),
    }

    # --- Test 2: One-way ANOVA across quarters ---
    # H0: mean invoice-level revenue is equal across all four quarters
    invoice_rev = sales.groupby(["InvoiceNo", "Quarter"])["Revenue"].sum().reset_index()
    groups = [g["Revenue"].values for _, g in invoice_rev.groupby("Quarter")]
    f_stat, p_val_anova = stats.f_oneway(*groups)
    results["anova_quarterly_invoice_revenue"] = {
        "hypothesis": "H0: mean invoice revenue is equal across quarters",
        "f_statistic": round(float(f_stat), 4),
        "p_value": float(p_val_anova),
        "significant_at_0.05": bool(p_val_anova < 0.05),
        "quarterly_means": invoice_rev.groupby("Quarter")["Revenue"].mean().round(2).to_dict(),
    }

    # --- Test 3: Chi-square test of independence ---
    # H0: cancellation status is independent of customer country (top 6 countries by volume)
    top6 = df["Country"].value_counts().head(6).index
    sub = df[df["Country"].isin(top6)]
    contingency = pd.crosstab(sub["Country"], sub["IsCancelled"])
    chi2, p_chi, dof, expected = stats.chi2_contingency(contingency)
    results["chisquare_country_vs_cancellation"] = {
        "hypothesis": "H0: cancellation status is independent of country",
        "chi2_statistic": round(float(chi2), 4),
        "degrees_of_freedom": int(dof),
        "p_value": float(p_chi),
        "significant_at_0.05": bool(p_chi < 0.05),
        "contingency_table": contingency.to_dict(),
    }

    # --- Test 4: Pearson correlation significance (Quantity vs UnitPrice) ---
    r, p_corr = stats.pearsonr(sales["Quantity"], sales["UnitPrice"])
    results["correlation_quantity_unitprice"] = {
        "hypothesis": "H0: no linear correlation between Quantity and UnitPrice",
        "pearson_r": round(float(r), 4),
        "p_value": float(p_corr),
        "significant_at_0.05": bool(p_corr < 0.05),
    }

    # --- Test 5: 95% confidence interval for mean invoice value ---
    invoice_totals = sales.groupby("InvoiceNo")["Revenue"].sum()
    mean_val = invoice_totals.mean()
    sem = stats.sem(invoice_totals)
    ci = stats.t.interval(0.95, len(invoice_totals) - 1, loc=mean_val, scale=sem)
    results["confidence_interval_mean_invoice_value"] = {
        "mean_invoice_value": round(float(mean_val), 2),
        "95pct_ci_low": round(float(ci[0]), 2),
        "95pct_ci_high": round(float(ci[1]), 2),
        "n_invoices": int(len(invoice_totals)),
    }

    findings["statistical_tests"] = results
    print("\nStatistical test results:\n", json.dumps(results, indent=2, default=str))
    return results


# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("CodeAlpha Task 2 - EDA Pipeline: Online Retail Dataset")
    print("=" * 70)

    df_raw = load_data()
    explore_structure(df_raw)
    missing_value_analysis(df_raw)
    duplicate_analysis(df_raw)
    data_quality_checks(df_raw)

    df = clean_data(df_raw)

    univariate_analysis(df)
    bivariate_analysis(df)
    trend_analysis(df)
    correlation_analysis(df)
    multivariate_analysis(df)
    anomaly_detection(df)
    rfm_segmentation(df)
    statistical_tests(df)

    df.to_csv(PROCESSED_PATH, index=False)
    print(f"\nSaved cleaned dataset to {PROCESSED_PATH.relative_to(ROOT)}")

    with open(FINDINGS_PATH, "w") as f:
        json.dump(findings, f, indent=2, default=str)
    print(f"Saved findings to {FINDINGS_PATH.relative_to(ROOT)}")

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
