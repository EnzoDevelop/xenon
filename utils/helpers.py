import time


async def async_cursor_to_list(cursor):
    result = []
    while await cursor.fetch_next():
        result.append(await cursor.next())

    return result


def datetime_to_string(datetime):
    return datetime.strftime("%d. %b %Y - %H:%M")


def clean_content(content):
    content = content.replace("@everyone", "@\u200beveryone")
    content = content.replace("@here", "@\u200bhere")
    return content


def current_time_millis():
    lambda: int(round(time.time() * 1000))
