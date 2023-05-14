import os
import uuid
from dotenv.main import load_dotenv
import logging
from twilio.rest import Client
from flask import Flask, request
from flask import session
from db import db
from models import CallSidModel

from twilio.twiml.voice_response import VoiceResponse, Gather

logging.basicConfig(level=logging.INFO)

load_dotenv()

account_sid = os.environ['ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
to_phone_number = os.environ['TO_PHONE_NUMBER']
from_phone_number = os.environ['FROM_PHONE_NUMBER']
answer_endpoint = os.environ['ANSWER_ENDPOINT'] # url endpoint: /answer
secret_key = os.environ['SECRET_KEY']
client = Client(account_sid, auth_token)


app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
app.secret_key = secret_key # set a secret key for the session
with app.app_context():
    db.create_all()

@app.route('/')
def hello():
    return "Hello World!"


@app.route('/call', methods=['GET', "POST"])
def make_call():
    logging.info('Call Started .....')
    call = client.calls.create(
        url=answer_endpoint,
        to=to_phone_number,
        from_=from_phone_number
    )
    callSid = call.sid
    name = 'TESTUSER'+ uuid.uuid4().hex
    try:
        logging.info(f"Logging call sid:{callSid}")
        CallSidModel.create(name, callSid)
    except Exception as e:
        logging.error(f'Error inserting data into db...:{e}')
    
    logging.info('Call Complete .....')
    return call.sid


@app.route('/answer', methods=['GET', 'POST'])
def answer_call():
    """Respond call with a brief message"""
    logging.info(f'Answering the phone call .........')
    # start TwiML response
    resp = VoiceResponse()
    customer_name = "Jaya Prakash"
    # Read  a message to the caller
    resp.say(
        f"Hi {customer_name}! We are Clear One Advantage and do Loan Consolidation", voice='alice')

    # Start our <Gather> verb
    gather = Gather(num_digits=1, action='/gather')
    gather.say(
        'Press 1 if you want to talk to Sales. Press 2 if you want to talk to Support. Press 3 to end the call.')
    resp.append(gather)
    logging.info(f'Logging  resp:{resp}')
    # If the user doesn't select an option, redirect them into a loop
    resp.redirect('/answer ')
    logging.info(f'Answered the phone call .........')
    return str(resp)


@app.route('/gather', methods=['GET', 'POST'])
def gather():
    """Processes results from the <Gather> prompt in /answer"""
    logging.info(
        f'Performing operation based on user input started for the req:{request} ')
    # Start TwiML response
    resp = VoiceResponse()

    # If Twilio's request to our app included already gathered digits,
    # process them
    if 'Digits' in request.values:
        # Get which digit the caller chose
        choice = request.values['Digits']
        logging.info(f'Logging choice...{choice}')

        # <Say> a different message depending on the caller's choice
        if choice == '1':
            resp.say('You selected sales. Good for you!')
            return str(resp)
        elif choice == '2':
            resp.say('You need support. We will help!')
            return str(resp)
        elif choice == '3':
            resp.say('Thanks for calling. Have a great day!')
            return str(resp)
        else:
            # If the caller didn't choose 1 or 2, apologize and ask them again
            resp.say("Sorry, I don't understand that choice.")

    # If the user didn't choose 1 or 2 (or anything), send them back to /voice
    resp.redirect('/answer')

    return str(resp)


@app.route('/intent_detection_twilio', methods=['POST'])
def twilio_intent():
    logging.info(f'Detecting twilio intent......')

    return "200"


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    logging.info(f'Inside dialogflow..............')
    payload = request.get_json(force=True)
    logging.info(f'Logging payload data:{payload}')
    return {'fulfillmentText': 'Yoo, was up?'}


def terminateCall():
    logging.info(f'Terminating the call.....')
     # Start TwiML response
    latest_record = CallSidModel.query.order_by(CallSidModel.id.desc()).first()
    callSid  = latest_record.sid
    logging.info(f'Logging latest record sid...{callSid}')
    try:
        call = client.calls(callSid) \
            .update(status='completed')
        call_to = call.to
        logging.info(f'Logging call to..{call.to}')
        logging.info(f'Call Terminated...')
    except Exception as e:
        logging.error(f'Exception occured while terminating the call due to error:{e}')
    return call_to


if __name__ == '__main__':
    app.run()
