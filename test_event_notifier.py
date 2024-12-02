import unittest
from unittest.mock import MagicMock, call
from datetime import datetime, timedelta, timezone
import threading
from event_notifier import EventNotifier


class TestEventNotifier(unittest.TestCase):
    def setUp(self):
        # Mock functions
        self.get_events_func = MagicMock()
        self.time_provider = MagicMock()

        # Start time for tests
        self.current_time = datetime(2021, 1, 1, 12, 0, tzinfo=timezone.utc)

        # Time provider returns the current time
        self.time_provider.side_effect = self.get_current_time

        # Sleep function increments current_time
        self.sleep_func = MagicMock()
        self.sleep_func.side_effect = self.sleep_side_effect

        # Event to signal when display_event_func is called
        self.display_event_called = threading.Event()
        self.display_event_func = MagicMock(side_effect=self.display_event_side_effect)

        # Create EventNotifier instance with shorter intervals for testing
        self.notifier = EventNotifier(
            get_events_func=self.get_events_func,
            display_event_func=self.display_event_func,
            poll_interval=1,        # 1 second for faster testing
            alarm_offset=2,         # 2 seconds before event
            screen_hold_duration=1, # 1 second hold duration
            time_provider=self.time_provider,
            sleep_func=self.sleep_func,
        )

    def get_current_time(self, tz=None):
        return self.current_time

    def sleep_side_effect(self, duration):
        self.current_time += timedelta(seconds=duration)

    def display_event_side_effect(self, *args, **kwargs):
        self.display_event_called.set()

    def test_no_upcoming_events(self):
        # Simulate no events
        self.get_events_func.return_value = []

        # Run notifier in a separate thread
        notifier_thread = threading.Thread(target=self.notifier.start)
        notifier_thread.start()

        # Wait for sleep_func to be called
        while self.sleep_func.call_count < 1:
            pass  # Wait

        # Stop the notifier
        self.notifier.stop()
        notifier_thread.join()

        # Assert that display_event_func was not called
        self.display_event_func.assert_not_called()
        # Assert that sleep_func was called with poll_interval
        self.sleep_func.assert_called_with(1)

    def test_event_notification(self):
        # Simulate an event starting in 5 seconds
        event_start_time = (self.current_time + timedelta(seconds=5)).isoformat()
        event = {'start': {'dateTime': event_start_time}, 'summary': 'Test Event'}
        self.get_events_func.return_value = [event]

        # Run notifier in a separate thread
        notifier_thread = threading.Thread(target=self.notifier.start)
        notifier_thread.start()

        # Wait until display_event_func is called
        self.display_event_called.wait(timeout=1)

        # Stop the notifier
        self.notifier.stop()
        notifier_thread.join()

        # Assert that display_event_func was called once
        self.display_event_func.assert_called_once_with(event, hold_duration=1)

    def test_event_cancelled_before_alarm(self):
        # Simulate an event starting in 5 seconds
        event_start_time = (self.current_time + timedelta(seconds=5)).isoformat()
        event = {'start': {'dateTime': event_start_time}, 'summary': 'Test Event'}

        # First call returns the event, second call returns no events
        self.get_events_func.side_effect = [
            [event],
            [],
        ]

        # Run notifier in a separate thread
        notifier_thread = threading.Thread(target=self.notifier.start)
        notifier_thread.start()

        # Allow some time for get_events_func to be called twice
        while self.get_events_func.call_count < 2:
            pass  # Wait

        # Stop the notifier
        self.notifier.stop()
        notifier_thread.join()

        # Assert that display_event_func was not called
        self.display_event_func.assert_not_called()

    def test_multiple_events(self):
        # Simulate multiple events
        event1_start_time = (self.current_time + timedelta(seconds=5)).isoformat()
        event1 = {'start': {'dateTime': event1_start_time}, 'summary': 'Event 1'}

        event2_start_time = (self.current_time + timedelta(seconds=15)).isoformat()
        event2 = {'start': {'dateTime': event2_start_time}, 'summary': 'Event 2'}

        # Side effect to simulate events changing over time
        self.get_events_func.side_effect = [
            [event1, event2],  # Initial events
            [event1, event2],  # Before event1 is notified
            [event2],          # After event1 is notified
            [event2],          # Before event2 is notified
            [],                # After event2 is notified
        ]

        # Event to signal when both events have been notified
        self.display_event_calls = 0
        self.all_events_notified = threading.Event()

        def display_event_side_effect(event, hold_duration):
            self.display_event_calls += 1
            if self.display_event_calls >= 2:
                self.all_events_notified.set()

        self.display_event_func.side_effect = display_event_side_effect

        # Run notifier in a separate thread
        notifier_thread = threading.Thread(target=self.notifier.start)
        notifier_thread.start()

        # Wait until both events have been notified
        self.all_events_notified.wait(timeout=2)

        # Stop the notifier
        self.notifier.stop()
        notifier_thread.join()

        # Assert that display_event_func was called twice
        self.assertEqual(self.display_event_func.call_count, 2)
        expected_calls = [
            call(event1, hold_duration=1),
            call(event2, hold_duration=1),
        ]
        self.display_event_func.assert_has_calls(expected_calls, any_order=False)


if __name__ == '__main__':
    unittest.main()
