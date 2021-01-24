import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slack.errors import SlackApiError
from slackeventsapi import SlackEventAdapter
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
from threading import Thread
import random
import re
import pytz

DEBUG = False  # change to false if you want to prevent server from reloading

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
        'text': 'Hey it\'s that time again :grinning:,keep things moving have some H2O.'},
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

user_to_channel_id = {}

# subscribe intervals or schedule
quote_time = 7
eye_care_interval = 0.5
stretch_interval = 1
water_interval = 2
meme_interval = 3


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
        elif "Quote Of The Day!" in text:
            subscribe_quotes(channel_id)
        elif text == "Keep Calm and Have a Meme":
            schedule_meme_notification(channel_id)
        elif any(d['text'] == text for d in EYE_MESSAGES):
            schedule_eye_care_notification(channel_id)


@app.route('/', methods=['GET'])
def home():
    return 'root'


@app.route('/todo', methods=['POST'])
def todo():
    data = request.form
    user_id = data.get('user_id')
    text = data.get('text')
    if text == '':
        if user_id not in user_to_channel_id:
            client.chat_postMessage(channel=user_id, text="There's currently nothing on your to-do list 😀")
            return Response(), 200
        else:
            return list_todo(user_id)
    elif re.search("\\d\\d:\\d\\d", text[-5:]):
        return schedule_task(user_id, text)
    else:
        try:
            client.chat_postMessage(channel=user_id, text="Sorry, Granny doesn't understand your request.")
            return Response("Invalid request. Please check your request format and try again."), 200
        except SlackApiError as e:
            return Response(str(e)), 500


@app.route('/done', methods=['POST'])
def done():
    data = request.form
    user_id = data.get('user_id')
    text = data.get('text')
    task_deleted = False
    for msg in client.chat_scheduledMessages_list()["scheduled_messages"]:
        if msg["text"][:-9] == "[task] " + text and text != '':
            try:
                client.chat_deleteScheduledMessage(channel=user_id, scheduled_message_id=msg["id"])
                client.chat_postMessage(channel=user_id, text="Deleted [" + text + "] from task list.")
                task_deleted = True
            except SlackApiError as e:
                return Response(str(e)), 500
        if msg["text"][:-9] == "[task reminder] " + text and text != '':
            try:
                client.chat_deleteScheduledMessage(channel=user_id, scheduled_message_id=msg["id"])
                client.chat_postMessage(channel=user_id, text="Deleted [" + text + "] from task reminder list.")
            except SlackApiError as e:
                return Response(str(e)), 500

    # Bad request
    if not task_deleted:
        try:
            client.chat_postMessage(channel=user_id, text="Granny cannot find task " + "[" + text + "]")
            return Response("Invalid task name. Please try again."), 200
        except SlackApiError as e:
            return Response(str(e)), 500
    return Response(), 200


@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.form
    user_id = data.get('user_id')
    service = data.get('text')
    scheduled_messages = client.chat_scheduledMessages_list()["scheduled_messages"]

    for msg in scheduled_messages:
        if scheduled_exists(service, msg, user_id):
            client.chat_postMessage(channel=user_id, text="You are already subscribed to " + service + " notifications.")
            return Response(), 200

    if service == 'stretch':
        client.chat_postMessage(channel=user_id, text="Subscribed to stretch notifications!")
        subscribe_stretch(user_id)
    elif service == 'nagging':
        client.chat_postMessage(channel=user_id, text="Subscribed to nagging notifications!")
        subscribe_nagging(user_id)
    elif service == 'water':
        client.chat_postMessage(channel=user_id, text="Subscribed to water notifications!")
        subscribe_water(user_id)
    elif service == 'quotes':
        client.chat_postMessage(channel=user_id, text="Subscribed to quotes notifications!")
        subscribe_quotes(user_id)
    elif service == 'memes':
        client.chat_postMessage(channel=user_id, text="Subscribed to memes notifications!")
        thr = Thread(target=schedule_meme_notification, args=[user_id])
        thr.start()
        return Response(), 200
    elif service == 'eye-care':
        client.chat_postMessage(channel=user_id, text="Subscribed to eye care notifications!")
        schedule_eye_care_notification(user_id)
    else:
        client.chat_postMessage(channel=user_id, text="Sorry, Granny doesn't understand your command.")
        return Response("Invalid service. Please check and try again."), 200

    return Response(), 200


