from datetime import datetime


def getDayDifference(start_time, current_time):
    delta = datetime.fromtimestamp(current_time).timestamp() - datetime.fromtimestamp(start_time).timestamp()
    day = int(datetime.fromtimestamp(delta).strftime("%j"))
    return day