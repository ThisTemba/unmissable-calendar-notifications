import datetime
import os.path
import threading
import tkinter as tk
from screeninfo import get_monitors
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from colors import colors

# Define the scope and screen hold duration
SCOPES = ["https://www.googleapis.com/auth/calendar.events.readonly"]
SCREEN_HOLD_DURATION = 30  # seconds

bg_color = colors["Stone"][950]


def get_credentials():
    """Obtains user credentials for Google Calendar API."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def get_upcoming_events(service, max_results=10):
    """Fetches upcoming events from Google Calendar."""
    now = datetime.datetime.utcnow().isoformat() + "Z"
    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    return events_result.get("items", [])


def display_event_on_all_screens(event):
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
            fg="#fbbf24",  # Amber 400
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
        end_time = start_time + datetime.timedelta(seconds=SCREEN_HOLD_DURATION)

        def update_time_remaining():
            current_time = datetime.datetime.now(pytz.UTC)
            time_until_event = event_start - current_time
            minutes, seconds = divmod(int(time_until_event.total_seconds()), 60)
            if time_until_event.total_seconds() > 0:
                if minutes > 0:
                    time_remaining = f"{minutes} minutes and {seconds} seconds"
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
            bg="#4b5563",  # Gray 600
            fg="white",
            relief="flat",
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


def main():
    """Main function to fetch and display the latest calendar event."""
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    events = get_upcoming_events(service, max_results=10)
    if not events:
        print("No upcoming events found.")
        return

    latest_event = events[0]
    display_event_on_all_screens(latest_event)

    # Print all upcoming events
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(f"{start}: {event.get('summary', 'No Title')}")


if __name__ == "__main__":
    main()
