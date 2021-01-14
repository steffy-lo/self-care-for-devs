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
import random

DEBUG = True  # change to false if you want to prevent server from reloading

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']

STRETCH_MESSAGES = [
    {'text': 'It\'s stretching time!',
     'attachment': 'https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch7_uzyfkp.jpg'},
    {'text': 'Another stretching time!',
     'attachment': 'https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch5_k2j8gq.png'},
    {'text': 'Time to stretch! Get up and stretch!',
     'attachment': 'https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch6_emvfa7.jpg'},
    {'text': 'Do you know that stretching improves circulation? So let\'s do it!',
     'attachment': 'https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch10_kead0s.png'},
    {'text': 'Let\'s stretch once an hour!',
     'attachment': 'https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch9_ve3p6y.jpg'},
    {'text': 'A healthy developer always stretches!',
     'attachment': 'https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch8_c3j5ab.jpg>'},
    {'text': 'Stretch for better health and productivity!',
     'attachment': 'https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch2_nddrup.jpg'},
    {'text': 'Stretching time! It only takes 2 minutes!',
     'attachment': 'https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch3_zypmtz.jpg'},
    {'text': 'A 2-minute stretch every hour can make a huge difference on your health!',
     'attachment': 'https://res.cloudinary.com/viclo2606/image/upload/v1610554469/Stretch/stretch4_w2bd87.jpg'},
    {'text': 'Time to relax and have a nice stretch!',
     'attachment': 'https://res.cloudinary.com/viclo2606/image/upload/v1610554470/Stretch/stretch1_swod3r.png'}
]

NAGGING_MESSAGES = [
    {
        'text': 'Are you hungry? Let\'s have some healthy snacks! Do you know almonds are great snacks? They lower bad cholesterol and contain vitamin E, magnesium, potassium and calcium!'},
    {
        'text': 'If you are always looking at screen, always remember to take short eye breaks every 30 minutes. This will prevent eye fatigues, dry eyes and blurry visions.'},
    {
        'text': 'Did you know that people will blink less when staring at screens? This can cause dry eyes and form tiny abrasions in your eyes. Over time, your vision may deteriorate.'},
    {
        'text': 'For better eye health, research recommends the 20/20 rule. Every 20 minutes on the screen, look far for 20 seconds.'},
    {
        'text': 'It\'s easy to get absorbed into work and forgot about good posture. But this increases the risk of muscle strain, neck and back pain. Check your posture every few minutes!'},
    {
        'text': 'Just a friendly reminder to check your posture. Don\'t strain your neck forward and make sure the screen is at least 30cm away from you.'},
    {'text': 'Have you been sitting too long? How about we stand up, walk to get some water and stretch a little?'},
    {
        'text': 'Standing up every hour boosts energy, circulation and productivity. It only takes 5 minutes to stand and stretch. Let\'s do it!'},
    {
        'text': 'Is your computer screen too bright? If you feel exhausted after staring at your screen for 30 minutes, you should try lowering the screen brightness or add some lighting to reduce glare.'},
    {
        'text': 'Do not underestimate the benefits of water. It can immediately make you feel more energized and reduce headaches that comes from fatigue. Drink water!'},
    {
        'text': 'Replace your caffeine intake with water. Water provide tons more health benefits than caffeine. A healthy developer should drink more water!'},
    {
        'text': 'Did you know that clutter on our desks can unconsciously lead to stress and unproductivity? Keep your desks clean and tidy to be an efficient developer!'},
    {
        'text': 'Don\'t skip meals! You need to feed your body well so that it can function well. Your brain will thank you for feeding it well with nutritious foods.'},
    {
        'text': 'Some amazing foods to boost memory and brain activity are blueberries, nuts, broccoli, salmon, eggs and avocado. Eat more of them for happy brains!'},
    {
        'text': 'Feeling a little stressed? Take 5 minutes to breathe deeply, close your eyes and meditate. You will feel calmer, more grounded and less stressed.'},
]

WATER_MESSAGES = [
    {
        'text': 'Time to drink water - keep yourself energised,hydration is the Number 1 Rule of health nutrition.'},
    {
        'text': 'Hey! Time to rejuvenate your body temperature by drinking Water.'},
    {
        'text': 'Hey it\'s that time again 😀,keep things moving have some H2O.'},
    {
        'text': 'Assist your body by drinking water as an escape route from constipation.'},
    {
        'text': 'Lubricate your shock absorbing joints by drinking H2O, assist yor body to prevent joint pains'},
    {
        'text': 'A beautiful skin a lovely smile can be maintained by drinking water, keep yourself hydrated.'}

]

