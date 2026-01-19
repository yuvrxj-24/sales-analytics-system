from typing import List


def read_sales_data(filename: str) -> List[str]:
    """
    Reads sales data from file handling encoding issues.

    Returns:
        list of raw transaction lines (strings)
    """
    encodings_to_try = ["utf-8", "latin-1", "cp1252"]

    for enc in encodings_to_try:
        try:
            with open(filename, "r", encoding=enc) as f:
                lines = f.readlines()

            # Remove empty lines and strip whitespace/newlines
            cleaned = [line.strip() for line in lines if line.strip()]

            # Skip header row if present
            if cleaned and cleaned[0].lower().startswith("transactionid"):
                cleaned = cleaned[1:]

            return cleaned

        except FileNotFoundError:
            print(f"Error: File not found -> {filename}")
            return []
        except UnicodeDecodeError:
            # Try next encoding
            continue
        except Exception as e:
            print(f"Error reading '{filename}': {e}")
            return []

    print(f"Error: Unable to decode '{filename}' with tried encodings: {encodings_to_try}")
    return []
