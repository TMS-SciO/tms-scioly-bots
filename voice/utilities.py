from __future__ import annotations


def pluralize(text: str, count: int) -> str:
    return f"{text}{'s' if count > 1 else ''}"


def readable_bool(value: bool) -> str:
    return str(value).replace("True", "yes").replace("False", "no")


def format_seconds(
        _seconds: float, /,
        *,
        friendly: bool = False
) -> str:
    _minutes, _seconds = divmod(round(_seconds), 60)
    _hours, _minutes = divmod(_minutes, 60)
    _days, _hours = divmod(_hours, 24)

    days, hours, minutes, seconds = round(_days), round(_hours), round(_minutes), round(_seconds)

    if friendly:
        return f"{f'{days}d ' if days else ''}" \
               f"{f'{hours}h ' if hours or days else ''}" \
               f"{minutes}m " \
               f"{seconds}s"

    return f"{f'{days:02d}:' if days else ''}" \
           f"{f'{hours:02d}:' if hours or days else ''}" \
           f"{minutes:02d}:" \
           f"{seconds:02d}"


def truncate(text: str | int, characters: int) -> str:
    text = str(text)
    return text if len(text) < characters else f"{text[:characters]}..."
