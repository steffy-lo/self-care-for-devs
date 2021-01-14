import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
from threading import Thread

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
    elif service == 'nagging':
        # Victoria
        raise NotImplemented
    elif service == 'memes':
        client.chat_postMessage(channel=user_id, text="Subscribed to memes notifications!")
        thr = Thread(target=schedule_meme_notification, args=[user_id])
        thr.start()
        return Response(), 200

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


def schedule_meme_notification(user_id):
    image_url = get_meme()
    client.chat_scheduleMessage(channel=user_id, post_at=str(datetime.now().timestamp() + timedelta(seconds=40).seconds), text="Keep Calm and Have a Meme", attachments=[
      {
          "fallback": "Programming Memes",
          "image_url": image_url,
      }
    ])
    return Response(), 200


def get_meme():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get('https://www.reddit.com/r/ProgrammerHumor', headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    image = soup.find('img', class_="_2_tDEnGMLxpM6uOa2kaDB3 ImageBox-image media-element _1XWObl-3b9tPy64oaG6fax")
    return str(image.attrs['src'])


if __name__ == "__main__":
    if DEBUG:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', debug=False, port=os.environ.get('PORT', 80))
