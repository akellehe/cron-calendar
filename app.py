from cron import get_events
from gcal import build, authenticate, create_cron_calendar_if_not_exists, cron_event_to_calendar_event, list_calendar_ids, add_calendar_events



creds = authenticate()
service = build('calendar', 'v3', credentials=creds)
print(list_calendar_ids(service))
calendar = create_cron_calendar_if_not_exists(service)
print('Created calendar', calendar)
add_calendar_events(service, calendar, [cron_event_to_calendar_event(event) for event in get_events()])
