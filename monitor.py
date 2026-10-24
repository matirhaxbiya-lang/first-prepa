import requests
from bs4 import BeautifulSoup
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USERNAME = os.environ.get("LOGIN")
PASSWORD = os.environ.get("PASSWORD")
PHONE = os.environ.get("PHONE")
API_KEY = os.environ.get("API_KEY")

LOGIN_URL = "https://firstprepa.com/"
NOTES_URL = "https://firstprepa.com/etudiant/notes.php"

def send_whatsapp(message):
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE}&text={message}&apikey={API_KEY}"
    try:
        requests.get(url)
        print("WhatsApp sent!")
    except Exception as e:
        print(f"Error: {e}")

def get_grades():
    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    login_data = {'nom_utilisateur': USERNAME, 'mot_de_passe': PASSWORD}
    session.post(LOGIN_URL, data=login_data, headers=headers, verify=False)
    notes_response = session.get(NOTES_URL, headers=headers, verify=False)
    
    if "Connexion" in notes_response.text:
        return None

    soup = BeautifulSoup(notes_response.text, 'html.parser')
    table = soup.find('table')
    if not table: return []

    grades = []
    for row in table.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) >= 7:
            grades.append({
                "trimestre": cols[0].text.strip(),
                "evaluation": cols[1].text.strip(),
                "enseignant": cols[2].text.strip(),
                "matiere": cols[3].text.strip(),
                "date": cols[4].text.strip(),
                "note": cols[5].text.strip(),
                "classement": cols[6].text.strip()
            })
    return grades

def main():
    current_grades = get_grades()
    if not current_grades: return

    message = "📊 *الجدول الحالي للنقط (تحديث كل ساعة):*\n\n"
    for grade in current_grades:
        if not grade['matiere']: continue
        message += f"📚 *المادة:* {grade['matiere']}\n📝 *الامتحان:* {grade['evaluation']}\n👨‍🏫 *الأستاذ:* {grade['enseignant']}\n📅 *التاريخ:* {grade['date']}\n💯 *النقطة:* {grade['note']}\n🏆 *الترتيب:* {grade['classement']}\n-------------------\n"

    send_whatsapp(message)

if __name__ == "__main__":
    main()
