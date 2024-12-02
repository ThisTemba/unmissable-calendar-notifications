import json
import time  # Add this import

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
        # poll_interval=15, for testing
    )
    try:
        notifier.start()
        while True:
            time.sleep(1)  # Keeps the main thread running
    except KeyboardInterrupt:
        notifier.stop()


def test():
    with open("heartbeat.json") as f:
        data = json.load(f)
        heartbeat_url = data["heartbeat_url"]

    notifier = EventNotifier(
        get_next_event_func=get_next_event,
        send_notification_func=display_event_on_all_screens,
        heartbeat_url=heartbeat_url,
        poll_interval=15,
    )

    # load the next event
    next_event = get_next_event()
    notifier.next_event = next_event

    # send a notification
    notifier.send_notification()


if __name__ == "__main__":
    main()
