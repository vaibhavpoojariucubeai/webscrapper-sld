# ABB Product & Price Web Scraper

A Python-based automation tool that:

- Scrapes technical product details from the ABB website  
- Extracts product prices from ABB Electrification Price List PDF  
- Merges product data with pricing  
- Exports a structured CSV file  

---

## 📌 Project Overview

This scraper performs two main tasks:

### 1️⃣ Web Scraping (ABB Website)

For each Product ID, the scraper extracts:

- Extended Product Type  
- Rated Current  
- Product Main Type  
- Electrical Durability  
- Rated Insulation Voltage  
- Rated Voltage  
- Rated Impulse Withstand Voltage  
- Rated Operational Voltage  
- Number of Poles  
- Rated Service Short-Circuit Breaking Capacity  

It uses:
- Selenium
- Dynamic page stabilization
- Technical section expansion
- Intelligent waiting logic

---

### 2️⃣ PDF Price Extraction

Extracts prices from:

**Electrification Products Price List – April 2025**

Method:
- Character-level PDF parsing using `pdfplumber`
- Regex detection for:
  - Product IDs (`1SDAxxxxxxR1`)
  - Price patterns (`12,340`)
  - "Upon Request"
- Handles:
  - Broken tables
  - Split text
  - Multi-column layouts
  - Vector-rendered tables

---

## 🛠️ Tech Stack

- Python 3.9+
- Selenium
- pdfplumber
- pandas
- re (Regex)

---

## 📂 Project Structure

```
webscrapper/
│
├── abb_scraper.py
├── data_exp.xlsx
├── price_catalog.pdf
├── final_abb_products.csv
├── .venv/
└── README.md
```

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone <your-repo-url>
cd webscrapper
```

### 2️⃣ Create Virtual Environment (Windows)

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux / Mac:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install selenium pdfplumber pandas openpyxl
```

### 4️⃣ Install ChromeDriver

Download ChromeDriver matching your Chrome version:

https://chromedriver.chromium.org/

Add it to your system PATH or place it inside the project folder.

---

## ▶️ How to Run

```bash
python abb_scraper.py
```

---

## 🐳 Run with Docker

### Shortcuts with Makefile

```bash
make build   # docker compose build
make rebuild # docker compose build --no-cache
make run     # docker compose up scraper
make up      # build + run
make build-run # build + run
make down    # docker compose down -v (clears volumes)
```

By default, `make run` creates an `output` folder in the project and mounts it to `/output` inside container.
The final CSV is written there: `output/final_abb_products.csv`.

To use a different host folder:

```bash
make run OUTPUT_DIR=/mnt/c/Users/vaiba/Desktop/abb-output
```

### 1️⃣ Build with Docker Compose

```bash
docker compose build
```

### 2️⃣ Run scraper with Docker Compose

```bash
OUTPUT_DIR=./output docker compose up scraper
```

Windows PowerShell:

```powershell
$env:OUTPUT_DIR = "./output"; docker compose up scraper
```

This runs Chrome in a virtual display (`Xvfb`) and is suitable for websites that block true headless browsers.

### 3️⃣ Input / Output files

- Put `data_exp.xlsx` and `price_catalog.pdf` in project root before running.
- Output `final_abb_products.csv` is written to `output/` on your host (or custom `OUTPUT_DIR`).

### Optional: force headless mode (not recommended for ABB)

```bash
HEADLESS=true OUTPUT_DIR=./output docker compose up scraper
```

---

## 📥 Input Files

### `data_exp.xlsx`

Must contain column:

```
Product ID / Addtl Info
```

Example:

| Product ID / Addtl Info |
|--------------------------|
| 1SDA066799R1 |
| 1SDA066800R1 |

---

### `price_catalog.pdf`

ABB Electrification Price List PDF.

---

## 📤 Output

```
final_abb_products.csv
```

Contains:

| Product ID | Extended Product Type | Rated Current | ... | Price |

---

## 🔍 Extraction Logic Details

### Web Scraping Logic

- Opens product URL:
  ```
  https://new.abb.com/products/{ProductID}
  ```
- Waits for:
  - Body load
  - Page stabilization
- Expands Technical section if present
- Extracts structured fields via regex

---

### PDF Parsing Logic

Instead of relying on unreliable table extraction:

- Extracts raw character stream
- Reconstructs full page text
- Detects product IDs
- Searches nearby for price
- Stores unique entries

This avoids:
- Table misalignment issues
- Multi-column parsing errors
- Missing prices due to broken row extraction

---

## ⚠️ Known Limitations

- Some ABB products may not exist in the price book.
- Some products are marked "Upon Request".
- Some global SKUs may not appear in regional price list.
- PDF extraction depends on text layer availability.

---

## 🚀 Performance Notes

- PDF parsing: ~2–4 minutes for 364 pages
- Web scraping: Depends on number of product IDs
- Recommended to test with first 5 IDs before full run

---

## 🔒 Anti-Detection Measures Used

- Disabled Selenium automation flags
- Page stabilization logic
- Intelligent waiting
- Controlled delay between requests

---

## 🧠 Possible Improvements

- Parallel scraping
- OCR support for image-based PDF pages
- SQLite database storage
- Async request optimization
- Headless mode support
- Logging framework

