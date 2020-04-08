import time
import datetime
import collections
import getpass

import crontabs


CronEvent = collections.namedtuple("CronEvent", ["command", "starting_date", "recurrence_rule"])


def not_star(*args):
    return not any([arg == '*' for arg in args])


def are_star(*args):
    return all([arg == '*' for arg in args])


def is_annual(ci):
    return not_star(ci.minute, ci.hour, ci.dom, ci.month) and are_star(ci.dow)


def is_monthly(ci):
    return not_star(ci.minute, ci.hour, ci.dom) and are_star(ci.month, ci.dow)


def is_weekly(ci):
    return not_star(ci.minute, ci.hour) and are_star(ci.dom, ci.month) and not_star(ci.dow)


def is_daily(ci):
    return (not_star(ci.hour) and are_star(ci.dom, ci.month, ci.dow)) or (
        are_star(ci.hour, ci.dom, ci.month, ci.dow))


def to_list(value):
    return ",".join([str(i) for i in expand(value)])


def expand(value):
    values = value.render().split(',')
    final_values = []
    for value_range in values:
        if '-' in value_range:
            start, stop = value_range.split('-')
            for i in range(int(start), int(stop) + 1):
                final_values.append(i)
        else:
            try:
                final_values.append(int(value_range))
            except ValueError:
                return None  # It was a *
    return final_values


def find_stopping_date(ci):
    for next_run_at in ci.schedule(date_from=time.time()):
        break
    if is_daily(ci): return next_run_at + datetime.timedelta(days=1)
    if is_weekly(ci): return next_run_at + datetime.timedelta(days=7)
    if is_monthly(ci): return next_run_at.replace(month=next_run_at.month + 1)
    if is_annual(ci): return next_run_at.replace(year=next_run_at.year + 1)


def find_starting_date(ci):
    for next_run_at in ci.schedule(date_from=time.time()):
        return next_run_at


def non_recurrent_datetimes_from_crontab(ci):
    stopping_date = find_stopping_date(ci)
    non_recurrent_datetimes = []
    for dt in ci.schedule(date_from=time.time()):
        if dt >= stopping_date:
            break
        non_recurrent_datetimes.append(dt)
    return non_recurrent_datetimes


def numbered_to_lettered_dow(ci):
    days_of_the_week = expand(ci.dow)
    mapping = {0: 'SU', 1: 'MO', 2: 'TU', 3: 'WE', 4: 'TH', 5: 'FR', 6: 'SA'}
    return ",".join([mapping[dow] for dow in days_of_the_week])


def recurrence_prefix(ci):
    print('--------------------------------')
    print(ci)
    print(ci.description())
    if is_daily(ci): return "RRULE:FREQ=DAILY;INTERVAL=1"
    elif is_weekly(ci): return "RRULE:FREQ=WEEKLY;INTERVAL=1"
    elif is_monthly(ci): return "RRULE:FREQ=MONTHLY;INTERVAL=1"
    elif is_annual(ci): return "RRULE:FREQ=ANNUALLY;INTERVAL=1"


def get_star_list(end):
    return ",".join([str(i) for i in range(end)])


def recurrence_suffixes(ci):
    suffixes = []
    if ci.minutes != '*':
        suffixes.append("BYMINUTE=" + to_list(ci.minutes))
    else:
        suffixes.append("BYMINUTE=" + get_star_list(60))
    if ci.hours != '*':
        suffixes.append("BYHOUR=" + to_list(ci.hours))
    else:
        suffixes.append("BYHOUR=" + get_star_list(24))
    if ci.dom != '*':
        suffixes.append("BYMONTHDAY=" + to_list(ci.dom))
    if ci.months != '*':
        suffixes.append("BYMONTH=" + to_list(ci.months))
    if ci.dow != '*':
        suffixes.append("BYDAY=" + numbered_to_lettered_dow(ci))
    return suffixes


def recurrence_rule_from_crontab(ci):
    prefix = recurrence_prefix(ci)
    suffixes = recurrence_suffixes(ci)
    return ";".join([prefix] + suffixes)


def get_events():
    user = getpass.getuser()
    events = []
    for ct in crontabs.CronTab(user=user).crons:
        events.append(
            CronEvent(ct.command,
                      find_starting_date(ct),
                      recurrence_rule_from_crontab(ct)))
    return events

