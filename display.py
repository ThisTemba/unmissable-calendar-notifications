import datetime
import threading
import tkinter as tk

import pytz
from screeninfo import get_monitors

from colors import colors
bg_color = colors["Stone"][950]

def display_event_on_all_screens(event, hold_duration):
    """Displays the latest event on all screens with an improved UI."""
    monitors = get_monitors()
    dismiss_event = threading.Event()  # Shared event to signal dismissal

    def create_window(monitor):
        root = tk.Tk()
        root.overrideredirect(True)
        root.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
        root.configure(background=bg_color)

        # Event details
        event_summary = event.get("summary", "No Title")
        event_start_str = event["start"].get("dateTime", event["start"].get("date"))
        event_start = datetime.datetime.fromisoformat(event_start_str)
        event_start = event_start.astimezone(pytz.UTC)

        # UI setup
        frame = tk.Frame(root, bg=bg_color)
        frame.pack(expand=True)

        title_label = tk.Label(
            frame,
            text="Upcoming Event!",
            font=("Arial", 80, "bold"),
            fg=colors["Amber"][400],
            bg=bg_color,
        )
        title_label.pack(pady=20)

        summary_label = tk.Label(
            frame,
            text=event_summary,
            font=("Arial", 60),
            fg=colors["Amber"][50],
            bg=bg_color,
        )
        summary_label.pack(pady=20)

        time_label = tk.Label(
            frame,
            text="",  # Will be updated in real-time
            font=("Arial", 50),
            fg=colors["Orange"][400],
            bg=bg_color,
        )
        time_label.pack(pady=20)

        countdown_label = tk.Label(
            frame,
            text="",
            font=("Arial", 30),
            fg="#fef3c7",  # Amber 100
            bg=bg_color,
        )
        countdown_label.pack(pady=10)

        start_time = datetime.datetime.now(pytz.UTC)
        end_time = start_time + datetime.timedelta(seconds=hold_duration)

        def update_time_remaining():
            current_time = datetime.datetime.now(pytz.UTC)
            time_until_event = event_start - current_time
            minutes, seconds = divmod(int(time_until_event.total_seconds()), 60)
            if time_until_event.total_seconds() > 0:
                if minutes > 0:
                    time_remaining = f"{minutes} minutes"
                else:
                    time_remaining = f"{seconds} seconds"
            else:
                time_remaining = "Now"

            time_label.config(text=f"Starting in {time_remaining}")

            # Update countdown timer
            time_left = int((end_time - current_time).total_seconds())
            if time_left > 0:
                countdown_label.config(text=f"Window closes in {time_left} seconds")
            else:
                root.destroy()
                return

            # Check if dismiss event is set
            if dismiss_event.is_set():
                root.destroy()
                return

            root.after(1000, update_time_remaining)

        def on_dismiss():
            dismiss_event.set()  # Signal all windows to close

        dismiss_button = tk.Button(
            frame,
            text="Dismiss",
            font=("Arial", 30),
            command=on_dismiss,
            bg=colors["Gray"][600],
            fg="white",
            relief="flat",
            padx=50  # Increased x padding
        )
        dismiss_button.pack(pady=40)

        update_time_remaining()
        root.mainloop()

    # Create a window for each monitor
    threads = [
        threading.Thread(target=create_window, args=(monitor,)) for monitor in monitors
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
