import datetime
import threading
import tkinter as tk
import winsound  # Add this import

import pytz
from screeninfo import get_monitors

from colors import colors
from logger import logger

BG_COLOR = colors["Stone"][950]
DEFAULT_HOLD_DURATION = (
    200  # seconds (longer is better, good that it is dismissed by you)
)
TEXT_COLOR_PRIMARY = colors["Orange"][400]
TEXT_COLOR_SECONDARY = colors["Gray"][200]


def display_event_on_all_screens(event):
    """Displays the latest event on all screens with an improved UI."""
    monitors = get_monitors()
    logger.info(f"Detected monitors: {monitors}")
    dismiss_event = threading.Event()  # Shared event to signal dismissal

    def create_window(monitor):
        try:
            logger.info(f"Creating window for monitor: {monitor}")
            root = tk.Tk()
            root.overrideredirect(True)
            root.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
            root.configure(background=BG_COLOR)

            # Make the window always on top
            root.attributes("-topmost", True)
            root.lift()
            root.after(0, lambda: root.focus_force())

            logger.info(f"Window geometry set for monitor: {monitor}")

            # Event details
            event_summary = event.get("summary", "No Title")
            event_start_str = event["start"].get("dateTime", event["start"].get("date"))
            event_start = datetime.datetime.fromisoformat(event_start_str)
            event_start = event_start.astimezone(pytz.UTC)

            # UI setup
            frame = tk.Frame(root, bg=BG_COLOR)
            frame.pack(expand=True)
            logger.debug(f"UI frame packed for monitor: {monitor}")

            font_size1 = 100 if monitor.width > 1920 else 60
            font_size2 = 40 if monitor.width > 1920 else 25

            intro_label = tk.Label(
                frame,
                text="You have an upcoming calendar event:",  # Will be updated in real-time
                font=("Arial", int(font_size2 * 2 / 3)),
                fg=TEXT_COLOR_SECONDARY,
                bg=BG_COLOR,
            )
            intro_label.pack(pady=20)

            title_label = tk.Label(
                frame,
                text=event_summary,
                font=("Arial", font_size1, "bold"),
                fg=TEXT_COLOR_PRIMARY,
                bg=BG_COLOR,
            )
            title_label.pack(pady=20)

            time_label = tk.Label(
                frame,
                text="",  # Will be updated in real-time
                font=("Arial", font_size2),
                fg=TEXT_COLOR_SECONDARY,
                bg=BG_COLOR,
            )
            time_label.pack(pady=(20, 100))

            def on_dismiss():
                logger.info(f"Dismiss button clicked for monitor {monitor}")
                dismiss_event.set()  # Signal all windows to close

            dismiss_button = tk.Button(
                frame,
                text="Dismiss",
                font=("Arial", 30),
                command=on_dismiss,
                bg=colors["Gray"][600],
                fg="white",
                relief="flat",
                padx=50,  # Increased x padding
            )
            dismiss_button.pack(pady=20)

            countdown_label = tk.Label(
                frame,
                text="",
                font=("Arial", 12),
                fg=TEXT_COLOR_SECONDARY,
                bg=BG_COLOR,
            )
            countdown_label.pack(pady=0)

            start_time = datetime.datetime.now(pytz.UTC)
            end_time = start_time + datetime.timedelta(seconds=DEFAULT_HOLD_DURATION)

            def update_time_remaining():
                current_time = datetime.datetime.now(pytz.UTC)
                time_until_event = event_start - current_time
                minutes, seconds = divmod(int(time_until_event.total_seconds()), 60)
                hours = minutes // 60
                if time_until_event.total_seconds() > 0:
                    if hours > 0:
                        time_remaining = f"{hours} hours"
                    elif minutes > 0:
                        time_remaining = f"{minutes} minutes"
                    else:
                        time_remaining = f"{seconds} seconds"
                else:
                    time_remaining = "Now"

                start_time_str = (
                    datetime.datetime.fromisoformat(event_start_str)
                    .strftime("%I:%M %p")
                    .lstrip("0")
                )

                time_label.config(
                    text=f"Starting in {time_remaining} at {start_time_str}"
                )

                # Update countdown timer
                time_left = int((end_time - current_time).total_seconds())
                if time_left > 0:
                    countdown_label.config(
                        text=f"(This alert will close in {time_left} seconds)"
                    )
                else:
                    root.destroy()
                    return

                # Check if dismiss event is set
                if dismiss_event.is_set():
                    root.destroy()
                    return

                root.after(50, update_time_remaining)

            update_time_remaining()
            logger.info(f"Starting main loop for monitor: {monitor}")

            # Diagnostics: Print window state and attributes
            root.update()
            logger.debug(f"Window state for monitor {monitor}: {root.state()}")
            logger.debug(
                f"Window is mapped (visible) for monitor {monitor}: {root.winfo_ismapped()}"
            )

            root.mainloop()
        except Exception as e:
            logger.error(f"Exception occurred for monitor {monitor}: {e}")

    # Custom thread class to catch exceptions
    class ThreadWithException(threading.Thread):
        def run(self):
            try:
                if self._target:
                    self._target(*self._args, **self._kwargs)
            except Exception as e:
                logger.error(
                    f"Exception in thread {self.name} for monitor {self._args[0]}: {e}"
                )

    # Create a window for each monitor
    threads = [
        ThreadWithException(target=create_window, args=(monitor,))
        for monitor in monitors
    ]

    sound_thread = ThreadWithException(
        target=winsound.PlaySound, args=("SystemExit", winsound.SND_ALIAS)
    )

    threads.append(sound_thread)

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    logger.info("All threads have finished.")


def main():
    event = {
        "summary": "Test Event",
        "start": {"dateTime": "2024-08-17T12:00:00"},
    }
    logger.info("Starting notification display.")
    display_event_on_all_screens(event)


if __name__ == "__main__":
    main()
