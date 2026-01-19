from typing import Dict, List


def clean_sales_data(raw_lines: List[str]) -> List[Dict]:
    """
    Cleans and validates raw sales transaction lines.

    Cleaning:
    - Remove commas from ProductName (e.g., 'Mouse,Wireless' -> 'MouseWireless')
    - Remove commas from numeric values (e.g., '1,916' -> '1916')

    Remove invalid records:
    - Missing CustomerID or Region
    - Quantity <= 0
    - UnitPrice <= 0
    - TransactionID not starting with 'T'

    Returns:
        List of cleaned transaction dictionaries
    """
    total = len(raw_lines)
    invalid = 0
    cleaned_records: List[Dict] = []

    for line in raw_lines:
        parts = line.split("|")

        # Defensive check: ensure correct number of fields
        if len(parts) != 8:
            invalid += 1
            continue

        transaction_id, date, product_id, product_name, qty, unit_price, customer_id, region = parts

        # Trim spaces
        transaction_id = transaction_id.strip()
        date = date.strip()
        product_id = product_id.strip()
        product_name = product_name.strip()
        qty = qty.strip()
        unit_price = unit_price.strip()
        customer_id = customer_id.strip()
        region = region.strip()

        # Rule: TransactionID must start with "T"
        if not transaction_id.startswith("T"):
            invalid += 1
            continue

        # Rule: CustomerID and Region must not be missing
        if customer_id == "" or region == "":
            invalid += 1
            continue

        # Clean product name commas
        product_name = product_name.replace(",", "")

        # Clean numeric commas and convert types
        try:
            quantity = int(qty.replace(",", ""))
            price = float(unit_price.replace(",", ""))
        except ValueError:
            invalid += 1
            continue

        # Rule: Quantity and UnitPrice must be > 0
        if quantity <= 0 or price <= 0:
            invalid += 1
            continue

        revenue = quantity * price

        cleaned_records.append({
            "TransactionID": transaction_id,
            "Date": date,
            "ProductID": product_id,
            "ProductName": product_name,
            "Quantity": quantity,
            "UnitPrice": price,
            "CustomerID": customer_id,
            "Region": region,
            "Revenue": revenue
        })

    print(f"Total records parsed: {total}")
    print(f"Invalid records removed: {invalid}")
    print(f"Valid records after cleaning: {len(cleaned_records)}")

    return cleaned_records
from typing import Dict, List


def parse_transactions(raw_lines: List[str]) -> List[Dict]:
    """
    Parses raw lines into a clean list of transaction dictionaries.

    Returns dictionaries with keys:
    ['TransactionID', 'Date', 'ProductID', 'ProductName',
     'Quantity', 'UnitPrice', 'CustomerID', 'Region']

    Rules:
    - Split by pipe '|'
    - Handle commas within ProductName (remove or replace)
    - Remove commas from numeric fields and convert to types
    - Quantity -> int
    - UnitPrice -> float
    - Skip rows with incorrect number of fields
    """
    transactions: List[Dict] = []

    for line in raw_lines:
        parts = line.split("|")

        # Skip malformed rows
        if len(parts) != 8:
            continue

        transaction_id, date, product_id, product_name, qty, unit_price, customer_id, region = parts

        # Strip whitespace
        transaction_id = transaction_id.strip()
        date = date.strip()
        product_id = product_id.strip()
        product_name = product_name.strip()
        qty = qty.strip()
        unit_price = unit_price.strip()
        customer_id = customer_id.strip()
        region = region.strip()

        # Handle commas in ProductName
        product_name = product_name.replace(",", "")

        # Remove commas from numeric fields and convert
        try:
            quantity = int(qty.replace(",", ""))
            price = float(unit_price.replace(",", ""))
        except ValueError:
            # If conversion fails, skip the row
            continue

        transactions.append({
            "TransactionID": transaction_id,
            "Date": date,
            "ProductID": product_id,
            "ProductName": product_name,
            "Quantity": quantity,
            "UnitPrice": price,
            "CustomerID": customer_id,
            "Region": region
        })

    return transactions
from typing import Dict, List, Tuple, Optional


