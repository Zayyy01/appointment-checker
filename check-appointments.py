import requests
import smtplib
import os
from bs4 import BeautifulSoup
from datetime import datetime
from email.message import EmailMessage

# Get variables
email = os.getenv('EMAIL')
email_pwd = os.getenv('EMAIL_PASSWORD')
target_date_string = os.getenv('TARGET_DATE')
target_date = datetime.strptime(target_date_string, '%Y.%m.%d')
url = os.getenv('URL')
doctor = os.getenv('DOCTOR')
appointment_type = os.getenv('TYPE')
description = os.getenv('DESCRIPTION')

payload = {
    "orvos": doctor,
    "rendeles": appointment_type,
    "vizsgalatnev": description,
    "orvosrendeles": "24",
    "szakrendeles": "",
    "intervallum": "30",
    "vizsgalat": "73",
    "step": "3"
}

def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = email
    msg['To'] = email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email, email_pwd)
        smtp.send_message(msg)
        print('Email has been sent successfully.')

def main():
    response = requests.post(url, data=payload)
    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, 'html.parser')
    date_divs = soup.find_all('div', class_='datum')

    earlier_dates = []
    for div in date_divs:
        try:
            date_text = div.get_text(strip=True)
            date_obj = datetime.strptime(date_text, '%Y.%m.%d')
            if date_obj < target_date:
                earlier_dates.append(date_text)
        except ValueError:
            continue

    if earlier_dates:
        print(f"Earlier dates found: {earlier_dates}")
        send_email(
            subject='Earlier Appointment Found!',
            body=f'The following dates were found earlier than {target_date_string}: {", ".join(earlier_dates)}.\r\nApply here: {url}'
        )
    else:
        print("No earlier dates found.")
    print('Done.')

if __name__ == '__main__':
    main()
