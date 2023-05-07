import psycopg2
from random import randint
from faker import Faker
from datetime import time
fake = Faker('es_ES')


num_ciutats = 100
num_empleats = 100


def create_ciutats(cur):
  print("%d ciutats will be inserted." % num_ciutats)
  cur.execute("DROP TABLE IF EXISTS Ciutats CASCADE")
  cur.execute("""CREATE TABLE Ciutats(
        nom varchar(50) NOT NULL,
        codi_postal numeric(5,0) NOT NULL,
        PRIMARY KEY (nom, codi_postal)
    )""")

  cities_inserted = 0
  while cities_inserted < num_ciutats:
    print(cities_inserted+1, end = '\r')
    nom = fake.city()
    codi_postal = fake.random_int(min=10000, max=99999)
    # Check if the city already exists in the table
    cur.execute("SELECT COUNT(*) FROM Ciutats WHERE nom = %s ", (nom,))
    count = cur.fetchone()[0]

    if count == 0:
        cities_inserted += 1
        try:
            cur.execute("INSERT INTO ciutats VALUES ('%s', '%s')" % (nom, codi_postal))
        except psycopg2.IntegrityError as e:
            conn.rollback()
            print("Error inserting (%s, %s). Error information: %s" % (nom, codi_postal, e))
        conn.commit()
        cities_inserted += 1



def create_empleats(cur):
  print("%d empleats will be inserted." % num_empleats)
  cur.execute("DROP TABLE IF EXISTS Empleats CASCADE")
  cur.execute("""CREATE TABLE Empleats(
        dni varchar(9) NOT NULL,
        tipus varchar(20) NOT NULL,
        sou numeric (7,2) NOT NULL,
        nom varchar(20) NOT NULL,
        cognoms varchar(40) NOT NULL,
        compte_bancari varchar(24) NOT NULL,
        telefon numeric(9) NOT NULL,
        naixement date NOT NULL,
        sexe char(1) NOT NULL,
        horaris varchar(50) NOT NULL,
        nom_ciutat varchar(50) NOT NULL,
        codi_postal numeric(5,0) NOT NULL,
        PRIMARY KEY (dni),
        -- Pot existir un cas molt molt especific en el que una parella vulgui cobrar el --seu sou en el mateix compte bancari, per aquest motiu no hi ha una unique_key a --compte bancari 
        UNIQUE(telefon),
        FOREIGN KEY (nom_ciutat, codi_postal) references Ciutats(nom, codi_postal) on update cascade on delete restrict
    )""")

  empleats_inserted = 0
  while empleats_inserted < num_empleats:
    print(empleats_inserted+1, end = '\r')
    # Generate unique dni
    dni = str(randint(10000000, 99999999)) + fake.random_letter()
    tipus = fake.random_element(elements=('encarregat', 'treballador'))
    sou = fake.pydecimal(left_digits=5, right_digits=2, positive=True)
    nom = fake.first_name()
    cognoms = fake.last_name() + ' ' + fake.last_name()
    telefon = fake.unique.random_number(digits=9) 
    compte_bancari = fake.iban()
    naixement = fake.date_of_birth(minimum_age=16, maximum_age=90)
    sexe = fake.random_element(elements=('H', 'D'))
    # Generate a time range for the day shift (8:00 - 20:00)
    start_time = time(hour=8)
    end_time = time(hour=20)
    shift_range = f'{start_time.strftime("%H:%M")} - {end_time.strftime("%H:%M")}'
    # Use the shift_range in the Empleats table insert statement
    horaris = fake.random_element(elements=(shift_range,))

    # There can't be more than 1 encarregat on the same city
    if tipus == 'encarregat':
        cur.execute("SELECT COUNT(*) FROM Empleats WHERE tipus = 'encarregat' AND nom_ciutat = '%s';" % (nom_ciutat,))
        count_encarregats = cur.fetchone()[0]
        if count_encarregats > 0:
            tipus = 'treballador'

    # Select a random city from the Ciutats table
    cur.execute("SELECT nom FROM Ciutats ORDER BY RANDOM() LIMIT 1")
    nom_ciutat   = cur.fetchone()[0]
    cur.execute("SELECT codi_postal FROM Ciutats WHERE nom = '%s';" % (nom_ciutat,))
    codi_postal = cur.fetchone()[0]

    # Check if the city already exists in the table
    cur.execute("SELECT COUNT(*) FROM Empleats WHERE nom = %s AND dni = %s", (nom,dni))
    count_dni = cur.fetchone()[0]

    if count_dni == 0:
        empleats_inserted += 1
        try:
            cur.execute("INSERT INTO Empleats VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (dni, tipus, sou, nom, cognoms, compte_bancari, telefon, naixement, sexe, horaris, nom_ciutat, codi_postal))
        except psycopg2.IntegrityError as e:
            conn.rollback()
            print("Error inserting (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s). Error information: %s" % (dni, tipus, sou, nom, cognoms, compte_bancari, telefon, naixement, sexe, horaris, nom_ciutat, codi_postal, e))
        conn.commit()
        empleats_inserted += 1


# Programa principal
conn = psycopg2.connect(
    host="ubiwan.epsevg.upc.edu",
    database="est_a4033441",
    user="est_a4033441",
    password="dB.a4033441",
    options=f'-c search_path=practica'
)
cur = conn.cursor()

create_ciutats(cur)
create_empleats(cur)

cur.close()
conn.close()