def validate_and_filter(
    transactions: List[Dict],
    region: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
) -> Tuple[List[Dict], int, Dict]:
    """
    Validates transactions and applies optional filters.

    Returns: (valid_transactions, invalid_count, filter_summary)
    """

    required_keys = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region"
    ]

    total_input = len(transactions)

    # ---- Display available regions ----
    available_regions = sorted({t.get("Region") for t in transactions if t.get("Region")})
    print("\n[3/10] Filter Options Available:")
    print("Regions:", ", ".join(available_regions) if available_regions else "None")

    # ---- Display transaction amount range ----
       # ---- Validation ----
    valid = []
    invalid_count = 0

    for t in transactions:
        # Check required fields
        if any(k not in t or t[k] in (None, "") for k in required_keys):
            invalid_count += 1
            continue

        # Check ID formats
        if not str(t["TransactionID"]).startswith("T"):
            invalid_count += 1
            continue
        if not str(t["ProductID"]).startswith("P"):
            invalid_count += 1
            continue
        if not str(t["CustomerID"]).startswith("C"):
            invalid_count += 1
            continue

        # Check numeric constraints
        try:
            qty = int(t["Quantity"])
            price = float(t["UnitPrice"])
        except Exception:
            invalid_count += 1
            continue

        if qty <= 0 or price <= 0:
            invalid_count += 1
            continue

        # Store amount temporarily for filtering + range display
        t["_Amount"] = qty * price
        valid.append(t)

    # ---- Display transaction amount range (VALID ONLY) ----
    valid_amounts = [t["_Amount"] for t in valid]
    if valid_amounts:
        print(f"Amount Range: ₹{min(valid_amounts):,.2f} - ₹{max(valid_amounts):,.2f}")
    else:
        print("Amount Range: Not available")

    print(f"\n[4/10] Validating transactions...")
    print(f"✓ Valid: {len(valid)} | Invalid: {invalid_count}")

    # ---- Filtering ----
    filter_summary = {
        "total_input": total_input,
        "invalid": invalid_count,
        "filtered_by_region": 0,
        "filtered_by_amount": 0,
        "final_count": 0
    }

    filtered = valid

    # Region filter
    if region:
        before = len(filtered)
        filtered = [t for t in filtered if t.get("Region") == region]
        removed = before - len(filtered)
        filter_summary["filtered_by_region"] = removed
        print(f"[After Region Filter: {region}] Remaining: {len(filtered)}")
    else:
        print("[Region Filter] Skipped")

    # Amount filter
    if min_amount is not None or max_amount is not None:
        before = len(filtered)

        def in_range(t: Dict) -> bool:
            amt = t.get("_Amount", 0)
            if min_amount is not None and amt < float(min_amount):
                return False
            if max_amount is not None and amt > float(max_amount):
                return False
            return True

        filtered = [t for t in filtered if in_range(t)]
        removed = before - len(filtered)
        filter_summary["filtered_by_amount"] = removed
        print(f"[After Amount Filter] Remaining: {len(filtered)}")
    else:
        print("[Amount Filter] Skipped")

    filter_summary["final_count"] = len(filtered)

    # Remove helper key before returning
    for t in filtered:
        t.pop("_Amount", None)

    return filtered, invalid_count, filter_summary


def calculate_total_revenue(transactions: List[Dict]) -> float:
    total = 0.0
    for t in transactions:
        try:
            total += int(t["Quantity"]) * float(t["UnitPrice"])
        except Exception:
            continue
    return total

def region_wise_sales(transactions: List[Dict]) -> Dict:
    """
    Analyzes sales by region.
    Returns a dictionary with region statistics sorted by total_sales descending.
    """
    total_revenue = calculate_total_revenue(transactions)

    region_stats: Dict[str, Dict] = {}

    # 1) accumulate totals + counts
    for t in transactions:
        try:
            region = str(t["Region"])
            amount = int(t["Quantity"]) * float(t["UnitPrice"])
        except Exception:
            continue

        if region not in region_stats:
            region_stats[region] = {
                "total_sales": 0.0,
                "transaction_count": 0,
                "percentage": 0.0
            }

        region_stats[region]["total_sales"] += amount
        region_stats[region]["transaction_count"] += 1

    # 2) compute percentages
    for region in region_stats:
        if total_revenue > 0:
            region_stats[region]["percentage"] = (region_stats[region]["total_sales"] / total_revenue) * 100
        else:
            region_stats[region]["percentage"] = 0.0

    # 3) sort by total_sales desc
    sorted_items = sorted(region_stats.items(), key=lambda x: x[1]["total_sales"], reverse=True)
    return dict(sorted_items)

