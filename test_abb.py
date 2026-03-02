import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

print("Starting test...")

options = Options()
driver = webdriver.Chrome(options=options)

product_id = "1SDA073323R1"
url = f"https://new.abb.com/products/{product_id}"

print("Opening:", url)
driver.get(url)

time.sleep(5)

print("Page title:", driver.title)

# Try clicking the specifications tab
try:
    tabs = driver.find_elements(By.XPATH, "//button | //a")
    for tab in tabs:
        text = tab.text.lower()
        if "technical" in text or "specification" in text:
            print("Clicking tab:", tab.text)
            tab.click()
            break
except:
    print("No tab found")

time.sleep(5)

# Now extract all label-value pairs
elements = driver.find_elements(By.XPATH, "//div[contains(@class,'row')]")

print("Elements found:", len(elements))

for el in elements[:20]:
    print(el.text)

driver.quit()
print("Test finished.")
