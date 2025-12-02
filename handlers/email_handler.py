import os
from dotenv import load_dotenv
import mailtrap as mt

load_dotenv()


class EmailManager:
    def __init__(self):
        # Mailtrap API settings
        self.__api_token = os.getenv("MAILTRAP_API_TOKEN")

        # Email settings
        self.__sender_email = os.getenv("SENDER_EMAIL", "hello@demomailtrap.com")
        self.__sender_name = os.getenv("SENDER_NAME", "Geofence Alert System")
        self.__receiver_email = "carljohannesllarenas.munoz24@bicol-u.edu.ph"
        self.__message_text = None

        # DEBUG: Print configuration (remove in production)
        print(f"DEBUG: API Token exists: {bool(self.__api_token)}")
        print(f"DEBUG: Sender Email: {self.__sender_email}")
        print(f"DEBUG: Receiver Email: {self.__receiver_email}")

        # Validate credentials
        if not self.__api_token:
            raise ValueError("MAILTRAP_API_TOKEN must be set in environment variables")

        # Initialize Mailtrap client
        self.__client = mt.MailtrapClient(token=self.__api_token)

    def create_message(self, text):
        """Create email message"""
        self.__message_text = text

    def send_alert_email(self):
        """Send email using Mailtrap API"""
        if not self.__message_text:
            raise ValueError("No message created. Call create_message() first.")

        try:
            # Create mail object
            mail = mt.Mail(
                sender=mt.Address(email=self.__sender_email, name=self.__sender_name),
                to=[mt.Address(email=self.__receiver_email)],
                subject="🚨 Geofence Alert",
                text=self.__message_text,
                category="Geofence Alerts"
            )

            print(f"DEBUG: Attempting to send email...")

            # Send email
            response = self.__client.send(mail)

            print(f"✓ Email sent successfully to {self.__receiver_email}")
            print(f"Response: {response}")
            return True

        except Exception as e:
            print(f"✗ Failed to send email: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False