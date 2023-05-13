import random
from datetime import datetime

hour = random.randint(0, 23)
fake_hour = datetime.strptime(str(hour), '%H').strftime('%I:%M')

print(fake_hour)
