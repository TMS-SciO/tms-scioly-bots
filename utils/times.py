import datetime


def format_relative(dt):
    return format_dt(dt, 'R')


def format_dt(dt, style=None):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)

    if style is None:
        return f'<t:{int(dt.timestamp())}>'
    return f'<t:{int(dt.timestamp())}:{style}>'
