# Unmissable Calendar Notifications

Stop being late to meetings because your calendar notifications got lost in the mud. Read your Google Calendar through Google's API and send unmissable notifications that take up your entire screen for several minutes before each event on your calendar.

## Intro

### Wait, but can't you just...

Q: "Oh, but I get notifications on my phone"

A: "So do I, my phone is sometimes on silent. Then I miss them"

Q: "Oh, but I get notifications from my browser"

A: "So do I, my browser is sometimes closed. Then I miss them"

Q: "Oh, have you checked your settings?"

A: "Yes, I have. Phone, broser, computer, calendar, focus modes, volume controls, etc."

Q: "Have you tried Googling it? [Troubleshoot missing Google Calendar notifications](https://support.google.com/calendar/answer/12200012?hl=en)"

A: "Yes, I have"

The problem, fundamentally, is that there are too many settings between me and my calendar notifications. More settings means more things that have to be aligned in order to get the notifications. Unmissable notifications should have virtually no settings. As simple as can be.

### How it Works

Here's what unmissable notifications does:

1. Every X minutes, check the user's calendar for the next event.
2. Set a timer to send them a desktop notification Y minutes before the event starts.
3. When it is time to send the notification, display it full screen on all displays.
4. If the script ever stops running, send the user an email.

Only works on Windows at the moment

## Usage

Not planning to maintain usage documentation for this. If you want to use it and can't figure out how, let me know and I'll help.

Roughly, you need to connect to the Google Calendar API through the google cloud platform, and also provide a heartbeat url. Credentials go in a `credentials.json` file in the root directory. The heartbeat url goes in a `heartbeat.json` file in the root directory.

## Run on Startup

On Windows, you can use Task Scheduler to run the script on startup. Here's roughly what you need to do:

1. Open task scheduler
2. Create a new task
3. Set the action to run a program
4. Set the program to absolute path to python.exe in your venv
5. Set the arguments to the relative path of the script
6. Set the start in to the absolute directory of the script
7. Set other settings like when to run, when to re-run, what to do if it crashes, etc.

Right now I have it set to attempt to start it every day. If it's already running, do nothing. My thought is if it crashes, it should make an attempt to start it once per day.

## Notes

- Most of this was written by AI, I just guided it and made modifications
- later on can read notification preferences from google calendar, optionally

## Logging & Down Detection

Unmissable notifications should be running all the time. So:

1. If something goes wrong, you won't be watching and you need logs to tell you how to fix it. Check the logs.
2. If for any reason the program stops running, you need to be notified as soon as possible. I have used healthchecks.io for this purpose.

## Next Steps

If you don't see the notification until after it has started, may want to show the alert a few minutes longer.
