from datetime import datetime, timedelta
import random

# 1. Generate random time
start = random.randint(7, 21)  # Hours

# 2. Convert to datetime object
time_str = f"{start}:00"

duracio = random.randint(20, 120)  

time_obj = datetime.strptime(time_str, "%H:%M")
new_time_obj = time_obj + timedelta(minutes=duracio)

new_time_str = datetime.strftime(new_time_obj, "%H:%M")

start_time = str(time_str)
end_time = str(new_time_str)
final_time = start_time + " - " + end_time
print(final_time)  
