from cron import get_events
from gcal import build, authenticate, create_cron_calendar_if_not_exists



def cron_event_to_calendar_entry(cron_event):


creds = authenticate()
service = build('calendar', 'v3', credentials=creds)
create_cron_calendar_if_not_exists(service)
