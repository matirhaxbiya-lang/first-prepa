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
        res = requests.get(url, timeout=15)
        print(f"WhatsApp API Status: {res.status_code}")
        print("WhatsApp sent!")
    except Exception as e:
        print(f"WhatsApp Error: {e}")

def get_grades():
    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    print("1. جاري تحميل صفحة الدخول...")
    login_page = session.get(LOGIN_URL, headers=headers, verify=False, timeout=20)
    soup_login = BeautifulSoup(login_page.text, 'html.parser')

    # هنا حطينا الأسماء الصحيحة اللي كشفناها
    payload = {
        'LoginForm[username]': USERNAME, 
        'LoginForm[password]': PASSWORD,
        'LoginForm[rememberMe]': '0'
    }

    # كنجيبو الـ CSRF token (كود الأمان) ونضيفوه
    hidden_inputs = soup_login.find_all("input", type="hidden")
    for hidden in hidden_inputs:
        name = hidden.get('name')
        value = hidden.get('value')
        if name:
            payload[name] = value

    print("2. جاري تسجيل الدخول...")
    session.post(LOGIN_URL, data=payload, headers=headers, verify=False, timeout=20)

    print("3. جاري جلب صفحة النقط...")
    notes_response = session.get(NOTES_URL, headers=headers, verify=False, timeout=20)
    
    # نتأكدو واش مازال كيرجعنا لصفحة الدخول
    if 'id="login"' in notes_response.text:
        print("❌ فشل الاتصال! الموقع مازال كيرجعنا لصفحة الدخول.")
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
                "matiere": matiere,
                "evaluation": cols[1].text.strip(),
                "enseignant": cols[2].text.strip(),
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
        message += f"📚 *المادة:* {grade['matiere']}\n"
        message += f"📝 *الامتحان:* {grade['evaluation']}\n"
        message += f"👨‍🏫 *الأستاذ:* {grade['enseignant']}\n"
        message += f"📅 *التاريخ:* {grade['date']}\n"
        message += f"💯 *النقطة:* {grade['note']}\n"
        message += f"🏆 *الترتيب:* {grade['classement']}\n"
        message += "-------------------\n"

    send_whatsapp(message)

if __name__ == "__main__":
    main() 
