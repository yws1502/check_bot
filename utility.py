import datetime

def compare_time(compare_hour, compare_min):
    current_time = datetime.datetime.now()
    if compare_hour != current_time.hour or compare_min != current_time.minute:
        return False
    return True

def get_date():
    current_time = datetime.datetime.now()
    weekday = current_time.weekday()
    month = f"{current_time.month}".zfill(2)
    day = f"{current_time.day}".zfill(2)
    hour = current_time.hour
    min = current_time.minute

    return [month, day, weekday, hour, min]
