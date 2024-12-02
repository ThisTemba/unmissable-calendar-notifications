import os.path
from datetime import datetime, timezone
from pprint import pprint

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from event import CalendarEvent

SCOPES = ["https://www.googleapis.com/auth/calendar.events.readonly"]


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


def get_next_event() -> CalendarEvent:
    """Fetches the next event from the user's Google Calendar."""
    credentials = get_credentials()
    service = build("calendar", "v3", credentials=credentials)
    now = datetime.now(timezone.utc).isoformat()
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    events = filter_events(events)
    next_event = events[0] if events else None
    return next_event


def filter_events(events):
    """
    Keep events with start times in the future
    * ignore all-day events
    * ignore events that have already started and are in progress
    """
    now = datetime.now(timezone.utc)
    events_new = []
    for event in events:
        # ignore all-day events
        start_time_str = event["start"].get("dateTime")
        if not start_time_str:
            continue
        # ignore events that have already started
        event_start_dt = datetime.fromisoformat(start_time_str)
        if event_start_dt < now:
            continue

        events_new.append(event)
    return events_new


def main():
    next_event = get_next_event()
    if next_event:
        pprint(next_event)
        print(f"Next event: {next_event['summary']}")
    else:
        print("No upcoming events found.")
    return


if __name__ == "__main__":
    main()
