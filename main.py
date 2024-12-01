import datetime
import os.path
import threading
import tkinter as tk
from screeninfo import get_monitors

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.events.readonly"]

SCREEN_HOLD_DURATION = 3  # seconds

def get_credentials():
    """Obtains user credentials from token.json or initiates an OAuth flow."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def get_upcoming_events(service, max_results=10):
    """Fetches upcoming events from the user's primary calendar."""
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print(f"Getting the upcoming {max_results} events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    return events


def display_event_on_all_screens(event):
    """Displays the latest event on all screens for 3 seconds."""
    monitors = get_monitors()
    windows = []

    def create_window(monitor):
        root = tk.Tk()
        root.overrideredirect(True)  # Remove window decorations
        root.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
        root.configure(background='black')

        # Create a label to display the event
        event_summary = event.get('summary', 'No Title')
        event_start = event['start'].get('dateTime', event['start'].get('date'))
        label = tk.Label(
            root,
            text=f"{event_summary}\n{event_start}",
            font=("Helvetica", 48),
            fg="white",
            bg="black",
            justify="center",
        )
        label.pack(expand=True)

        # Close the window after 3 seconds
        root.after(SCREEN_HOLD_DURATION*1000, root.destroy)
        root.mainloop()

    # Start a thread for each monitor
    threads = []
    for monitor in monitors:
        t = threading.Thread(target=create_window, args=(monitor,))
        threads.append(t)
        t.start()

    # Wait for all windows to close
    for t in threads:
        t.join()


def main():
    """Shows basic usage of the Google Calendar API by printing upcoming events."""
    creds = get_credentials()

    try:
        service = build("calendar", "v3", credentials=creds)
        events = get_upcoming_events(service, max_results=10)

        if not events:
            print("No upcoming events found.")
            return

        latest_event = events[0]
        display_event_on_all_screens(latest_event)

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(f"{start}: {event.get('summary', 'No Title')}")

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
