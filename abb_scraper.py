import pandas as pd
import pdfplumber
import time
import re
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# -----------------------------
# SETTINGS
# -----------------------------
excel_path = "data_exp.xlsx"
pdf_path = "price_catalog.pdf"
DELAY_SECONDS = 5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


# -----------------------------
# LOAD PRODUCT IDS
# -----------------------------
df = pd.read_excel(excel_path)
df["Product ID / Addtl Info"] = df["Product ID / Addtl Info"].astype(str).str.strip()
product_ids = list(dict.fromkeys(df["Product ID / Addtl Info"].tolist()))

product_ids=product_ids[:5]  # TESTING ONLY - REMOVE THIS LINE FOR FULL RUN

logger.info("Total Unique Product IDs Loaded: %s", len(product_ids))


# -----------------------------
# DRIVER SETUP (VISIBLE)
# -----------------------------
def create_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    headless_mode = os.getenv("HEADLESS", "false").lower()
    if headless_mode in {"1", "true", "yes"}:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


def wait_until_page_stable(driver, timeout=20, check_interval=0.5):
    import time

    start_time = time.time()
    last_length = 0

    while time.time() - start_time < timeout:
        current_length = len(driver.page_source)

        if current_length == last_length:
            return True  # Page stabilized

        last_length = current_length
        time.sleep(check_interval)

    return False


# -----------------------------
# TEXT EXTRACTION HELPER
# -----------------------------
def extract_field(text, label):
    pattern = rf"{label}.*?:\s*(.+)"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


# -----------------------------
# SCRAPER
# -----------------------------
def scrape_products(product_ids):

    driver = create_driver()
    wait = WebDriverWait(driver, 20)
    results = []

    for idx, product_id in enumerate(product_ids, start=1):

        logger.info("[%s/%s] Scraping: %s", idx, len(product_ids), product_id)

        data = {
            "Product ID": product_id,
            "Extended Product Type": None,
            "Rated Current": None,
            "Product Main Type": None,
            "Electrical Durability": None,
            "Rated Insulation Voltage": None,
            "Rated Voltage": None,
            "Rated Impulse Withstand Voltage": None,
            "Rated Operational Voltage": None,
            "Number of Poles": None,
            "Rated Service Short-Circuit Breaking Capacity": None
        }

        try:
            url = f"https://new.abb.com/products/{product_id}"
            driver.get(url)

            # Wait until body loads
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Wait until page fully stabilizes (IMPORTANT FIX)
            wait_until_page_stable(driver, timeout=20)

            # Handle cookie popup
            try:
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if "reject" in btn.text.lower() or "accept" in btn.text.lower():
                        btn.click()
                        time.sleep(1)
                        break
            except:
                pass

            # Expand Technical section if present
            try:
                tech_sections = driver.find_elements(By.XPATH, "//*[contains(text(),'Technical')]")
                for sec in tech_sections:
                    if sec.is_displayed():
                        driver.execute_script("arguments[0].click();", sec)
                        time.sleep(1)
                        break
            except:
                pass

            # Final stabilization after expanding sections
            wait_until_page_stable(driver, timeout=15)

            body_text = driver.find_element(By.TAG_NAME, "body").text

            # Extract fields
            data["Extended Product Type"] = extract_field(body_text, "Extended Product Type")
            data["Rated Current"] = extract_field(body_text, "Rated Current")
            data["Product Main Type"] = extract_field(body_text, "Product Main Type")
            data["Electrical Durability"] = extract_field(body_text, "Electrical Durability")
            data["Rated Insulation Voltage"] = extract_field(body_text, "Rated Insulation Voltage")
            data["Rated Voltage"] = extract_field(body_text, "Rated Voltage")
            data["Rated Impulse Withstand Voltage"] = extract_field(body_text, "Rated Impulse Withstand Voltage")
            data["Rated Operational Voltage"] = extract_field(body_text, "Rated Operational Voltage")
            data["Number of Poles"] = extract_field(body_text, "Number of Poles")
            data["Rated Service Short-Circuit Breaking Capacity"] = extract_field(
                body_text, "Rated Service Short-Circuit Breaking Capacity"
            )

            logger.info("--------------------------------------------------")
            for k, v in data.items():
                if v:
                    logger.info("%s: %s", k, v)
            logger.info("--------------------------------------------------")

        except Exception as e:
            logger.error("Error scraping %s: %s", product_id, str(e))

        results.append(data)
        time.sleep(DELAY_SECONDS)

    driver.quit()
    return pd.DataFrame(results)


logger.info("Starting ABB Scraping...")

# 🔥 TEST FIRST
# product_ids = product_ids[:5]

abb_df = scrape_products(product_ids)


# -----------------------------
# PDF PRICE EXTRACTION
# -----------------------------

def extract_prices_from_pdf(pdf_path):

    # Universal ABB product pattern
    product_pattern = re.compile(r"\b[A-Z0-9]{6,}R\d+\b")

    # Numeric price pattern (e.g., 12,340)
    price_pattern = re.compile(r"\b\d{1,3}(?:,\d{3})+\b")

    # Upon Request pattern
    upon_pattern = re.compile(r"Upon Request", re.IGNORECASE)

    price_map = {}

    with pdfplumber.open(pdf_path) as pdf:

        for page_number, page in enumerate(pdf.pages, start=1):

            text = page.extract_text()
            if not text:
                continue

            # Extract in order of appearance
            products = product_pattern.findall(text)
            prices = price_pattern.findall(text)
            upon_requests = upon_pattern.findall(text)

            # Combine numeric prices + upon request
            combined_prices = prices + ["Upon Request"] * len(upon_requests)

            pair_count = min(len(products), len(combined_prices))

            for i in range(pair_count):

                product_id = products[i]
                price = combined_prices[i]

                # Prevent overwriting duplicates
                if product_id not in price_map:
                    price_map[product_id] = price

                    logger.info("%s", "-" * 50)
                    logger.info("Product ID: %s", product_id)
                    logger.info("Price: %s", price)
                    logger.info("Page: %s", page_number)

    logger.info("Total Unique Products with Price Found: %s", len(price_map))

    return pd.DataFrame(
        [{"Product ID": k, "Price": v} for k, v in price_map.items()]
    )


logger.info("Extracting Prices from PDF...")
price_df = extract_prices_from_pdf(pdf_path)
logger.info("Price DataFrame size: %s", price_df.size)

def count_products_on_price_pages(pdf_path):

    import re
    import pdfplumber

    product_pattern = re.compile(r"\b[A-Z0-9]{6,}R\d+\b")
    price_pattern = re.compile(r"\d{1,3}(?:,\d{3})+")

    total_products = set()

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            if price_pattern.search(text):  # Only pages with numeric prices
                products = product_pattern.findall(text)
                total_products.update(products)

    logger.info("Unique products on pages containing prices: %s", len(total_products))


# Run this once
count_products_on_price_pages(pdf_path)

final_df = pd.merge(abb_df, price_df, on="Product ID", how="left")
output_dir = os.getenv("OUTPUT_DIR", ".")
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "final_abb_products.csv")
final_df.to_csv(output_file, index=False)

logger.info("Final file saved as: %s", output_file)
logger.info("Process Completed Successfully")