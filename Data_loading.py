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
chrome_options.add_argument("--window-size=1920,1080")

# Spécifiez le chemin du driver explicitement
service = Service('/usr/local/bin/chromedriver')

# Open all json files in the procedures directory
fichiers = glob.glob('data/procedures/procedures_*.json')

tous_les_procedures = []
liens = []

# Function to extract links from a list of dictionaries
def get_link(L):
    links = []
    for a in L:
        links.append(a['link'])
    return links

def extract_conditions(driver):
    """
    Fonction pour extraire les conditions depuis les spans
    """
    conditions = []
    
    # Différents sélecteurs possibles basés sur votre HTML
    selectors = [
        # Sélecteur principal pour les conditions
        "div[data-v-070cae60][data-v-a437adb8][class*='media-content'] span",
        "div[data-v-070cae60] span[data-v-070cae60]",
        "span[data-v-070cae60][data-v-a437adb8]",
        
        # Sélecteurs alternatifs
        "div[class*='media-content'] span",
        "div[class*='card-content'] span",
        
        # Sélecteur spécifique pour les conditions (basé sur votre capture)
        "div[data-v-070cae60][data-v-a437adb8][class*='media'] span",
        
        # Sélecteur très spécifique pour le conteneur des conditions
        "#__layout > div > div:nth-child(2) > div:nth-child(4) > div:nth-child(1) > div > div:nth-child(2) > div:nth-child(2) span"
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"Sélecteur '{selector}': {len(elements)} éléments trouvés")
            
            for element in elements:
                text = element.text.strip()
                if text and len(text) > 5:  # Ignorer les textes trop courts
                    conditions.append(text)
                    print(f"  - Condition trouvée: {text}")
            
            # Si des conditions sont trouvées, arrêter la recherche
            if conditions:
                break
                
        except Exception as e:
            print(f"Erreur avec le sélecteur {selector}: {e}")
    
    # Si aucune condition n'est trouvée, essayer une approche différente
    if not conditions:
        print("Tentative de recherche par contenu...")
        try:
            # Rechercher tous les spans contenant du texte arabe
            all_spans = driver.find_elements(By.TAG_NAME, "span")
            
            for span in all_spans:
                text = span.text.strip()
                # Vérifier si le texte contient des mots-clés arabes typiques des conditions
                if any(keyword in text for keyword in ["زوجين", "أن يكونا", "لزم", "الشروط", "يجب"]):
                    if text not in conditions and len(text) > 10:
                        conditions.append(text)
                        print(f"  - Condition par recherche textuelle: {text}")
                        
        except Exception as e:
            print(f"Erreur lors de la recherche textuelle: {e}")
    
    return conditions

def extract_conditions_from_container(driver):
    """
    Fonction alternative pour extraire depuis le conteneur spécifique
    """
    conditions = []
    
    try:
        # Utiliser le XPath exact de votre code mais corrigé
        container_xpath = "//*[@id='__layout']/div/div[2]/div[4]/div[1]/div/div[2]/div[2]"
        container = driver.find_element(By.XPATH, container_xpath)
        
        # Chercher tous les spans dans ce conteneur
        spans = container.find_elements(By.TAG_NAME, "span")
        
        for span in spans:
            text = span.text.strip()
            if text and len(text) > 5:
                conditions.append(text)
                print(f"  - Condition du conteneur: {text}")
                
    except Exception as e:
        print(f"Erreur lors de l'extraction depuis le conteneur: {e}")
    
    return conditions

# Initialiser le driver une seule fois
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Read the content of each JSON file
    for chemin in fichiers:
        with open(chemin, 'r', encoding='utf-8') as f:
            contenu = json.load(f)
            tous_les_procedures.extend(contenu)
            print(f"Total procedures: {len(tous_les_procedures)}")
    
    # Extraire tous les liens
    liens = get_link(tous_les_procedures)
    print(f"Total liens à traiter: {len(liens)}")
    
    # Traiter chaque lien
    for i, link in enumerate(liens, 1):
        print(f"\n[{i}/{len(liens)}] Traitement de: {link}")
        
        try:
            driver.get(link)
            
            # Attendre que la page se charge complètement
            wait = WebDriverWait(driver, 30)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Attendre un peu plus pour que le contenu se charge
            time.sleep(3)
            
            # Extraire les conditions - méthode 1
            print("=== Méthode 1: Sélecteurs CSS ===")
            conditions1 = extract_conditions(driver)
            
            # Extraire les conditions - méthode 2
            print("=== Méthode 2: Conteneur spécifique ===")
            conditions2 = extract_conditions_from_container(driver)
            
            # Combiner les résultats
            all_conditions = list(set(conditions1 + conditions2))
            
            print(f"=== RÉSULTATS FINAUX pour {link} ===")
            if all_conditions:
                for j, condition in enumerate(all_conditions, 1):
                    print(f"{j}. {condition}")
                    
                # Sauvegarder les conditions pour cette URL
                result = {
                    "url": link,
                    "conditions": all_conditions,
                    "timestamp": time.time()
                }
                
                # Sauvegarder dans un fichier JSON
                with open(f'conditions_{i}.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                    
            else:
                print("Aucune condition trouvée pour cette URL")
                
        except Exception as e:
            print(f"Erreur lors du traitement de {link}: {e}")
            continue

except Exception as e:
    print(f"Erreur générale: {e}")

finally:
    # Fermer le driver
    driver.quit()
    print("\nScraping terminé!")