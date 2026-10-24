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
    
    print("1. جاري تحميل صفحة الدخول...")
    login_page = session.get(LOGIN_URL, headers=headers, verify=False, timeout=20)
    soup_login = BeautifulSoup(login_page.text, 'html.parser')

    # --- هاد الجزء باش نكشفو أسماء الخانات ---
    print("--- حقول الإدخال الموجودة في صفحة الدخول ---")
    for inp in soup_login.find_all('input'):
        print(f"Name: {inp.get('name')} | Type: {inp.get('type')}")
    print("---------------------------------------------")
    # ------------------------------------------

    payload = {
        'nom_utilisateur': USERNAME, # هادي مؤقتة
        'mot_de_passe': PASSWORD     # هادي مؤقتة
    }

    hidden_inputs = soup_login.find_all("input", type="hidden")
    for hidden in hidden_inputs:
        name = hidden.get('name')
        value = hidden.get('value')
        if name:
            payload[name] = value

    print("2. جاري تسجيل الدخول (محاولة)...")
    session.post(LOGIN_URL, data=payload, headers=headers, verify=False, timeout=20)

    print("3. جاري جلب صفحة النقط...")
    notes_response = session.get(NOTES_URL, headers=headers, verify=False, timeout=20)
    
    if 'id="login"' in notes_response.text:
        print("❌ فشل الاتصال! (طبيعي حيت مازال ما صلحناش الأسماء).")
        return None

    # (باقي الكود ديال قراءة الجدول وصيفط الواتساب)
    soup = BeautifulSoup(notes_response.text, 'html.parser')
    table = soup.find('table')
    if not table: return []
    
    grades = []
    for row in table.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) >= 7:
            if not cols[3].text.strip(): continue
            grades.append({"matiere": cols[3].text.strip(), "note": cols[5].text.strip(), "classement": cols[6].text.strip()})
    return grades

def main():
    current_grades = get_grades()
    if not current_grades: return 
    message = "📊 *الجدول الحالي للنقط:*\n\n"
    for grade in current_grades:
        message += f"📚 {grade['matiere']} | 💯 {grade['note']} | 🏆 {grade['classement']}\n"
    send_whatsapp(message)

if __name__ == "__main__":
    main()
