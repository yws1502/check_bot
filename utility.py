import datetime

def check_time(compare_hour, compare_min):
    current_time = datetime.datetime.now()
    if current_time.weekday() not in [5, 6] or compare_hour != current_time.hour or compare_min != current_time.minute:
        return False
    return True