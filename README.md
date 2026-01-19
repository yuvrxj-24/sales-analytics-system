# Sales Analytics System

A Python-based sales analytics pipeline that:
- Reads sales data with encoding handling
- Parses, cleans, validates, and optionally filters transactions
- Computes sales analytics (region, products, customers, trends)
- Fetches product metadata from DummyJSON API
- Enriches transactions and saves to file
- Generates a comprehensive text report

## Folder Structure
- `data/sales_data.txt` (input)
- `data/enriched_sales_data.txt` (generated)
- `output/sales_report.txt` (generated)
- `utils/` (modules)
- `main.py` (runner)

## Setup
```bash
python -m pip install -r requirements.txt
