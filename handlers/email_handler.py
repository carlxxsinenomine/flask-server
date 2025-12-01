import os
from email.mime.text import MIMEText
from dotenv import load_dotenv
import smtplib
import socket

load_dotenv()


class EmailManager:
    def __init__(self, **kwargs):
        self.__session = kwargs.get('session', 'smtp.gmail.com')
        self.__port = kwargs.get('port', 587)
        self.__sender_email = os.getenv("USER_EMAIL")
        self.__sender_password = os.getenv("APP_PASSWORD")
        self.__receiver_email = "carljohannesllarenas.munoz24@bicol-u.edu.ph"
        self.__message = None

        # Validate credentials
        if not self.__sender_email or not self.__sender_password:
            raise ValueError("USER_EMAIL and APP_PASSWORD must be set in environment variables")

    def create_message(self, text):
        self.__message = MIMEText(text, "plain")
        self.__message["Subject"] = "Geofence Breached"
        self.__message["From"] = self.__sender_email
        self.__message["To"] = self.__receiver_email

    def send_alert_email(self):
        if not self.__message:
            raise ValueError("No message created. Call create_message() first.")

        try:
            # Set a timeout to prevent hanging
            with smtplib.SMTP(self.__session, self.__port, timeout=10) as server:
                server.starttls()
                server.login(self.__sender_email, self.__sender_password)
                server.sendmail(
                    self.__sender_email,
                    self.__receiver_email,
                    self.__message.as_string()
                )
                print(f"✓ Email sent successfully to {self.__receiver_email}")
                return True

        except smtplib.SMTPAuthenticationError:
            print("✗ SMTP Authentication failed. Check USER_EMAIL and APP_PASSWORD")
            raise
        except socket.timeout:
            print("✗ Email sending timed out")
            raise
        except Exception as e:
            print(f"✗ Failed to send email: {type(e).__name__}: {e}")
            raise