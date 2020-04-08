from __future__ import print_function
import collections
import getpass
import json
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def create_calendar(service, calendar_id):
    calendar = {
        'summary': calendar_id,
        'timeZone': 'UTC'
    }
    return service.calendars().insert(body=calendar).execute()


def list_calendar_ids(service):
    calendar_list = service.calendarList().list().execute()
    calendar_ids = set([])
    for calendar in calendar_list.get('items'):
        calendar_ids.add(calendar.get('id'))
    return calendar_ids


def create_cron_calendar_if_not_exists(service):
    user = getpass.getuser()
    calendar_ids = list_calendar_ids(service)
    calendar_id = f'{user}.cron'
    if calendar_id not in calendar_ids:
        return create_calendar(service, calendar_id)


def cron_recurrence_rule_to_gcal_recurrence_rule(recurrence_rule):
    if recurrence_rule == 'annual':
        return "RRULE:FREQ=ANNUALLY"
    elif recurrence_rule == 'daily':
        return "RRULE:FREQ=DAILY"
    elif recurrence_rule == 'monthly':
        return "RRULE:FREQ=MONTLY"
    elif recurrence_rule == 'weekly':
        return "RRULE:FREQ=WEEKLY"


def cron_event_to_calendar_event(cron_event):
    return {
        "summary": cron_event.command,
        "description": cron_event.schedule + " Recurrence rule: " + cron_event.recurrence_rule,
        "start":  {
            "dateTime": cron_event.starting_date.isoformat(),
            "timeZone": "America/New_York"
        },
        "end": {
            "dateTime": (cron_event.starting_date + datetime.timedelta(minutes=10)).isoformat(),
            "timeZone": "America/New_York"
        },
        "recurrence": [
            cron_event.recurrence_rule
        ]
    }


def add_calendar_events(service, calendar, events):
    for evt in events:
        print('Creating event for')
        print(evt)
        event = service.events().insert(calendarId=calendar.get('id'), body=evt).execute()
        print(event.get('htmlLink'))


def authenticate():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

