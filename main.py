from event_notifier import EventNotifier
from google_calendar import get_upcoming_events
from display import display_event_on_all_screens

def main():
    notifier = EventNotifier(
        get_events_func=get_upcoming_events,
        display_event_func=display_event_on_all_screens,
    )
    try:
        notifier.start()
    except KeyboardInterrupt:
        notifier.stop()


if __name__ == "__main__":
    main()
