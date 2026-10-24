import requests
from bs4 import BeautifulSoup
import os
import urllib3

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
        print("WhatsApp sent!")
    except Exception as e:
        print(f"WhatsApp Error: {e}")

def get_grades():
    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    print("1. جاري تسجيل الدخول...")
    login_data = {'nom_utilisateur': USERNAME, 'mot_de_passe': PASSWORD}
    session.post(LOGIN_URL, data=login_data, headers=headers, verify=False, timeout=20)

    print("2. جاري جلب صفحة النقط...")
    notes_response = session.get(NOTES_URL, headers=headers, verify=False, timeout=20)
    print(f"Notes Page Status Code: {notes_response.status_code}")
    
    soup = BeautifulSoup(notes_response.text, 'html.parser')
    
    # --- سطور جديدة باش نشوفو شنو كاين فالصفحة ---
    print("--- بداية كود الصفحة ---")
    print(notes_response.text[:500]) # كيطبع أول 500 حرف من الصفحة
    print("--- نهاية كود الصفحة ---")
    # ---------------------------------------------

    table = soup.find('table')
    
    if not table:
        print("❌ مالقيتش الجدول فالصفحة!")
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
    return grades

def main():
    current_grades = get_grades()
    if not current_grades:
        return 
    message = "📊 *الجدول الحالي للنقط:*\n\n"
    for grade in current_grades:
        message += f"📚 *المادة:* {grade['matiere']}\n💯 *النقطة:* {grade['note']}\n🏆 *الترتيب:* {grade['classement']}\n---\n"
    send_whatsapp(message)

if __name__ == "__main__":
    main()
