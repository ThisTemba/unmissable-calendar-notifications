import datetime
import time
from typing import Callable

import requests

from event import CalendarEvent
from logger import logger

"""
Super Simple Event notifier:
1. Check calendar for next event
2. If event is soon, wait until it is time to send a notification, then send it
3. If event is not soon, wait a bit, then go back to step 1
"""


class EventNotifier:
    def __init__(
        self,
        get_next_event_func: Callable[[], CalendarEvent],
        send_notification_func: Callable[[CalendarEvent], None],
        heartbeat_url: str,
        poll_interval: int = 15 * 60,
        alarm_offset: int = 3 * 60 + 5,
        heartbeat_period: int = 5 * 60,
    ):
        self.get_next_event_func = get_next_event_func
        self.send_notification_func = send_notification_func
        self.poll_interval = poll_interval  # in seconds
        self.alarm_offset = alarm_offset  # in seconds
        self.heartbeat_url = heartbeat_url
        self.heartbeat_period = heartbeat_period

    def start(self):
        logger.info("Starting notifier.")
        while True:
            self.check_and_wait()

    def check_and_wait(self):
        self.send_heartbeat()

        logger.info("Checking for next event.")
        next_event = self.get_next_event_func()
        time_till_notify = self.get_time_till_notify(next_event)

        if time_till_notify < self.poll_interval:
            logger.info(
                f"Event Soon. Waiting {time_till_notify} s before sending notification."
            )
            time.sleep(time_till_notify)
            self.send_notification(next_event)
        else:
            logger.info(
                f"Event not soon. Waiting {self.poll_interval} s before checking again."
            )
            time.sleep(self.poll_interval)

    def get_time_till_notify(self, next_event):
        start_time_str = next_event["start"]["dateTime"]
        event_start_dt = datetime.datetime.fromisoformat(start_time_str)
        notify_dt = event_start_dt - datetime.timedelta(seconds=self.alarm_offset)
        now_dt = datetime.datetime.now(datetime.timezone.utc)
        time_till_notify = (notify_dt - now_dt).total_seconds()
        return time_till_notify

    def send_notification(self, next_event):
        logger.info("Sending notification.")
        try:
            self.send_notification_func(next_event.copy())
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            print(f"Failed to send notification: {e}")

    def send_heartbeat(self):
        try:
            requests.get(self.heartbeat_url)
            logger.info(f"Pinged {self.heartbeat_url}")
        except requests.RequestException as e:
            logger.error(f"Failed to ping {self.heartbeat_url}: {e}")


def main():
    pass


if __name__ == "__main__":
    main()
