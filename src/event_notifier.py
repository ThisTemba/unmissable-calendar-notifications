import threading
from datetime import datetime, timedelta, timezone
from typing import Callable

import requests  # Add this import


class EventNotifier:
    def __init__(
        self,
        get_next_event_func: Callable[[], dict],
        send_notification_func: Callable[[dict], None],
        heartbeat_url: str,
        poll_interval: int = 15 * 60,
        alarm_offset: int = 3 * 60,
        heartbeat_period: int = 5 * 60,
    ):
        """
        Initializes the EventNotifier with the given functions.
        :param get_next_event_function: Function that returns the next event as a dictionary.
        :param send_notification_function: Function that sends a notification for an event.
        """
        self.get_next_event_func = get_next_event_func
        self.send_notification_func = send_notification_func
        self.next_event = None
        self.check_timer = None
        self.poll_interval = poll_interval  # in seconds
        self.alarm_offset = alarm_offset  # in seconds
        self.notification_timer = None
        self.lock = threading.Lock()
        self.heartbeat_url = heartbeat_url
        self.heartbeat_timer = None
        self.heartbeat_period = heartbeat_period

    def start(self):
        """
        Starts the event notifier.
        """
        self.schedule_next_check()
        self.schedule_heartbeat()  # Add this line

    def schedule_next_check(self):
        """
        Schedules the next check for the next event.
        """
        self.check_next_event()
        print(f"Next check scheduled in {self.poll_interval} seconds.")
        self.check_timer = threading.Timer(self.poll_interval, self.schedule_next_check)
        self.check_timer.start()

    def check_next_event(self):
        """
        Checks for the next event and schedules a notification.
        """
        print("Checking for next event...")
        with self.lock:
            self.next_event = self.get_next_event_func()
            self.schedule_notification()

    def schedule_notification(self):
        """
        Schedules a notification 3 minutes before the event starts.
        """
        no_start_time = "dateTime" not in self.next_event["start"]
        if no_start_time:
            print("Skipping all-day event.")
            return

        start_time_str = self.next_event["start"]["dateTime"]
        event_start_dt = datetime.fromisoformat(start_time_str)
        notify_dt = event_start_dt - timedelta(seconds=self.alarm_offset)
        now_dt = datetime.now(timezone.utc)
        delay = (notify_dt - now_dt).total_seconds()

        # TODO: potential bug is current event blocking next event,
        # should ignore events that are in progress

        if delay > 0:
            print(f"Notification scheduled in {round(delay)} seconds.")
            if self.notification_timer:
                self.notification_timer.cancel()
            self.notification_timer = threading.Timer(delay, self.send_notification)
            self.notification_timer.start()

    def send_notification(self):
        """
        Sends a notification for the next event.
        """
        print("Sending notification...")
        self.send_notification_func(self.next_event.copy())

    def schedule_heartbeat(self):
        """
        Schedules a heartbeat signal to the URL every minute.
        """
        self.send_heartbeat()
        self.heartbeat_timer = threading.Timer(
            self.heartbeat_period, self.schedule_heartbeat
        )
        self.heartbeat_timer.start()

    def send_heartbeat(self):
        """
        Pings the specified URL.
        """
        try:
            requests.get(self.heartbeat_url)
            print(f"Pinged {self.heartbeat_url}")
        except requests.RequestException as e:
            print(f"Failed to ping {self.heartbeat_url}: {e}")

    def stop(self):
        """
        Stops the event notifier.
        """
        if self.check_timer:
            self.check_timer.cancel()
        if self.notification_timer:
            self.notification_timer.cancel()
        if self.heartbeat_timer:
            self.heartbeat_timer.cancel()


def main():
    def get_next_event():
        # Your implementation to fetch the next event
        pass

    def send_notification(event):
        # Your implementation to send a notification
        pass

    notifier = EventNotifier(get_next_event, send_notification)
    timestr = notifier.get_start_dt(
        {"dateTime": "2024-12-02T13:30:00-05:00", "timeZone": "America/New_York"}
    )
    print(timestr)


if __name__ == "__main__":
    main()
