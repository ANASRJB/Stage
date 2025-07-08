from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import glob 


# Configuration Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Mode sans interface
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

# Spécifiez le chemin du driver explicitement
service = Service('/usr/local/bin/chromedriver')

# Open all json files in the procedures directory 
fichiers = glob.glob('data/procedures/procedures_*.json')

tous_les_procedures=[]
# Read the content of each JSON file
try:
    for chemin in fichiers:
     with open(chemin, 'r', encoding='utf-8') as f:
        contenu = json.load(f)
        tous_les_procedures.extend(contenu)
        print(tous_les_procedures)
except Exception as e:
    print(f"Erreur lors de la lecture des fichiers JSON : {e}")
print(tous_les_procedures)
# Extract links from the loaded content
def links():
    links = []
    for a in tous_les_procedures:
        links.append(a['link'])
    return links

print(len(links()))
try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    l=links()
    for link in l:
        driver.get(link)
        
        # Attendre que la page se charge complètement
        wait = WebDriverWait(driver, 30)
        print(f"Loading URL: {link}")
    
        # Attendre un peu plus pour que le contenu se charge
        time.sleep(3)
        # les conditions de la procedure 
except Exception as e:
    print(f"Erreur lors de la connexion au driver : {e}")
