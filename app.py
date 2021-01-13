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

if __name__ == "__main__":
    if DEBUG:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', debug=False, port=os.environ.get('PORT', 80))
