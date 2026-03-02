import pdfplumber
import re

pdf_path = "price_catalog.pdf"

all_ids = set()

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if not text:
            continue

        matches = re.findall(r"1SDA\d{6}R1", text)
        for m in matches:
            all_ids.add(m)

print("Total unique 1SDA codes found in entire PDF:", len(all_ids))