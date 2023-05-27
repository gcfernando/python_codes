# Developer ::> Gehan Fernando
# import libraries
import os
from twilio.rest import Client

class TwilioService:
    def __init__(self, account_sid, auth_token, twilio_phone_number, twilio_whatsapp_number):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.twilio_phone_number = twilio_phone_number
        self.twilio_whatsapp_number = twilio_whatsapp_number
        self.client = Client(account_sid, auth_token)
    
    def send_sms(self, to_number, message_body):
        self.client.messages.create(body=message_body, from_=self.twilio_phone_number, to=to_number)

    def send_whatsapp_message(self, to_number, message_body):
        self.client.messages.create(body=message_body, from_='whatsapp:' + self.twilio_whatsapp_number, to='whatsapp:' + to_number)

    def make_call(self, to_number, twiml_url):
        self.client.calls.create(url=twiml_url, from_=self.twilio_phone_number, to=to_number)

twilio_service = TwilioService(account_sid='********************', auth_token='********************', 
                               twilio_phone_number='+***********', twilio_whatsapp_number='+***********')

while True:
    os.system('cls')

    serviceType = eval(input("Enter option (0, 1, 2) : "))
    recipient_phone_number = input("Enter recipient phone number : ")
    message = input("Enter message : ")

    if serviceType == 0:
        twilio_service.send_sms(recipient_phone_number, message)
    elif serviceType == 1:
        twilio_service.send_whatsapp_message(recipient_phone_number, message)
    else:
        twilio_service.make_call(recipient_phone_number, 'http://demo.twilio.com/docs/voice.xml')