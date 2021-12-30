import time
from datetime import datetime

def calculate_worker(current_time):
    result = (get_timestamp() - current_time)
    return float(str(result)[:5])

def delay(sec: int = 0):
    time.sleep(sec)

def get_timestamp():
    return time.time()

def timenow():
    now = datetime.now()
    return now.strftime("%H:%M:%S")

def datenow():
    now = datetime.now()
    return now.strftime("%d-%m-%Y")