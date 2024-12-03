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

## Notes

- Most of this was written by AI, I just guided it and made modifications
- later on can read notification preferences from google calendar, optionally

## Logging & Down Detection

Unmissable notifications should be running all the time. So:

1. If something goes wrong, you won't be watching and you need logs to tell you how to fix it. Check the logs.
2. If for any reason the program stops running, you need to be notified as soon as possible. I have used healthchecks.io for this purpose.

## Next Steps

If you don't see the notification until after it has started, may want to show the alert a few minutes longer.
