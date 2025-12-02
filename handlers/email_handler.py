import os
from email.mime.text import MIMEText
from dotenv import load_dotenv
import smtplib

load_dotenv()


class EmailManager:
    def __init__(self):
        # Mailtrap SMTP settings
        self.__session = os.getenv("MAILTRAP_HOST", "live.smtp.mailtrap.io")
        self.__port = int(os.getenv("MAILTRAP_PORT", 587))
        self.__username = os.getenv("MAILTRAP_USERNAME")
        self.__password = os.getenv("MAILTRAP_PASSWORD")

        # Email settings
        self.__sender_email = os.getenv("SENDER_EMAIL", "noreply@demomailtrap.co")
        self.__receiver_email = "carljohannesllarenas.munoz24@bicol-u.edu.ph"
        self.__message = None

        # Validate credentials
        if not self.__username or not self.__password:
            raise ValueError("MAILTRAP_USERNAME and MAILTRAP_PASSWORD must be set in environment variables")

    def create_message(self, text):
        """Create email message"""
        self.__message = MIMEText(text, "plain")
        self.__message["Subject"] = "🚨 Geofence Alert"
        self.__message["From"] = self.__sender_email
        self.__message["To"] = self.__receiver_email

    def send_alert_email(self):
        """Send email using Mailtrap SMTP"""
        if not self.__message:
            raise ValueError("No message created. Call create_message() first.")

        try:
            with smtplib.SMTP(self.__session, self.__port, timeout=10) as server:
                server.starttls()
                server.login(self.__username, self.__password)
                server.sendmail(
                    self.__sender_email,
                    self.__receiver_email,
                    self.__message.as_string()
                )
                print(f"✓ Email sent successfully to {self.__receiver_email}")
                return True

        except smtplib.SMTPAuthenticationError as e:
            print(f"✗ SMTP Authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            print(f"✗ SMTP error: {e}")
            return False
        except Exception as e:
            print(f"✗ Failed to send email: {type(e).__name__}: {e}")
            return False