def top_selling_products(transactions: List[Dict], n: int = 5) -> List[tuple]:
    """
    Finds top n products by total quantity sold.
    Returns list of tuples: (ProductName, TotalQuantity, TotalRevenue)
    """
    product_stats: Dict[str, Dict] = {}

    # 1) Aggregate by ProductName
    for t in transactions:
        try:
            name = str(t["ProductName"])
            qty = int(t["Quantity"])
            rev = qty * float(t["UnitPrice"])
        except Exception:
            continue

        if name not in product_stats:
            product_stats[name] = {"total_qty": 0, "total_rev": 0.0}

        product_stats[name]["total_qty"] += qty
        product_stats[name]["total_rev"] += rev

    # 2) Convert to list of tuples
    result = [(name, vals["total_qty"], vals["total_rev"]) for name, vals in product_stats.items()]

    # 3) Sort by TotalQuantity desc
    result.sort(key=lambda x: x[1], reverse=True)

    # 4) Return top n
    return result[:n]

def customer_analysis(transactions: List[Dict]) -> Dict:
    """
    Analyzes customer purchase patterns.
    Returns dictionary of customer stats sorted by total_spent descending.
    """
    customer_stats: Dict[str, Dict] = {}

    # 1) Aggregate spend, count, and unique products
    for t in transactions:
        try:
            cid = str(t["CustomerID"])
            pname = str(t["ProductName"])
            amount = int(t["Quantity"]) * float(t["UnitPrice"])
        except Exception:
            continue

        if cid not in customer_stats:
            customer_stats[cid] = {
                "total_spent": 0.0,
                "purchase_count": 0,
                "avg_order_value": 0.0,
                "products_bought": set()  # use set to keep unique
            }

        customer_stats[cid]["total_spent"] += amount
        customer_stats[cid]["purchase_count"] += 1
        customer_stats[cid]["products_bought"].add(pname)

    # 2) Finalize avg + convert set to list
    for cid in customer_stats:
        count = customer_stats[cid]["purchase_count"]
        total = customer_stats[cid]["total_spent"]
        customer_stats[cid]["avg_order_value"] = (total / count) if count else 0.0
        customer_stats[cid]["products_bought"] = sorted(list(customer_stats[cid]["products_bought"]))

    # 3) Sort by total_spent desc
    sorted_items = sorted(customer_stats.items(), key=lambda x: x[1]["total_spent"], reverse=True)
    return dict(sorted_items)

def daily_sales_trend(transactions: List[Dict]) -> Dict:
    """
    Analyzes sales trends by date.
    Returns dict sorted chronologically by date.
    """
    daily: Dict[str, Dict] = {}

    # 1) group + accumulate
    for t in transactions:
        try:
            date = str(t["Date"])
            cid = str(t["CustomerID"])
            amount = int(t["Quantity"]) * float(t["UnitPrice"])
        except Exception:
            continue

        if date not in daily:
            daily[date] = {
                "revenue": 0.0,
                "transaction_count": 0,
                "unique_customers": set()
            }

        daily[date]["revenue"] += amount
        daily[date]["transaction_count"] += 1
        daily[date]["unique_customers"].add(cid)

    # 2) finalize unique customers (convert set -> count)
    for date in daily:
        daily[date]["unique_customers"] = len(daily[date]["unique_customers"])

    # 3) sort chronologically (YYYY-MM-DD sorts naturally as strings)
    sorted_items = sorted(daily.items(), key=lambda x: x[0])
    return dict(sorted_items)

def find_peak_sales_day(transactions: List[Dict]) -> tuple:
    """
    Identifies the date with highest revenue.
    Returns: (date, revenue, transaction_count)
    """
    trend = daily_sales_trend(transactions)

    if not trend:
        return ("", 0.0, 0)

    # max by revenue
    peak_date, stats = max(trend.items(), key=lambda x: x[1]["revenue"])
    return (peak_date, stats["revenue"], stats["transaction_count"])

def low_performing_products(transactions: List[Dict], threshold: int = 10) -> List[tuple]:
    """
    Identifies products with total quantity sold < threshold.
    Returns list of tuples: (ProductName, TotalQuantity, TotalRevenue)
    Sorted by TotalQuantity ascending.
    """
    product_map: Dict[str, Dict] = {}

    # 1) aggregate per product
    for t in transactions:
        try:
            name = str(t["ProductName"])
            qty = int(t["Quantity"])
            rev = qty * float(t["UnitPrice"])
        except Exception:
            continue

        if name not in product_map:
            product_map[name] = {"qty": 0, "rev": 0.0}

        product_map[name]["qty"] += qty
        product_map[name]["rev"] += rev

    # 2) filter low performers
    low_list = [
        (name, vals["qty"], vals["rev"])
        for name, vals in product_map.items()
        if vals["qty"] < threshold
    ]

    # 3) sort by qty ascending
    low_list.sort(key=lambda x: x[1])

    return low_list
