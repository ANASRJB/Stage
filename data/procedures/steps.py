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
fichiers.sort()  
tous_les_procedures=[]
liens=[]
# Function to extract links from a list of dictionaries
def get_link(L):
    links = []
    for a in L:
        links.append(a['link'])
    return links
# Read the content of each JSON file
try:
    for chemin in fichiers:
        with open(chemin, 'r+', encoding='utf-8') as f:
           contenu = json.load(f)
        tous_les_procedures.extend(contenu)
        nb=len(tous_les_procedures)
        liens = get_link(tous_les_procedures)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        for link in liens:
            driver.get(link)
            
            # Attendre que la page se charge complètement
            wait = WebDriverWait(driver, 30)
            print(f"Loading URL: {link}")
            wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='__layout']/div/div[2]/div[4]/div[1]/div/div[2]/div[2]/div/div")))
            print("successfully loaded the page")
            # Attendre un peu plus pour que le contenu se charge
            time.sleep(3)
            
            
            try:
                # Les conditions
                conditions={}
                list_cond=[]
                l=[]
                elements = driver.find_elements(By.XPATH, "//*[@id='__layout']/div/div[2]/div[4]/div[1]/div/div[2]/div[2]/div/div")
                for element in elements:
                    list_cond = element.find_elements(By.CSS_SELECTOR, ".media-content span")
                for cond  in list_cond:
                    if cond.text.strip() != "":
                        l.append(cond.text.strip())
                print(f"Conditions found: {l}")
                for i in range(len(l)):
                    conditions[str(i)] = l[i]
                        
                for i in contenu:
                    if i['link'] == link:
                        i['conditions'] = conditions
                        print(f"Conditions added to procedure: {i['title']}")
            
                nb-=1
                if nb==0:
                   with open(chemin,'w',encoding="utf-8") as f:
                       json.dump(contenu, f, ensure_ascii=False,indent=4)   
            except Exception as e:
                print(f"Erreur lors de collection : {e}")
            
except Exception as e:
    print(f"Erreur lors de la lecture des fichiers JSON : {e}")