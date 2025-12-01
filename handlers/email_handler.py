import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()


class EmailManager:
    def __init__(self):
        self.__sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.__sender_email = os.getenv("SENDER_EMAIL")
        self.__receiver_email = "carljohannesllarenas.munoz24@bicol-u.edu.ph"
        self.__message_text = None

        # Validate credentials
        if not self.__sendgrid_api_key:
            raise ValueError("SENDGRID_API_KEY must be set in environment variables")
        if not self.__sender_email:
            raise ValueError("SENDER_EMAIL must be set in environment variables")

    def create_message(self, text):
        """Create email message"""
        self.__message_text = text

    def send_alert_email(self):
        """Send email using SendGrid API"""
        if not self.__message_text:
            raise ValueError("No message created. Call create_message() first.")

        try:
            message = Mail(
                from_email=self.__sender_email,
                to_emails=self.__receiver_email,
                subject="🚨 Geofence Alert",
                plain_text_content=self.__message_text
            )

            sg = SendGridAPIClient(self.__sendgrid_api_key)
            response = sg.send(message)

            print(f"✓ Email sent successfully to {self.__receiver_email}")
            print(f"Status code: {response.status_code}")
            return True

        except Exception as e:
            print(f"✗ Failed to send email: {type(e).__name__}: {e}")
            # Don't raise - let the app continue even if email fails
            return False