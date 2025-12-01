import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

import smtplib

load_dotenv()

class EmailManager:
    def __init__(self, **kwargs):
        self.__session = kwargs.get('session', 'smtp.gmail.com')
        self.__port = kwargs.get('port', 587)
        # self.user_email = kwargs.get("user_email", None) maya nato
        self.__sender_email = os.getenv("USER_EMAIL")
        self.__sender_password = os.getenv("APP_PASSWORD")
        self.__receiver_email = "carljohannesllarenas.munoz24@bicol-u.edu.ph"
        self.__message = None

    def create_message(self, text):
        self.__message = MIMEText(text, "plain")

        self.__message["Subject"] = "Geofence Breached"
        self.__message["From"] = self.__sender_email
        self.__message["To"] = self.__receiver_email

    def send_alert_email(self):
        with smtplib.SMTP(self.__session, self.__port) as server:
            server.starttls()
            server.login(self.__sender_email, self.__sender_password)
            server.sendmail(self.__sender_email, self.__receiver_email, self.__message.as_string())
            print("Sent")
            server.quit()