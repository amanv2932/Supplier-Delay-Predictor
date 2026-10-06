import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add pathlib import if it's not there
if 'from pathlib import Path' not in content:
    content = content.replace('import os', 'import os\nfrom pathlib import Path')

# Add BASE_DIR logic right after imports
if 'BASE_DIR =' not in content:
    # Find the # --- SETTINGS --- line
    content = content.replace('# --- SETTINGS ---', 'BASE_DIR = Path(__file__).resolve().parent\nDATA_PATH = BASE_DIR / "supplier_shipment_delay_dataset.csv"\n\n# --- SETTINGS ---')

# Replace the hardcoded string with the pathlib object
content = content.replace("'supplier_shipment_delay_dataset.csv'", "DATA_PATH")
content = content.replace('"supplier_shipment_delay_dataset.csv"', "DATA_PATH")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
