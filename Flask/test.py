from faker import Faker
import psycopg2

fake = Faker('es_ES')

conn = psycopg2.connect(
    host="ubiwan.epsevg.upc.edu",
    database="est_a4033441",
    user="est_a4033441",
    password="dB.a4033441",
    options=f'-c search_path=practica'
)

cursor = conn.cursor()

# add 1 password for each user
cursor.execute("SELECT dni FROM clients")
data = cursor.fetchall()

count = 0
for i in data:
    
    print(count+1, end = '\r')
    cursor.execute("UPDATE clients SET passwords = %s WHERE dni = %s", (fake.password(), i[0]))
    count += 1

conn.commit()
cursor.close()
conn.close()



