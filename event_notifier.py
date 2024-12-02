import time
import threading
from dateutil import parser
from datetime import datetime, timezone


class EventNotifier:
    def __init__(
        self,
        get_events_func,
        display_event_func,
        poll_interval=600,       # 10 minutes in seconds
        alarm_offset=180,        # 3 minutes in seconds
        screen_hold_duration=30, # seconds
        time_provider=datetime.now,
        sleep_func=time.sleep,
    ):
        self.get_events_func = get_events_func
        self.display_event_func = display_event_func
        self.poll_interval = poll_interval
        self.alarm_offset = alarm_offset
        self.screen_hold_duration = screen_hold_duration
        self.time_provider = time_provider
        self.sleep_func = sleep_func
        self.next_event_start_dt_stored = None
        self.alarm_set = False
        self.running = True

    def start(self):
        """Starts the event notifier."""
        while self.running:
            now = self.time_provider(timezone.utc)
            events = self.get_events_func(max_results=1)
            if not events:
                print("No upcoming events found.")
                self.alarm_set = False
                self.next_event_start_dt_stored = None
                self.sleep_func(self.poll_interval)
                continue

            next_event = events[0]
            event_start_time = next_event.get('start', {}).get('dateTime')
            if not event_start_time:
                # Skip events without a specific start time
                self.sleep_func(self.poll_interval)
                continue

            event_start_dt = parser.parse(event_start_time)

            if self.next_event_start_dt_stored != event_start_dt:
                # New event detected
                self.next_event_start_dt_stored = event_start_dt
                self.alarm_set = False

            time_until_event = (event_start_dt - now).total_seconds()
            time_until_alarm = time_until_event - self.alarm_offset

            if not self.alarm_set and time_until_alarm <= 0:
                # It's time to check and notify
                self.check_and_notify_event()
                self.alarm_set = True
                self.next_event_start_dt_stored = None
            else:
                # Sleep for a short interval to check again soon
                sleep_duration = min(self.poll_interval, max(1, time_until_alarm))
                self.sleep_func(sleep_duration)

    def check_and_notify_event(self):
        """Checks if the next event is still on the calendar and displays a notification."""
        events = self.get_events_func(max_results=1)
        if not events:
            print("No upcoming events found.")
            return

        next_event = events[0]
        event_start_time = next_event.get('start', {}).get('dateTime')
        if event_start_time != self.next_event_start_dt_stored.isoformat():
            # Event has changed or been removed
            return

        # Re-check if the event is still there
        self.display_event_func(next_event, hold_duration=self.screen_hold_duration)

    def stop(self):
        """Stops the event notifier."""
        self.running = False

