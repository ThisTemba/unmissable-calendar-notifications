import json

from notify import display_event_on_all_screens
from event_notifier import EventNotifier
from google_calendar import get_next_event


def main():
    with open("heartbeat.json") as f:
        data = json.load(f)
        heartbeat_url = data["heartbeat_url"]

    notifier = EventNotifier(
        get_next_event_func=get_next_event,
        send_notification_func=display_event_on_all_screens,
        heartbeat_url=heartbeat_url,
    )
    try:
        notifier.start()
    except KeyboardInterrupt:
        notifier.stop()


if __name__ == "__main__":
    main()
