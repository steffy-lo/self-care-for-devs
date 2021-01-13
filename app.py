import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from datetime import datetime, timedelta
import random

DEBUG = True  # change to false if you want to prevent server from reloading

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']

STRETCH_MESSAGES = [
    {'text': 'It\'s stretching time! <https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch7_uzyfkp.jpg>'},
    {'text': 'Another stretching time! <https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch5_k2j8gq.png>'},
    {'text': 'Time to stretch! Get up and stretch! <https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch6_emvfa7.jpg>'},
    {'text': 'Do you know that stretching improves circulation? So let\'s do it! <https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch10_kead0s.png>'},
    {'text': 'Let\'s stretch once an hour! <https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch9_ve3p6y.jpg>'},
    {'text': 'A healthy developer always stretches! <https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch8_c3j5ab.jpg>'},
    {'text': 'Stretch for better health and productivity! <https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch2_nddrup.jpg>'},
    {'text': 'Stretching time! It only takes 2 minutes! <https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch3_zypmtz.jpg>'},
    {'text': 'A 2-minute stretch every hour can make a huge difference on your health! <https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch4_w2bd87.jpg>'},
    {'text': 'Time to relax and have a nice stretch! <https://res.cloudinary.com/viclo2606/image/upload/v1610554470/Stretch/stretch1_swod3r.png>'}
]


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    user_id = event.get('user')
    text = event.get('text')
    if text in STRETCH_MESSAGES:
        subscribe_stretch(user_id)  # re-schedule a new stretch message once a stretch message is sent


@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.form
    user_id = data.get('user_id')
    service = data.get('text')
    if service == 'stretch':
        client.chat_postMessage(channel=user_id, text="Subscribed to stretch notifications!")
        subscribe_stretch(user_id)
    elif service == 'nagging':
        # Victoria
        client.chat_postMessage(channel=user_id, text="Subscribed to nagging notifications!")
    elif service == 'memes':
        # Steffy
        raise NotImplemented
    elif service == 'eye-break':
        # Steffy
        raise NotImplemented
    elif service == 'water':
        # Thulie
        raise NotImplemented
    elif service == 'motivational-quotes':
        # Thulie
        raise NotImplemented
    else:
        client.chat_postMessage(channel=user_id, text="Sorry, Granny doesn't understand your command.")
    return Response(), 200


# Sends notifications to stretch once every hour
def subscribe_stretch(user):
    stretch = random.choice(STRETCH_MESSAGES)
    client.chat_scheduleMessage(channel=user, text=stretch.text,
                                post_at=(datetime.now() + timedelta(hours=1)).timestamp())


if __name__ == "__main__":
    if DEBUG:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', debug=False, port=os.environ.get('PORT', 80))
