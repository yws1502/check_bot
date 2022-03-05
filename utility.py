import datetime

def check_time(compare_hour, compare_min):
    _, _, weekday, hour, min = get_date()
    
    if weekday not in [5, 6] or compare_hour != hour or compare_min != min:
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
