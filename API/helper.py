

def getDayofGame(start_time, current_time):
    delta = current_time.timestamp() - start_time.timestamp()
    day = round(delta / 3600 * 24)
    return day
