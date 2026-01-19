from typing import Dict, List, Tuple
from datetime import datetime
import os

from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products,
)


def _money(x: float) -> str:
    return f"₹{x:,.2f}"


def generate_sales_report(
    transactions: List[Dict],
    enriched_transactions: List[Dict],
    output_file: str = r"output\sales_report.txt"
) -> None:
    """
    Generates a comprehensive formatted text report.
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_txns = len(transactions)

    total_revenue = calculate_total_revenue(transactions)
    avg_order_value = (total_revenue / total_txns) if total_txns else 0.0

    dates = sorted({t.get("Date") for t in transactions if t.get("Date")})
    date_range = f"{dates[0]} to {dates[-1]}" if dates else "N/A"

    # analytics
    region_stats = region_wise_sales(transactions)
    top5_products = top_selling_products(transactions, n=5)
    cust_stats = customer_analysis(transactions)
    top5_customers = list(cust_stats.items())[:5]
    trend = daily_sales_trend(transactions)
    peak_date, peak_rev, peak_count = find_peak_sales_day(transactions)
    low_perf = low_performing_products(transactions, threshold=10)

    # avg transaction value per region
    avg_txn_region = {}
    for r, s in region_stats.items():
        cnt = s["transaction_count"]
        avg_txn_region[r] = (s["total_sales"] / cnt) if cnt else 0.0

    # API enrichment summary
    enriched_total = len(enriched_transactions)
    enriched_success = sum(1 for t in enriched_transactions if t.get("API_Match") is True)
    success_rate = (enriched_success / enriched_total * 100) if enriched_total else 0.0

    not_enriched = [t.get("ProductID") for t in enriched_transactions if t.get("API_Match") is False]
    not_enriched_unique = sorted({p for p in not_enriched if p})

    # write report
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("============================================\n")
        f.write("           SALES ANALYTICS REPORT\n")
        f.write(f"         Generated: {now}\n")
        f.write(f"         Records Processed: {total_txns}\n")
        f.write("============================================\n\n")

        # 2) Overall Summary
        f.write("OVERALL SUMMARY\n")
        f.write("--------------------------------------------\n")
        f.write(f"Total Revenue:        {_money(total_revenue)}\n")
        f.write(f"Total Transactions:   {total_txns}\n")
        f.write(f"Average Order Value:  {_money(avg_order_value)}\n")
        f.write(f"Date Range:           {date_range}\n\n")

        # 3) Region-wise Performance
        f.write("REGION-WISE PERFORMANCE\n")
        f.write("--------------------------------------------\n")
        f.write(f"{'Region':8} {'Sales':15} {'% of Total':10} {'Transactions':12}\n")
        for r, s in region_stats.items():
            f.write(f"{r:8} {_money(s['total_sales']):15} {s['percentage']:9.2f}% {s['transaction_count']:12}\n")
        f.write("\n")

        # 4) Top 5 Products
        f.write("TOP 5 PRODUCTS\n")
        f.write("--------------------------------------------\n")
        f.write(f"{'Rank':4} {'Product Name':25} {'Qty Sold':10} {'Revenue':15}\n")
        for i, (name, qty, rev) in enumerate(top5_products, start=1):
            f.write(f"{i:<4} {name[:25]:25} {qty:10} {_money(rev):15}\n")
        f.write("\n")

        # 5) Top 5 Customers
        f.write("TOP 5 CUSTOMERS\n")
        f.write("--------------------------------------------\n")
        f.write(f"{'Rank':4} {'Customer':10} {'Total Spent':15} {'Orders':8}\n")
        for i, (cid, s) in enumerate(top5_customers, start=1):
            f.write(f"{i:<4} {cid:10} {_money(s['total_spent']):15} {s['purchase_count']:8}\n")
        f.write("\n")

        # 6) Daily Sales Trend
        f.write("DAILY SALES TREND\n")
        f.write("--------------------------------------------\n")
        f.write(f"{'Date':12} {'Revenue':15} {'Txns':6} {'Unique Customers':16}\n")
        for d, s in trend.items():
            f.write(f"{d:12} {_money(s['revenue']):15} {s['transaction_count']:6} {s['unique_customers']:16}\n")
        f.write("\n")

        # 7) Product Performance Analysis
        f.write("PRODUCT PERFORMANCE ANALYSIS\n")
        f.write("--------------------------------------------\n")
        f.write(f"Best selling day: {peak_date} | Revenue: {_money(peak_rev)} | Transactions: {peak_count}\n\n")

        f.write("Low performing products (Qty < 10):\n")
        if not low_perf:
            f.write("None\n")
        else:
            for name, qty, rev in low_perf:
                f.write(f"- {name}: Qty={qty}, Revenue={_money(rev)}\n")
        f.write("\n")

        f.write("Average transaction value per region:\n")
        for r in avg_txn_region:
            f.write(f"- {r}: {_money(avg_txn_region[r])}\n")
        f.write("\n")

        # 8) API Enrichment Summary
        f.write("API ENRICHMENT SUMMARY\n")
        f.write("--------------------------------------------\n")
        f.write(f"Total products enriched: {enriched_success}/{enriched_total}\n")
        f.write(f"Success rate: {success_rate:.2f}%\n")
        f.write("Products that couldn't be enriched:\n")
        if not not_enriched_unique:
            f.write("None\n")
        else:
            for p in not_enriched_unique:
                f.write(f"- {p}\n")
        f.write("\n")

    print(f"✓ Report saved to: {output_file}")