@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    data = request.form
    user_id = data.get('user_id')
    service = data.get('text')
    result = client.chat_scheduledMessages_list()
    SERVICES = ['water', 'stretch', 'quotes', 'eye-care', 'memes', 'nagging']

    if service not in SERVICES or service == '':
        try:
            client.chat_postMessage(channel=user_id, text="Please specify an appropriate service to unsubscribe.")
        except SlackApiError as e:
            return Response(str(e)), 500

    elif len(result["scheduled_messages"]) == 0:
        try:
            client.chat_postMessage(channel=user_id, text="You are currently not subscribed to any service.")
        except SlackApiError as e:
            return Response(str(e)), 500
    else:
        deleting = False
        # Find scheduled message to delete
        for msg in result["scheduled_messages"]:
            if scheduled_exists(service, msg, user_id):
                thr = Thread(target=unsubscribe_service, args=[msg])
                thr.start()
                deleting = True
        if deleting:
            return Response("Unsubscribed from " + service + " service"), 200
        else:
            return Response("You are already currently unsubscribed to " + service + " service"), 200
    return Response(), 200


def scheduled_exists(service, msg, user_id):
    if user_id not in user_to_channel_id:
        return False
    if user_to_channel_id[user_id] == msg['channel_id']:
        if service == 'stretch' and any(d['text'] == msg['text'] for d in STRETCH_MESSAGES):
            return True
        elif service == 'nagging' and any(d['text'] == msg['text'] for d in NAGGING_MESSAGES):
            return True
        elif service == 'water' and any(d['text'] == msg['text'] for d in WATER_MESSAGES):
            return True
        elif service == 'quotes' and "Quote Of The Day!" in msg['text']:
            return True
        elif service == 'memes' and msg['text'] == "Keep Calm and Have a Meme":
            return True
        elif service == 'eye-care' and any(d['text'] == msg['text'] for d in EYE_MESSAGES):
            return True
        else:
            return False
    return False


def unsubscribe_service(msg):
    client.chat_deleteScheduledMessage(channel=msg['channel_id'], scheduled_message_id=msg['id'])
    return Response(), 200


def schedule_task(user_id, text):
    time = text[-5:].strip()
    task = "[task] " + text[:-5].strip() + " by " + time
    task_reminder = "[task reminder] " + text[:-5].strip() + " by " + time

    deadline = datetime.combine(datetime.now(), datetime.strptime(time, '%H:%M').time())
    timezone = pytz.timezone(os.environ["TIMEZONE"])
    deadline = timezone.localize(deadline)
    reminder = (deadline - timedelta(minutes=30)).timestamp()
    if deadline.timestamp() < (datetime.now() + timedelta(minutes=30)).timestamp() or deadline.timestamp() < datetime.now().timestamp():
        try:
            client.chat_postMessage(channel=user_id,
                                    text="Unable to set deadline as it is too early.")
            return Response(
                "Invalid deadline. Please make sure that your deadline is more than 30 minutes in the future."), 200
        except SlackApiError as e:
            return Response(str(e)), 500
    else:
        try:
            res = client.chat_scheduleMessage(channel=user_id, text=task_reminder, post_at=str(reminder))
            client.chat_scheduleMessage(channel=user_id, text=task, post_at=str(deadline.timestamp()))
            user_to_channel_id[user_id] = res["channel"]
            client.chat_postMessage(channel=user_id, text="Added " + text[:-5].strip() + " to task list.")
            return Response(), 200
        except SlackApiError as e:
            return Response(str(e)), 500


