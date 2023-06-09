import datetime
import time

# get current date like year month day
print("Current date like year month day: " + time.strftime("%Y-%m-%d"))
now = datetime.datetime.now()
print("Current date and time : " + str(now))


