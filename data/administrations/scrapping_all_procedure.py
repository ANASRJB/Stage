from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time


# Configuration Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Mode sans interface
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

# Spécifiez le chemin du driver explicitement
service = Service('/usr/local/bin/chromedriver')

# Les liens des administrations 
with open('data/administrations/administrations.json', 'r') as file:

    admins = json.load(file)

links=[]
for a in admins:
    links.append(a['lien'])
L=links[75:]  
print(L[0])
#start scrapping procedures 
try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    for link in L:
        driver.get(link)
        
        # Attendre que la page se charge complètement
        wait = WebDriverWait(driver, 30)
        print(f"Loading URL: {link}")
        
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='__layout']/div/div[2]/div[8]/div/div/div[1]")))
        print("suscessfully loaded the page")
        # Attendre un peu plus pour que le contenu se charge
        time.sleep(3)
        
        
        # Collect all procedures
        procedures = []
        elements = driver.find_elements(By.CSS_SELECTOR, ".column.is-4.tile")
        
        for element in elements:
            administration_name = element.find_element(By.XPATH, "//*[@id='__layout']/div/div[2]/div[8]/div/div/div[1]/a/div[1]/div[1]/div/h4/strong").text.strip()
            title = element.find_element(By.CSS_SELECTOR, "span[data-v-f85cfe9c]").text.strip()
            
            link = element.find_element(By.TAG_NAME, "a").get_attribute("href")

            
            procedures.append({
                'title': title,
                'link': link,
                'administration': administration_name
            })
        
        # Save procedures to a JSON file named after the administration
        admin_name = link.split("/")[-1]  # Assuming the last part of the URL is
        # the administration name
        with open(f'data/procedures/procedures_{admin_name}.json','w',encoding="utf-8") as f:
            json.dump(procedures, f, ensure_ascii=False,indent=4)                                          


except Exception as e:
    print(f"Erreur: {e}")
    if 'driver' in locals():
        driver.quit()