def list_todo(user_id):
    try:
        # Call the chat.scheduledMessages.list method using the WebClient
        result = client.chat_scheduledMessages_list()
        if len(result["scheduled_messages"]) == 0:
            try:
                client.chat_postMessage(channel=user_id, text="There's currently nothing on your to-do list 😀")
                return Response(), 200
            except SlackApiError as e:
                return Response(str(e)), 500
        else:
            blocks = []
            # Print scheduled messages
            for msg in result["scheduled_messages"]:
                if msg["text"][:6] == "[task]" and user_to_channel_id[user_id] == msg["channel_id"]:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": msg["text"]
                        }
                    })

            if len(blocks) > 0:
                client.chat_postMessage(channel=user_id, blocks=blocks)
            else:
                client.chat_postMessage(channel=user_id, text="There's currently nothing on your to-do list 😀")
            return Response(), 200
    except SlackApiError as e:
        Response(str(e)), 500


@app.route('/schedule_eye_care/<user_id>', methods=["POST"])
def schedule_eye_care_notification(user_id):
    eye_care = random.choice(EYE_MESSAGES)
    post_at = (datetime.now() + timedelta(hours=eye_care_interval)).timestamp()
    try:
        res = client.chat_scheduleMessage(channel=user_id, post_at=str(post_at), text=eye_care.get('text'), attachments=[
            {
                "fallback": "Eye Infographic",
                "image_url": eye_care.get('image_url')
            }
        ])
        user_to_channel_id[user_id] = res["channel"]
        return Response("Scheduled eye care notification at " + str(post_at)), 200
    except SlackApiError as e:
        return Response(str(e)), 500


@app.route('/schedule_meme/<user_id>', methods=["POST"])
def schedule_meme_notification(user_id):
    image_url = get_meme()
    post_at = (datetime.now() + timedelta(hours=meme_interval)).timestamp()
    try:
        res = client.chat_scheduleMessage(channel=user_id, post_at=str(post_at), text="Keep Calm and Have a Meme",
                                    attachments=[
                                        {
                                            "fallback": "Programming Memes",
                                            "image_url": image_url,
                                        }
                                    ])
        user_to_channel_id[user_id] = res["channel"]
        return Response("Scheduled meme notification at " + str(post_at)), 200
    except SlackApiError as e:
        return Response(str(e)), 500


