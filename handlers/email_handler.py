import os
from dotenv import load_dotenv
import mailtrap as mt

load_dotenv()

# Debug: Check if .env is loaded
token = os.getenv("MAILTRAP_API_TOKEN")
sender = os.getenv("SENDER_EMAIL", "hello@demomailtrap.co")

print(f"Token exists: {bool(token)}")
print(f"Token: {token}")
print(f"Sender: {sender}")

try:
    mail = mt.Mail(
        sender=mt.Address(email=sender, name="Test"),
        to=[mt.Address(email="10johannesmunoz@gmail.com")],
        subject="Test Email from .env",
        text="This is a test email using environment variables!",
        category="Test"
    )

    client = mt.MailtrapClient(token=token)
    response = client.send(mail)

    print(f"✓ Success! Response: {response}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback

    traceback.print_exc()