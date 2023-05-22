import psycopg2
from random import randint
import random
from faker import Faker
from faker_food import FoodProvider
import datetime as dt
from datetime import time, datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta


conn = psycopg2.connect(
    host="ubiwan.epsevg.upc.edu",
    database="est_a4033441",
    user="est_a4033441",
    password="dB.a4033441",
    options=f'-c search_path=practica'
)

cur = conn.cursor()


cur.execute("SELECT * FROM information_schema.tables WHERE table_schema = 'practica';")

tables = cur.fetchall()

total = 0

for table in tables:
    nom = table[2]
    cur.execute("SELECT count(*) FROM %s;" % nom)
    result = cur.fetchone()[0]
    print(nom, " --> ", result)
    total += result

print("--------------------")
print("TOTAL: ", total)
print("--------------------")