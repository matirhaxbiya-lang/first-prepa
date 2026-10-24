import requests
from bs4 import BeautifulSoup
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USERNAME = os.environ.get("LOGIN")
PASSWORD = os.environ.get("PASSWORD")
PHONE = os.environ.get("PHONE")
API_KEY = os.environ.get("API_KEY")

# تحديث الروابط بناءً على المعلومات الجديدة
LOGIN_URL = "https://www.firstprepa.com/cpge/index.php"
NOTES_URL = "https://www.firstprepa.com/cpge/index.php?r=evaluation/notation/admin&id_eleve=4046"

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
        # تسجيل الدخول
        session.post(LOGIN_URL, data=login_data, headers=headers, verify=False, timeout=20)
        print("تم إرسال طلب تسجيل الدخول.")
    except Exception as e:
        print(f"Login Error: {e}")
        return None

    print("2. جاري جلب صفحة النقط...")
    try:
        # استخدام الرابط الجديد لجلب صفحة النقط
        notes_response = session.get(NOTES_URL, headers=headers, verify=False, timeout=20)
        print(f"Notes Page Status Code: {notes_response.status_code}")
    except Exception as e:
        print(f"Notes Error: {e}")
        return None
    
    # التحقق مما إذا كنا قد تمت إعادتنا إلى صفحة تسجيل الدخول
    if "Connexion" in notes_response.text and "Mot de passe" in notes_response.text:
        print("❌ فشل الاتصال! الموقع أعادنا إلى صفحة تسجيل الدخول. تأكد من صحة بيانات الدخول.")
        return None

    soup = BeautifulSoup(notes_response.text, 'html.parser')
    # البحث عن الجدول
    table = soup.find('table')
    
    if not table:
        print("❌ لم يتم العثور على الجدول في الصفحة! قد يكون الرابط خاطئًا أو أن هيكل الصفحة قد تغير.")
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
    print(f"✅ تم العثور على {len(grades)} صفًا في الجدول.")
    return grades

def main():
    print("بدء الفحص...")
    current_grades = get_grades()
    
    if not current_grades:
        print("لا توجد معلومات لإرسالها.")
        return 

    message = "📊 *الجدول الحالي للنقط:*\n\n"
    for grade in current_grades:
        message += f"📚 *المادة:* {grade['matiere']}\n📝 *الامتحان:* {grade['evaluation']}\n👨‍🏫 *الأستاذ:* {grade['enseignant']}\n📅 *التاريخ:* {grade['date']}\n💯 *النقطة:* {grade['note']}\n🏆 *الترتيب:* {grade['classement']}\n-------------------\n"

    send_whatsapp(message)

if __name__ == "__main__":
    main()
