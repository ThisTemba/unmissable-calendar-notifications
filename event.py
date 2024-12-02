from typing import TypedDict, Optional


class EventDateTime(TypedDict):
    dateTime: str  # ISO 8601
    timeZone: Optional[str]


class EventDate(TypedDict):
    date: str


class CreatorOrganizer(TypedDict):
    email: str
    self: Optional[bool]


class Reminders(TypedDict):
    useDefault: bool


class CalendarEvent(TypedDict):
    created: str
    creator: CreatorOrganizer
    end: EventDateTime | EventDate
    etag: str
    eventType: str
    htmlLink: str
    iCalUID: str
    id: str
    kind: str
    organizer: CreatorOrganizer
    reminders: Reminders
    sequence: int
    start: EventDateTime | EventDate
    status: str
    summary: str
    updated: str
