import os
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

load_dotenv()


class EmailManager:
    def __init__(self):
        # Brevo API settings
        self.__api_key = os.getenv("BREVO_API_KEY")

        # Email settings
        self.__sender_email = os.getenv("SENDER_EMAIL")
        self.__sender_name = os.getenv("SENDER_NAME", "Geofence Alert System")
        self.__receiver_email = "carljohannesllarenas.munoz24@bicol-u.edu.ph"
        self.__message_text = None

        # Validate credentials
        if not self.__api_key:
            raise ValueError("BREVO_API_KEY must be set in environment variables")
        if not self.__sender_email:
            raise ValueError("SENDER_EMAIL must be set in environment variables")

        # Configure Brevo API
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = self.__api_key
        self.__api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

    def create_message(self, text):
        """Create email message"""
        self.__message_text = text

    def send_alert_email(self):
        """Send email using Brevo API"""
        if not self.__message_text:
            raise ValueError("No message created. Call create_message() first.")

        try:
            # Create email object
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": self.__receiver_email}],
                sender={"name": self.__sender_name, "email": self.__sender_email},
                subject="🚨 Geofence Alert",
                text_content=self.__message_text
            )

            # Send email
            api_response = self.__api_instance.send_transac_email(send_smtp_email)

            print(f"✓ Email sent successfully to {self.__receiver_email}")
            print(f"Message ID: {api_response.message_id}")
            return True

        except ApiException as e:
            print(f"✗ Brevo API error: {e}")
            return False
        except Exception as e:
            print(f"✗ Failed to send email: {type(e).__name__}: {e}")
            return False