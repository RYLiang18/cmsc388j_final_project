import requests
from flask_mail import Mail, Message
from datetime import datetime


holiday_key = "ce3b6b2d-f653-4206-b961-4953877aec55"

def send_mail(recipient, message, subject=None):
    mail = Mail()
    msg = Message(subject, recipients=[recipient])
    msg.body = message
    mail.send(msg)

def get_holiday():
    country = "US"
    now = datetime.now()
    year = "2020"
    day = now.day
    month = now.month
    params= {
    "country":country,
    "key":holiday_key,
    "year":year,
    "month":month,
    "day":day
    }
    resp = requests.get("https://holidayapi.com/v1/holidays", params=params)
    holidays = resp.json()["holidays"]
    if len(holidays) == 0:
        return None

    return holidays[0]["name"]

if __name__ == "__main__":

    print(get_holiday())
