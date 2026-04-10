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
    # Configurações cruciais para rodar no GitHub Actions
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # User-agent realista para evitar bloqueios
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
    
    # Esconde marcas de automação
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Script para limpar rastros do webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def run_search(driver, num_paginas=2):
    # Dork otimizada para capturar as vagas que você quer
    query = 'site:linkedin.com/jobs/view ("Power BI" OR "SQL" OR "Analista de Dados") "Remoto"'
    url_base = "https://www.google.com/search?q="
    
    todas_vagas = []
    
    for p in range(num_paginas):
        start = p * 10
        url_final = f"{url_base}{urllib.parse.quote(query)}&start={start}"
        print(f"Buscando página {p+1}...")
        
        driver.get(url_final)
        
        # Pausa longa para evitar captchas sem conta logada
        time.sleep(random.uniform(15, 25)) 
        
        if "google.com/sorry" in driver.current_url:
            print("❌ Bloqueio por Captcha detectado.")
            break

        elementos = driver.find_elements(By.CSS_SELECTOR, "div.g")
        for el in elementos:
            try:
                link = el.find_element(By.TAG_NAME, "a").get_attribute("href")
                if "linkedin.com/jobs/view" in link:
                    titulo = el.find_element(By.TAG_NAME, "h3").text
                    try:
                        resumo = el.find_element(By.CSS_SELECTOR, "div.VwiC3b").text
                    except:
                        resumo = "Resumo indisponível"
                    
                    # Formato solicitado
                    todas_vagas.append({
                        "Data_Busca": pd.Timestamp.now().strftime("%d/%m/%Y"),
                        "Vaga": titulo,
                        "Resumo": resumo,
                        "Link": link
                    })
            except:
                continue
                
    return todas_vagas

def save_data(jobs):
    if not jobs:
        print("Nenhuma vaga encontrada.")
        return
        
    os.makedirs('data', exist_ok=True)
    df_new = pd.DataFrame(jobs)
    path = 'data/vagas.csv'
    
    if os.path.exists(path):
        df_old = pd.read_csv(path)
        df_final = pd.concat([df_old, df_new]).drop_duplicates(subset=['Link'])
    else:
        df_final = df_new
        
    df_final.to_csv(path, index=False, encoding='utf-8-sig')
    print(f"✅ Dados salvos. Total: {len(df_final)} vagas.")

if __name__ == "__main__":
    browser = setup_browser()
    try:
        dados = run_search(browser, num_paginas=2)
        save_data(dados)
    finally:
        browser.quit()