EYE_MESSAGES = [
    {
        'text': 'Give your eyes a break! Time to practice the 20-20-20 rule.',
        'image_url': 'https://res.cloudinary.com/dx0ws0ikf/image/upload/v1610635473/eye-care-1_gknc2k.jpg'
    },
    {
        'text': 'Did you know some these facts? How about taking a break from the screen?',
        'image_url': 'https://res.cloudinary.com/dx0ws0ikf/image/upload/v1610635473/eye-care-6_gyqkxq.png'
    },
    {
        'text': 'Follow some of these eye exercises to help reduce eye strain and train your eye muscles!',
        'image_url': 'https://res.cloudinary.com/dx0ws0ikf/image/upload/v1610635473/eye-care-3_qkq7jl.png'
    },
    {
        'text': 'Practice these 8 tips for you to improve your eye health.',
        'image_url': 'https://res.cloudinary.com/dx0ws0ikf/image/upload/v1610635474/eye-care-4_vvrrbr.jpg'
    },
    {
        'text': 'Let\'s practice the 20-20-20 rule!',
        'image_url': 'https://res.cloudinary.com/dx0ws0ikf/image/upload/v1610635473/eye-care-5_vq3bxs.jpg'
    },
    {
        'text': 'Eyes getting tired? How about some eye yoga to reset them?',
        'image_url': 'https://res.cloudinary.com/dx0ws0ikf/image/upload/v1610635473/eye-care-2_j4deez.png'
    }

]


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    text = event.get('text')
    user_id = event.get('user')

    if user_id == BOT_ID:
        if any(d['text'] == text for d in STRETCH_MESSAGES):
            subscribe_stretch(channel_id)  # re-schedule a new stretch message once a stretch message is sent
        elif any(d['text'] == text for d in NAGGING_MESSAGES):
            subscribe_nagging(channel_id)  # re-schedule a new nagging message once a nagging message is sent
        elif any(d['text'] == text for d in WATER_MESSAGES):
            subscribe_water(channel_id)
        elif text == "Keep Calm and Have a Meme":
            schedule_meme_notification(channel_id)
        elif any(d['text'] == text for d in EYE_MESSAGES):
            schedule_eye_care_notification(user_id)


@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.form
    user_id = data.get('user_id')
    service = data.get('text')
    if service == 'stretch':
        client.chat_postMessage(channel=user_id, text="Subscribed to stretch notifications!")
        subscribe_stretch(user_id)
    elif service == 'nagging':
        client.chat_postMessage(channel=user_id, text="Subscribed to nagging notifications!")
        subscribe_nagging(user_id)
    elif service == 'water':
        client.chat_postMessage(channel=user_id, text="Subscribed to water notifications!")
        subscribe_water(user_id)
    elif service == 'memes':
        client.chat_postMessage(channel=user_id, text="Subscribed to memes notifications!")
        thr = Thread(target=schedule_meme_notification, args=[user_id])
        thr.start()
        return Response(), 200
    elif service == 'eye-care':
        # Steffy
        client.chat_postMessage(channel=user_id, text="Subscribed to eye care notifications!")
        schedule_eye_care_notification(user_id)
    elif service == 'motivational-quotes':
        # Thulie
        raise NotImplemented
    else:
        client.chat_postMessage(channel=user_id, text="Sorry, Granny doesn't understand your command.")
    return Response(), 200


def schedule_eye_care_notification(user_id):
    eye_care = random.choice(EYE_MESSAGES)
    post_at = (datetime.now() + timedelta(seconds=40)).timestamp()
    client.chat_scheduleMessage(channel=user_id, post_at=str(post_at), text=eye_care.get('text'), attachments=[
        {
            "fallback": "Eye Infographic",
            "image_url": eye_care.get('image_url')
        }
    ])
    return Response(), 200


def schedule_meme_notification(user_id):
    image_url = get_meme()
    post_at = (datetime.now() + timedelta(seconds=40)).timestamp()
    client.chat_scheduleMessage(channel=user_id, post_at=str(post_at), text="Keep Calm and Have a Meme", attachments=[
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


# Sends notifications to stretch once every hour
def subscribe_stretch(user):
    stretch = random.choice(STRETCH_MESSAGES)
    post_at = (datetime.now() + timedelta(seconds=20)).timestamp()
    client.chat_scheduleMessage(channel=user, text=stretch.get('text'), post_at=str(post_at), attachments=[
        {
            "fallback": "Stretching Infographic",
            "image_url": stretch.get('attachment')
        }
    ])


# Sends a nag at random intervals
def subscribe_nagging(user):
    nagging = random.choice(NAGGING_MESSAGES)
    random_seconds = random.randint(1800, 10800)  # interval between 30 minutes (1800) to 3 hours (10800)
    post_at = (datetime.now() + timedelta(seconds=random_seconds)).timestamp()
    client.chat_scheduleMessage(channel=user, text=nagging.get('text'), post_at=str(post_at))


# SEND WATER NOTIFICATIONS EVERY 2 HOURS
def subscribe_water(user):
    water = random.choice(WATER_MESSAGES)
    post_at = (datetime.now() + timedelta(hours=2)).timestamp()
    client.chat_scheduleMessage(channel=user, text=water.get('text'), post_at=str(post_at))


@app.route('/help', methods=['POST'])
def help_command():
    data = request.form
    user_id = data.get('user_id')
    help_text = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*SLASH COMMANDS* \n*/todo*: returns task list"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*/todo [task, date]*: adds a task with deadline date"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*/done [task]*: marks a task as completed"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*/subscribe [service]*: subscribe to a specified service to receive notifications"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*/unsubscribe [service]*: unsubscribe to a specified service to stop notifications"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*SERVICES* \n*motivational-quotes*: sends a quote every morning"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*eye-care*: sends a eye break notification every 30 mins, with helpful infographics"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*stretch*: sends a notification to stretch every hour, with helpful infographics"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*water*: sends reminder to drink water every 2 hours"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*memes*: sends programming-related memes every 3 hours to brighten the day"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*nagging*: sends reminders on healthy habits like posture, screen brightness, stand up, "
                        "etc. "
            }
        }
    ]

    client.chat_postMessage(channel=user_id, blocks=help_text)
    return Response(), 200


if __name__ == "__main__":
    if DEBUG:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', debug=False, port=os.environ.get('PORT', 80))
