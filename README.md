
A Python-based sales analytics pipeline that:
- Reads sales data with encoding handling
- Parses, cleans, validates, and optionally filters transactions
- Computes analytics (revenue, region, products, customers, daily trend)
- Fetches product metadata from DummyJSON API and enriches transactions
- Saves enriched data and generates a comprehensive text report

## Folder Structure
- `main.py` — main application entry point
- `utils/` — modules (file handling, processing, API, report generator)
- `data/sales_data.txt` — input sales data
- `data/enriched_sales_data.txt` — generated enriched output
- `output/sales_report.txt` — generated report output

## Filtering (Optional)
When prompted:
- Enter region like `North` / `South` / `East` / `West`
- Enter min/max amount to filter by transaction value (Quantity * UnitPrice)
- Press Enter to skip any filter

## Verify Outputs
```powershell
Get-Content .\data\enriched_sales_data.txt -TotalCount 3
Get-Content .\output\sales_report.txt -TotalCount 30

## Setup
## Troubleshooting
If you get `ModuleNotFoundError: No module named 'requests'`:
Install dependencies:
```bash
python -m pip install -r requirements.txt