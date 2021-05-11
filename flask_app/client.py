import requests
from flask_mail import Mail, Message
from datetime import datetime

import pprint
pp = pprint.PrettyPrinter(indent=2)

holiday_key = "AIzaSyBVuarosmaHKCYrTSJ7DAOZSQ5eA5At1Ws"

def send_mail(recipient, message, subject=None):
    mail = Mail()
    msg = Message(subject, recipients=[recipient])
    msg.body = message
    mail.send(msg)

def get_holiday():
    now = datetime.now()
    year = now.year
    day = now.day
    month = now.month
    
    params2 = {
        "key": holiday_key
    }

    api_link = "https://www.googleapis.com/calendar/v3/calendars/en.usa%23holiday%40group.v.calendar.google.com/events?"

    resp = requests.get(api_link, params=params2)
    all_holidays = resp.json()["items"]
    
    def is_today(holiday):
        dt = datetime.strptime(holiday['start']['date'], '%Y-%m-%d')
        return dt.year == year and dt.month == month and dt.day == day
    
    today_holidays = list(filter(lambda x : is_today(x), all_holidays))
    # pp.pprint(today_holidays)
    if len(today_holidays) == 0:
        return None

    return today_holidays[0]["summary"]

if __name__ == "__main__":

    print(get_holiday())
