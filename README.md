# Self Care for Devs Slack API
> Aka Granny Bot API

## Slash Commands
| Slash Commands        | Description                                    |
|-----------------------|------------------------------------------------|
| `/help`                 | Returns list of commands                       |
| `/todo`                | Returns list of todos                          |
| `/todo [task] [HH:mm]`     | Adds task and deadline time in HH:mm in the todo list                      |
| `/done [task]`          | Marks task as completed                        |
| `/subscribe [service]`   | Receive notifications on the specified service |
| `/unsubscribe [service]` | Stop notifications from the specified service  |


## Services
| Services              | Description                                                                                                                     |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------|
| `quotes` | Sends a motivational quote every morning                                                                                        |
| `eye-care`            | Sends notifications to take eye breaks every 30 minutes, with helpful tips on eye care                                     |
| `stretch`             | Sends notifications to stretch once every hour, with helpful infographics to follow                                          |
| `water`               | Sends reminder to drink water and only H20 every 2 hours                                                                      |                                                |
| `memes`               | Sends programming-related memes every 3 hours to brighten the day                                                           |
| `nagging`             | Sends frequent reminders on random things like your posture, lighting on your setup, stand up occasionally and take eye breaks |

# Getting Started
1. Clone this repo
2. Create your .env file and provide your SLACK_TOKEN and SIGINING_SECRET
3. 