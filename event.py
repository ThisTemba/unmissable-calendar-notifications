from typing import TypedDict, Optional


class EventDateTime(TypedDict):
    dateTime: str
    timeZone: Optional[str]


class CreatorOrganizer(TypedDict):
    email: str
    self: Optional[bool]


class Reminders(TypedDict):
    useDefault: bool


class CalendarEvent(TypedDict):
    created: str
    creator: CreatorOrganizer
    end: EventDateTime
    etag: str
    eventType: str
    htmlLink: str
    iCalUID: str
    id: str
    kind: str
    organizer: CreatorOrganizer
    reminders: Reminders
    sequence: int
    start: EventDateTime
    status: str
    summary: str
    updated: str
