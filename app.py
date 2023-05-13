import os
from dotenv.main import load_dotenv
from twilio.rest import Client
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse

load_dotenv()

account_sid = os.environ['ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
to_phone_number = os.environ['TO_PHONE_NUMBER']
from_phone_number = os.environ['FROM_PHONE_NUMBER']
client = Client(account_sid, auth_token)

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/call', methods=['GET', "POST"])
def make_call():
    print('Call Started .....')
    call = client.calls.create(
    url="http://demo.twilio.com/docs/voice.xml",
    to=to_phone_number,
    from_=from_phone_number
    )

    print(call.sid)
    print('Call Complete .....')
    return call.sid
    

@app.route('/answer', methods=['GET', 'POST'])
def answer_call():
    """Respond call with a brief message"""
    
    # start TwiML response
    resp = VoiceResponse()
    
    # Read  a message to the caller
    resp.say("Thank you for calling! Have a great day.", voice='alice')
    
    return str(resp)

@app.route('/intent_detection_twilio', methods=['POST'])
def twilio_intent():
    print(f'Detecting twilio intent......')
    
    return "200"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    print(f'Inside dialogflow..............')
    payload = request.get_json(force=True)
    print(f'Logging payload data:{payload}')
    return {'fulfillmentText': 'Yoo, was up?'}
    
    
if __name__ == '__main__':
    app.run()