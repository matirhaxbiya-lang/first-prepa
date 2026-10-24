import os
import urllib3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USERNAME = os.environ.get("LOGIN")
PASSWORD = os.environ.get("PASSWORD")
PHONE = os.environ.get("PHONE")
API_KEY = os.environ.get("API_KEY")

LOGIN_URL = "https://www.firstprepa.com/cpge/index.php"
NOTES_URL = "https://www.firstprepa.com/cpge/index.php?r=evaluation/notation/admin&id_eleve=4046"

def send_whatsapp(message):
    url = f"https://api.textmebot.com/send.php?recipient={PHONE}&apikey={API_KEY}&text={message}"
    try:
        requests.get(url, timeout=15)
        print("WhatsApp sent successfully!")
    except Exception as e:
        print(f"WhatsApp Error: {e}")

def get_grades():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    print("1. Opening browser...")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("2. Loading login page...")
        driver.get(LOGIN_URL)
        time.sleep(2)

        print("3. Entering credentials...")
        username_input = driver.find_element(By.NAME, "LoginForm[username]")
        password_input = driver.find_element(By.NAME, "LoginForm[password]")
        
        username_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)
        
        submit_btn = driver.find_element(By.NAME, "yt0")
        submit_btn.click()
        
        time.sleep(3)

        print("4. Loading notes page...")
        driver.get(NOTES_URL)
        time.sleep(2)
        
        page_source = driver.page_source
        
        if 'id="login"' in page_source or "LoginForm" in page_source:
            print("ERROR: Still on login page. Site might be blocking GitHub.")
            driver.quit()
            return None

        soup = BeautifulSoup(page_source, 'html.parser')
        table = soup.find('table')
        
        if not table:
            print("ERROR: Table not found.")
            driver.quit()
            return []

        grades = []
        for row in table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 7:
                matiere = cols[3].text.strip()
                if not matiere: continue
                grades.append({
                    "matiere": matiere,
                    "evaluation": cols[1].text.strip(),
                    "enseignant": cols[2].text.strip(),
                    "date": cols[4].text.strip(),
                    "note": cols[5].text.strip(),
                    "classement": cols[6].text.strip()
                })
        
        print(f"SUCCESS: Found {len(grades)} rows.")
        driver.quit()
        return grades
        
    except Exception as e:
        print(f"ERROR during execution: {e}")
        driver.quit()
        return None

def main():
    print("Starting script...")
    current_grades = get_grades()
    
    if not current_grades: 
        print("No grades to send.")
        return 
    
    message = "FirstPrepa Grades:\n\n"
    for grade in current_grades:
        message += f"Matiere: {grade['matiere']}\n"
        message += f"Exam: {grade['evaluation']}\n"
        message += f"Note: {grade['note']}\n"
        message += f"Classement: {grade['classement']}\n"
        message += "-------------------\n"
    
    send_whatsapp(message)

if __name__ == "__main__":
    main()
