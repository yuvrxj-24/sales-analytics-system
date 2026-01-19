# utils/api_handler.py

from typing import Dict, List
import requests

BASE_URL = "https://dummyjson.com/products"


def fetch_all_products() -> List[Dict]:
    """
    Fetches ALL products from DummyJSON API.
    First gets total count, then fetches with limit=total.
    Returns: list of product dictionaries with required fields.
    """
    try:
        # 1) Get total count
        r1 = requests.get(BASE_URL, timeout=10)
        r1.raise_for_status()
        data1 = r1.json()
        total = int(data1.get("total", 0))

        if total <= 0:
            print("✗ API fetch failed: Could not determine total products")
            return []

        # 2) Fetch all products using limit=total
        url_all = f"{BASE_URL}?limit={total}"
        r2 = requests.get(url_all, timeout=15)
        r2.raise_for_status()
        data2 = r2.json()

        products = data2.get("products", [])

        cleaned = []
        for p in products:
            cleaned.append({
                "id": p.get("id"),
                "title": p.get("title"),
                "category": p.get("category"),
                "brand": p.get("brand"),
                "price": p.get("price"),
                "rating": p.get("rating")
            })

        print(f"✓ Fetched {len(cleaned)} products from API")
        return cleaned

    except requests.RequestException as e:
        print(f"✗ API fetch failed: {e}")
        return []
    except Exception as e:
        print(f"✗ Unexpected error while fetching products: {e}")
        return []

def create_product_mapping(api_products: List[Dict]) -> Dict[int, Dict]:
    """
    Creates mapping of product ID -> product info.
    """
    mapping: Dict[int, Dict] = {}

    for p in api_products:
        try:
            pid = int(p["id"])
            mapping[pid] = {
                "title": p.get("title"),
                "category": p.get("category"),
                "brand": p.get("brand"),
                "rating": p.get("rating")
            }
        except Exception:
            continue

    return mapping

def enrich_sales_data(transactions: List[Dict], product_mapping: Dict[int, Dict]) -> List[Dict]:
    """
    Enriches transactions with API product information.
    Adds: API_Category, API_Brand, API_Rating, API_Match
    """
    enriched = []

    for t in transactions:
        # Make a copy so we don’t mutate original list
        tx = dict(t)

        try:
            product_id = str(tx.get("ProductID", "")).strip()  # e.g., "P101"
            numeric_part = product_id[1:] if product_id.upper().startswith("P") else ""

            pid = int(numeric_part) if numeric_part.isdigit() else None
        except Exception:
            pid = None

        if pid is not None and pid in product_mapping:
            info = product_mapping[pid]
            tx["API_Category"] = info.get("category")
            tx["API_Brand"] = info.get("brand")
            tx["API_Rating"] = info.get("rating")
            tx["API_Match"] = True
        else:
            tx["API_Category"] = None
            tx["API_Brand"] = None
            tx["API_Rating"] = None
            tx["API_Match"] = False

        enriched.append(tx)

    return enriched

import os


def save_enriched_data(enriched_transactions: List[Dict], filename: str = r"data\enriched_sales_data.txt") -> None:
    """
    Saves enriched transactions to a pipe-delimited file with header.
    """
    headers = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region",
        "API_Category", "API_Brand", "API_Rating", "API_Match"
    ]

    # Ensure folder exists
    folder = os.path.dirname(filename)
    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("|".join(headers) + "\n")

        for t in enriched_transactions:
            row = []
            for h in headers:
                val = t.get(h, "")
                if val is None:
                    val = ""
                row.append(str(val))
            f.write("|".join(row) + "\n")

