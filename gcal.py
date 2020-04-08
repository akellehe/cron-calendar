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
    calendar_list_entry = {
        'id': calendar_id
    }
    return service.calendarList().insert(body=calendar_list_entry).execute()


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
        create_calendar(service, calendar_id)


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
        'id': cron_event.command,
        "start":  {
            "dateTime": cron_event.datetime.isoformat(),
        },
        "end": {
            "dateTime": (cron_event.datetime + datetime.timedelta(minutes=10)).isoformat(),
        },
        "recurrence": [
            "RRULE:FREQ=MONTHLY"
        ]
    }


def add_calendar_events(events):
    pass


def authenticate():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    user = getpass.getuser()
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


if __name__ == '__main__':
    main()
