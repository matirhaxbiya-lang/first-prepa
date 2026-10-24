import requests
from bs4 import BeautifulSoup
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USERNAME = os.environ.get("LOGIN")
PASSWORD = os.environ.get("PASSWORD")
PHONE = os.environ.get("PHONE")
API_KEY = os.environ.get("API_KEY")

# هنا حطينا رابط الدخول الصحيح ديال Yii
LOGIN_URL = "https://www.firstprepa.com/cpge/index.php?r=site/login"
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
    
    # هنا زدنا معلومات المتصفح باش الموقع ما يشكش فيها
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': LOGIN_URL,
        'Origin': 'https://www.firstprepa.com'
    }
    
    print("1. جاري تحميل صفحة الدخول...")
    login_page = session.get(LOGIN_URL, headers=headers, verify=False, timeout=20)
    soup_login = BeautifulSoup(login_page.text, 'html.parser')

    payload = {
        'LoginForm[username]': USERNAME, 
        'LoginForm[password]': PASSWORD,
        'LoginForm[rememberMe]': '0'
    }

    hidden_inputs = soup_login.find_all("input", type="hidden")
    for hidden in hidden_inputs:
        name = hidden.get('name')
        value = hidden.get('value')
        if name:
            payload[name] = value

    print("2. جاري تسجيل الدخول...")
    # كنصيفطو الطلب لرابط الدخول الصحيح
    session.post(LOGIN_URL, data=payload, headers=headers, verify=False, timeout=20)

    print("3. جاري جلب صفحة النقط...")
    notes_response = session.get(NOTES_URL, headers=headers, verify=False, timeout=20)
    
    if 'id="login"' in notes_response.text or 'LoginForm' in notes_response.text:
        print("❌ فشل الاتصال! الموقع مازال كيرجعنا لصفحة الدخول.")
        print("💡 السبب: الموقع كيحظر السيرفرات ديال GitHub.")
        return None

    soup = BeautifulSoup(notes_response.text, 'html.parser')
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
    print(f"✅ تلقينا {len(grades)} ديال السطور.")
    return grades

def main():
    current_grades = get_grades()
    if not current_grades: return 
    
    message = "📊 *النقط ديالك:*\n\n"
    for grade in current_grades:
        message += f"📚 {grade['matiere']} | 💯 {grade['note']} | 🏆 {grade['classement']}\n"
    
    send_whatsapp(message)

if __name__ == "__main__":
    main()
