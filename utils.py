from datetime import datetime

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def seconds_to_hours(seconds):
    return round(seconds / 3600, 2)


def calculate_amount(hours, rate):
    return round(hours * rate, 2)
