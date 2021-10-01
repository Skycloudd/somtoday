def pretty_datetime(dt):
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute = dt.minute

    return f"{day}/{month}/{year} at {hour}:{minute}"


def pretty_timedelta(td):
    minutes = (td.seconds % 3600) // 60
    hours = td.seconds // 3600

    if hours > 0:
        output = f"{hours}h {minutes}m"
    else:
        output = f"{minutes}m"

    return output
