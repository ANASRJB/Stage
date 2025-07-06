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

try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://idaraty.tn/organisations")
    
    # Attendre que la page se charge complètement
    wait = WebDriverWait(driver, 30)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".column.tile.is-6-tablet.is-4-desktop.is-12-mobile")))
    # Attendre un peu plus pour que le contenu se charge
    time.sleep(3)
    
    # Function to scroll to bottom of page
    def scroll_to_bottom():
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
    # Function to get current number of elements
    def get_element_count():
        elements = driver.find_elements(By.CSS_SELECTOR, ".column.tile.is-6-tablet.is-4-desktop.is-12-mobile")
        return len(elements)
    
    # Function to click "Show more" button if available
    def click_show_more():
        try:
            show_more_button = driver.find_element(By.CSS_SELECTOR, ".button.is-default.is-medium")
            if show_more_button.is_enabled() and show_more_button.is_displayed():
                show_more_button.click()
                print("Bouton 'Afficher plus' cliqué.")
                time.sleep(2)
                return True
        except Exception as e:
            print(f"Pas de bouton 'Afficher plus' trouvé: {e}")
            return False
    
    # Function to handle login
    def handle_login():
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".modal.is-active")))
            print("Login modal detected. Attempting to login...")
            time.sleep(3)  # Attendre un peu pour que la modal se charge
            
            # Remplir les champs de connexion
            email_input = driver.find_element(By.XPATH, "//*[@id='__layout']/div/div[2]/div[2]/div/div/div/section/span/form/div[1]/div/div/input")
            password_input = driver.find_element(By.XPATH, "//*[@id='__layout']/div/div[2]/div[2]/div/div/div/section/span/form/div[2]/div/div/input")

            email_input.send_keys("anasrejeb02@gmail.com")  # Remplacez par votre nom d'utilisateur
            password_input.send_keys("Anasrjb2002")  # Remplacez par votre mot de passe
            
            # Cliquer sur le bouton de connexion
            login_button = driver.find_element(By.XPATH, "//*[@id='__layout']/div/div[2]/div[2]/div/div/div/section/span/form/div[3]/div/button")
            login_button.click()
            print("Tentative de connexion...")
            
            # Attendre que la modal disparaisse (indication que la connexion est réussie)
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal.is-active")))
            print("Connexion réussie.")
            
            # Attendre que la page soit stable après la connexion
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"Pas de modal de connexion ou erreur: {e}")
            return False
    
    # Function to load all content using scrolling and button clicking
    def load_all_content():
        initial_count = get_element_count()
        print(f"Nombre initial d'éléments: {initial_count}")
        
        max_iterations = 20  # Limite pour éviter les boucles infinies
        no_change_count = 0
        max_no_change = 3  # Arrêter après 3 tentatives sans changement
        
        for iteration in range(max_iterations):
            print(f"\n--- Iteration {iteration + 1} ---")
            
            # Essayer de cliquer sur le bouton "Afficher plus" d'abord
            button_clicked = click_show_more()
            
            if button_clicked:
                # Si le bouton a été cliqué, vérifier s'il y a une modal de connexion
                if handle_login():
                    # Après la connexion, essayer de cliquer à nouveau sur le bouton
                    time.sleep(2)
                    click_show_more()
            
            # Faire défiler vers le bas pour déclencher le chargement automatique
            scroll_to_bottom()
            
            # Attendre un peu pour que le contenu se charge
            time.sleep(3)
            
            # Vérifier le nouveau nombre d'éléments
            new_count = get_element_count()
            print(f"Nombre d'éléments après l'itération {iteration + 1}: {new_count}")
            
            # Si aucun nouveau contenu n'a été chargé
            if new_count == initial_count:
                no_change_count += 1
                print(f"Aucun nouveau contenu chargé ({no_change_count}/{max_no_change})")
                
                if no_change_count >= max_no_change:
                    print("Pas de nouveau contenu après plusieurs tentatives. Arrêt.")
                    break
            else:
                # Nouveau contenu trouvé, réinitialiser le compteur
                no_change_count = 0
                initial_count = new_count
                print(f"Nouveau contenu chargé! Total: {new_count}")
        
        return get_element_count()
    
    # Charger tout le contenu
    print("Début du chargement de tout le contenu...")
    final_count = load_all_content()
    print(f"\nChargement terminé. Total final: {final_count} éléments")
    
    # Attendre un peu plus pour s'assurer que tout est chargé
    time.sleep(3)
    
    # Trouver tous les éléments d'organisation
    elements = driver.find_elements(By.CSS_SELECTOR, ".column.tile.is-6-tablet.is-4-desktop.is-12-mobile")
    
    print(f"\nNombre final d'éléments trouvés: {len(elements)}")
    print("Page title:", driver.title)
    
    # Extraire les données de chaque élément
    organizations = []
    
    for i, element in enumerate(elements, 1):
        try:
            # Trouver le nom de l'organisation
            name_element = element.find_element(By.CSS_SELECTOR, "div.is-size-6.has-text-weight-semibold span")
            name = name_element.text.strip()
            
            # Trouver le lien
            link_element = element.find_element(By.CSS_SELECTOR, "a.card-org")
            link = link_element.get_attribute("href")
            
            # Trouver le nombre de procédures
            procedures_element = element.find_element(By.CSS_SELECTOR, "div.is-size-6.has-text-grey")
            procedures_text = procedures_element.text.strip()
            procedures_count = procedures_text.split()[0] if procedures_text else "0"
            
            # Trouver l'image
            try:
                img_element = element.find_element(By.CSS_SELECTOR, "img")
                image_url = img_element.get_attribute("src")
            except:
                image_url = "N/A"
            
            org_data = {
                'nom': name,
                'lien': link,
                'nombre_procedures': procedures_count,
                'image_url': image_url
            }
            
            organizations.append(org_data)
            
            print(f"{i}. {name} - {procedures_count} اجراءات")
            print(f"   Lien: {link}")
            print(f"   Image: {image_url}")
            print("-" * 50)
            
        except Exception as e:
            print(f"Erreur lors de l'extraction de l'élément {i}: {e}")
            continue
    
    print(f"\nTotal des organisations extraites: {len(organizations)}")
    
    # Sauvegarder dans un fichier (optionnel)
    with open('organizations.json', 'w', encoding='utf-8') as f:
        json.dump(organizations, f, ensure_ascii=False, indent=2)
    print("Données sauvegardées dans organizations.json")
    
    driver.quit()
    print("Test réussi!")
    
except Exception as e:
    print(f"Erreur: {e}")
    if 'driver' in locals():
        driver.quit()