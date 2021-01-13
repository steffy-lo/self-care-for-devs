import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from datetime import datetime, timedelta

DEBUG = True  # change to false if you want to prevent server from reloading

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']


@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.form
    user_id = data.get('user_id')
    service = data.get('text')
    if service == 'stretch':
        client.chat_postMessage(channel=user_id, text="Subscribed to stretch notifications!")
        subscribe_stretch()
    elif service == 'nagging':
        # Victoria
        raise NotImplemented
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

# Sends notifications to stretch once every hour, with helpful infographics to follow
def subscribe_stretch():


if __name__ == "__main__":
    if DEBUG:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', debug=False, port=os.environ.get('PORT', 80))
