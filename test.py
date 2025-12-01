import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

try:
    settings = config['SETTINGS']
except:
    settings = {}

API = settings.get('APIKEY', None)

message = Mail(
    from_email='10johannesmunoz@gmail.com',
    to_emails='carlxxsinenomine@gmail.com',
    subject='Sending with Twilio SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
try:
    sg = SendGridAPIClient(API)
    # sg.set_sendgrid_data_residency("eu")
    # uncomment the above line if you are sending mail using a regional EU subuser
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)