@app.route('/meme', methods=["GET"])
def get_meme():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get('https://www.reddit.com/r/ProgrammerHumor/new/', headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    image = soup.find('img', class_="_2_tDEnGMLxpM6uOa2kaDB3 ImageBox-image media-element _1XWObl-3b9tPy64oaG6fax")
    return str(image.attrs['src'])


@app.route('/schedule_stretch/<user_id>', methods=["POST"])
# Sends notifications to stretch once every hour
def subscribe_stretch(user_id):
    stretch = random.choice(STRETCH_MESSAGES)
    post_at = (datetime.now() + timedelta(hours=1)).timestamp()
    try:
        res = client.chat_scheduleMessage(channel=user_id, text=stretch.get('text'), post_at=str(post_at), attachments=[
            {
                "fallback": "Stretching Infographic",
                "image_url": stretch.get('attachment')
            }
        ])
        user_to_channel_id[user_id] = res["channel"]
        return Response("Scheduled stretch notification at " + str(post_at)), 200
    except SlackApiError as e:
        return Response(str(e)), 500


# Sends a nag at random intervals
@app.route('/schedule_nagging/<user_id>', methods=["POST"])
def subscribe_nagging(user_id):
    nagging = random.choice(NAGGING_MESSAGES)
    random_seconds = random.randint(1800, 10800)  # interval between 30 minutes (1800) to 3 hours (10800)
    post_at = (datetime.now() + timedelta(seconds=random_seconds)).timestamp()
    try:
        res = client.chat_scheduleMessage(channel=user_id, text=nagging.get('text'), post_at=str(post_at))
        user_to_channel_id[user_id] = res["channel"]
        return Response("Scheduled nagging notification at " + str(post_at)), 200
    except SlackApiError as e:
        return Response(str(e)), 500


# SEND WATER NOTIFICATIONS EVERY 2 HOURS
@app.route('/schedule_water/<user_id>', methods=["POST"])
def subscribe_water(user_id):
    water = random.choice(WATER_MESSAGES)
    post_at = (datetime.now() + timedelta(hours=water_interval)).timestamp()
    try:
        res = client.chat_scheduleMessage(channel=user_id, text=water.get('text'), post_at=str(post_at))
        user_to_channel_id[user_id] = res["channel"]
        return Response("Scheduled water notification at " + str(post_at)), 200
    except SlackApiError as e:
        return Response(str(e)), 500


@app.route('/get_quote', methods=["GET"])
def get_quote():
    req = requests.get("http://famous-quotes.uk/api.php?id=random&minpop=80")
    json = req.json()
    return json[0][1]


# motivational Quotes
@app.route('/schedule_quotes/<user_id>', methods=["POST"])
def subscribe_quotes(user_id):
    quotes = "Quote Of The Day!\n" + get_quote()
    current_datetime = datetime.now()
    current_year = current_datetime.year
    current_month = current_datetime.month
    current_day = current_datetime.day

    # time of the day to be posted
    post = datetime(year=current_year, month=current_month, day=current_day + 1, hour=quote_time)
    post_at = post.timestamp()
    try:
        res = client.chat_scheduleMessage(channel=user_id, text=quotes, post_at=str(post_at))
        user_to_channel_id[user_id] = res["channel"]
        return Response("Scheduled quote notification at " + str(post_at)), 200
    except SlackApiError as e:
        return Response(str(e)), 500


@app.route('/set_notifications', methods=['POST'])
def set_schedule():
    global stretch_interval
    global water_interval
    global quote_time
    global meme_interval
    global eye_care_interval

    data = request.form
    user_id = data.get('user_id')
    args = data.get('text')
    if args:
        args = args.split(" ")
    else:
        return Response("Command requires [value] argument"), 200

    if len(args) != 2:
        return Response("Command requires 2 arguments: [service] [value]"), 200

    service = args[0]
    value = args[1]

    try:
        float(value)
    except ValueError:
        return Response("[value] must be a float!"), 200

    if service == 'stretch':
        stretch_interval = float(value)
    elif service == 'water':
        water_interval = float(value)
    elif service == 'quotes':
        if 0 <= float(value) < 24:
            try:
                quote_time = int(value)
                return Response(
                    "Successfully updated notification schedule for " + service + " service."), 200
            except ValueError:
                return Response("[value] must be a valid integer for quote service."), 200
        else:
            return Response("Invalid value. [value] must be in between 0 and 23."), 200
    elif service == 'memes':
        meme_interval = float(value)
    elif service == 'eye-care':
        eye_care_interval = float(value)
    else:
        try:
            client.chat_postMessage(channel=user_id, text="Sorry, Granny doesn't understand your command.")
            return Response("Invalid service. Please check and try again."), 200
        except SlackApiError as e:
            return Response(str(e)), 500
    return Response("Successfully updated notification schedule for " + service + " to " + str(float(value)) + " h or "
                    + str(float(value)*60) + " min."), 200


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
                "text": "*SERVICES* \n*quotes*: sends a quote every morning"
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

    try:
        client.chat_postMessage(channel=user_id, blocks=help_text)
    except SlackApiError as e:
        return Response(str(e)), 500
    return Response(), 200


if __name__ == "__main__":
    if DEBUG:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', debug=False, port=os.environ.get('PORT', 80))
