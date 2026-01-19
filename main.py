from utils.file_handler import read_sales_data
from utils.data_processor import parse_transactions, validate_and_filter, calculate_total_revenue,region_wise_sales,top_selling_products,customer_analysis
from utils.data_processor import daily_sales_trend, find_peak_sales_day, low_performing_products
from utils.api_handler import fetch_all_products, create_product_mapping, enrich_sales_data, save_enriched_data
from utils.report_generator import generate_sales_report



def _to_float_or_none(s: str):
    s = s.strip()
    if s == "":
        return None
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return None


def main():
    try: 
        print("========================================")
        print("SALES ANALYTICS SYSTEM")
        print("========================================\n")

        # [1/10] Read
        print("[1/10] Reading sales data...")
        raw_lines = read_sales_data(r"data\sales_data.txt")
        print(f"✓ Successfully read {len(raw_lines)} transactions\n")

        # [2/10] Parse
        print("[2/10] Parsing and cleaning data...")
        transactions = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(transactions)} records\n")

        # Ask user if they want filters
        choice = input("Do you want to filter data? (y/n): ").strip().lower()

        region = None
        min_amount = None
        max_amount = None

        if choice == "y":
            region_in = input("Enter region (or press Enter to skip): ").strip()
            if region_in:
                region = region_in.title()  # ✅ normalize

            min_amount = _to_float_or_none(input("Enter minimum amount (or press Enter to skip): "))
            max_amount = _to_float_or_none(input("Enter maximum amount (or press Enter to skip): "))

        # [4/10] Validate + Filter
        valid_txns, invalid_count, summary = validate_and_filter(
            transactions,
            region=region,
            min_amount=min_amount,
            max_amount=max_amount
        )

        print("\nValidation + Filter Summary:")
        print(summary)

        # Revenue after filtering
        total_rev = calculate_total_revenue(valid_txns)
        print(f"\nTotal Revenue: ₹{total_rev:,.2f}")

            # Region-wise performance
        region_stats = region_wise_sales(valid_txns)
        print("\nREGION-WISE SALES (sorted by total_sales):")
        for r, s in region_stats.items():
            print(f"{r:6} | Sales: ₹{s['total_sales']:,.2f} | %: {s['percentage']:.2f}% | Txns: {s['transaction_count']}")

        top5 = top_selling_products(valid_txns, n=5)

        print("\nTOP 5 SELLING PRODUCTS:")
        print("Rank | Product Name                 | Qty Sold | Revenue")
        for i, (name, qty, rev) in enumerate(top5, start=1):
            print(f"{i:>4} | {name[:27]:27} | {qty:>8} | ₹{rev:,.2f}")


        cust_stats = customer_analysis(valid_txns)

        print("\nTOP 5 CUSTOMERS:")
        print("Rank | Customer | Total Spent      | Orders | Avg Order Value")
        for i, (cid, s) in enumerate(cust_stats.items(), start=1):
            if i > 5:
                break
            print(
                f"{i:>4} | {cid:8} | ₹{s['total_spent']:>13,.2f} | "
                f"{s['purchase_count']:>6} | ₹{s['avg_order_value']:,.2f}"
            )


        trend = daily_sales_trend(valid_txns)

        print("\nDAILY SALES TREND:")
        print("Date         | Revenue         | Txns | Unique Customers")
        for date, s in trend.items():
            print(f"{date} | ₹{s['revenue']:>13,.2f} | {s['transaction_count']:>4} | {s['unique_customers']:>16}")

        peak_date, peak_rev, peak_txn = find_peak_sales_day(valid_txns)
        print("\nPEAK SALES DAY:")
        print(f"{peak_date} | Revenue: ₹{peak_rev:,.2f} | Transactions: {peak_txn}")
        

        low_perf = low_performing_products(valid_txns, threshold=10)

        print("\nLOW PERFORMING PRODUCTS (Qty < 10):")
        if not low_perf:
            print("None")
        else:
            print("Product Name                 | Qty Sold | Revenue")
            for name, qty, rev in low_perf:
                print(f"{name[:27]:27} | {qty:>8} | ₹{rev:,.2f}")


        print("\n[6/10] Fetching product data from API...")
        api_products = fetch_all_products()

        product_mapping = create_product_mapping(api_products)

        print("\n[7/10] Enriching sales data...")
        enriched_txns = enrich_sales_data(valid_txns, product_mapping)

        enriched_success = sum(1 for t in enriched_txns if t.get("API_Match") is True)
        total_valid = len(enriched_txns)
        rate = (enriched_success / total_valid * 100) if total_valid else 0.0
        print(f"✓ Enriched {enriched_success}/{total_valid} transactions ({rate:.1f}%)")

        print("\n[8/10] Saving enriched data...")
        save_enriched_data(enriched_txns, r"data\enriched_sales_data.txt")
        print("✓ Saved to: data\\enriched_sales_data.txt")

        print("\n[9/10] Generating report...")
        generate_sales_report(valid_txns, enriched_txns, r"output\sales_report.txt")

        print("\n[10/10] Process Complete!")
        print("========================================")
        print("✓ Enriched file: data\\enriched_sales_data.txt")
        print("✓ Report file:   output\\sales_report.txt")
        print("========================================")
        pass
    except FileNotFoundError as e:
        print(f"✗ File error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")    

if __name__ == "__main__":
    main()
