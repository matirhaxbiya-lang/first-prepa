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
    url = f"https://api.textmebot.com/send.php?recipient={PHONE}&apikey={API_KEY}&text={message}"
    try:
        print("جاري إرسال الواتساب...")
        res = requests.get(url, timeout=15)
        print(f"WhatsApp API Status: {res.status_code}")
        print("WhatsApp sent!")
    except Exception as e:
        print(f"WhatsApp Error: {e}")

def get_grades():
    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    print("1. جاري تسجيل الدخول...")
    login_data = {'nom_utilisateur': USERNAME, 'mot_de_passe': PASSWORD}
    try:
        response = session.post(LOGIN_URL, data=login_data, headers=headers, verify=False, timeout=20)
        print(f"Login Status Code: {response.status_code}")
    except Exception as e:
        print(f"Login Error: {e}")
        return None

    print("2. جاري جلب صفحة النقط...")
    try:
        notes_response = session.get(NOTES_URL, headers=headers, verify=False, timeout=20)
        print(f"Notes Page Status Code: {notes_response.status_code}")
    except Exception as e:
        print(f"Notes Error: {e}")
        return None
    
    if "Connexion" in notes_response.text and "Mot de passe" in notes_response.text:
        print("❌ فشل الاتصال! الموقع مارضاش يقبل الدخول (يمكن الباسورد غالط ولا الموقع كيبلوكي GitHub).")
        return None

    soup = BeautifulSoup(notes_response.text, 'html.parser')
    table = soup.find('table')
    
    if not table:
        print("❌ مالقيتش الجدول فالصفحة! يمكن الرابط ديال النقط ماشي هو هادا.")
        return []

    grades = []
    for row in table.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) >= 7:
            matiere = cols[3].text.strip()
            if not matiere: continue
            grades.append({
                "trimestre": cols[0].text.strip(),
                "evaluation": cols[1].text.strip(),
                "enseignant": cols[2].text.strip(),
                "matiere": matiere,
                "date": cols[4].text.strip(),
                "note": cols[5].text.strip(),
                "classement": cols[6].text.strip()
            })
    print(f"✅ تلقينا {len(grades)} ديال السطور من الجدول.")
    return grades

def main():
    print("بدا الفحص...")
    current_grades = get_grades()
    
    if not current_grades:
        print("ماكاين حتى شي معلومات باش نصيفطو.")
        return 

    message = "📊 *الجدول الحالي للنقط:*\n\n"
    for grade in current_grades:
        message += f"📚 *المادة:* {grade['matiere']}\n📝 *الامتحان:* {grade['evaluation']}\n👨‍🏫 *الأستاذ:* {grade['enseignant']}\n📅 *التاريخ:* {grade['date']}\n💯 *النقطة:* {grade['note']}\n🏆 *الترتيب:* {grade['classement']}\n-------------------\n"

    send_whatsapp(message)

if __name__ == "__main__":
    main()
