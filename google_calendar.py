import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

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

def get_service():
    return 


def get_upcoming_events(max_results=10):
    credentials = get_credentials()
    service = build("calendar", "v3", credentials=credentials)
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
