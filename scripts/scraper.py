import os
import time
import random
import urllib.parse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def run_search(driver):
    # Seu prompt específico
    dork = 'site:linkedin.com/jobs/view ("Power BI" OR "SQL" OR "Data Analyst" OR "Analista de Dados" OR "Analytics") ("Remoto" OR "Remote") ("PJ" OR "Pessoa Jurídica" OR "Contrato" OR "Contract") ("Easy Apply" OR "Candidatura Simplificada" OR "Apply") -intitle:"promoted"'
    
    encoded_query = urllib.parse.quote(dork)
    url = f"https://www.google.com/search?q={encoded_query}"
    
    print(f"Buscando no Google: {url}")
    driver.get(url)
    time.sleep(random.uniform(5, 10))
    
    found_jobs = []
    results = driver.find_elements(By.CSS_SELECTOR, "div.g")

    for res in results:
        try:
            title = res.find_element(By.TAG_NAME, "h3").text
            link = res.find_element(By.TAG_NAME, "a").get_attribute("href")
            
            if "linkedin.com/jobs/view" in link:
                found_jobs.append({
                    "Data_Captura": pd.Timestamp.now().strftime("%d/%m/%Y"),
                    "Titulo": title,
                    "Link": link
                })
        except:
            continue
            
    return found_jobs

def save_results(jobs):
    os.makedirs('data', exist_ok=True)
    file_path = 'data/vagas.csv'
    
    df_new = pd.DataFrame(jobs)
    
    if os.path.exists(file_path):
        df_old = pd.read_csv(file_path)
        df_final = pd.concat([df_old, df_new]).drop_duplicates(subset=['Link'], keep='first')
    else:
        df_final = df_new
        
    df_final.to_csv(file_path, index=False)
    print(f"Base atualizada! Total de vagas: {len(df_final)}")

if __name__ == "__main__":
    driver = setup_browser()
    try:
        results = run_search(driver)
        if results:
            save_results(results)
        else:
            print("Nenhum resultado encontrado nesta rodada.")
    finally:
        driver.quit()