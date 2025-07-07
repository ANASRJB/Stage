from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# Configuration Chrome
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Disabled for debugging
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

service = Service('/usr/local/bin/chromedriver')

try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Test URL
    url = "https://idaraty.tn/organisations/ministere-de-lindustrie-et-des-petites-et-moyennes-entreprises"
    
    print(f"1. Loading URL: {url}")
    driver.get(url)
    
    print(f"2. Page title: {driver.title}")
    print(f"3. Current URL: {driver.current_url}")
    
    # Wait for page to load
    print("4. Waiting for page to load...")
    time.sleep(10)
    
    # Check if page loaded
    print("5. Looking for any content...")
    
    # Try to find any element
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        print(f"   Body found with {len(body.text)} characters")
    except:
        print("   No body found")
    
    # Look for different selectors
    selectors = [
        "div",
        ".column",
        ".tile", 
        "a",
        "[class*='column']",
        "[class*='tile']",
        ".procedure",
        ".service"
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"   Found {len(elements)} elements with '{selector}'")
        except Exception as e:
            print(f"   Error with '{selector}': {e}")
    
    # Check page source
    page_source = driver.page_source
    print(f"6. Page source length: {len(page_source)}")
    
    # Look for key content
    if "procedure" in page_source.lower():
        print("   ✓ Found 'procedure' in page")
    if "service" in page_source.lower():
        print("   ✓ Found 'service' in page")
    if "ministere" in page_source.lower():
        print("   ✓ Found 'ministere' in page")
    
    # Save first 2000 characters of page source
    print("\n7. First 2000 characters of page:")
    print(page_source[:2000])
    
    input("Press Enter to close browser...")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'driver' in locals():
        driver.quit()