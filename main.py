from event_notifier import EventNotifier
from google_calendar import get_next_event
from display import display_event_on_all_screens


def main():
    notifier = EventNotifier(
        get_next_event_func=get_next_event,
        send_notification_func=display_event_on_all_screens,
    )
    try:
        notifier.start()
    except KeyboardInterrupt:
        notifier.stop()


if __name__ == "__main__":
    main()
