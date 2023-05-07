import psycopg2
from random import randint
from faker import Faker
from datetime import time
fake = Faker('es_ES')


num_ciutats = 100
num_empleats = 100
num_gimnasos = 100


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
  current_ciutat = 0
  
  while empleats_inserted < num_empleats:
    print(empleats_inserted+1, end = '\r')
    # Generate unique dni
    dni = str(randint(10000000, 99999999)) + fake.random_letter()
    #tipus = fake.random_element(elements=('encarregat', 'treballador'))
    tipus = 'encarregat'
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

    num_ciutats = cur.execute("SELECT COUNT(*) FROM Ciutats;")
    num_ciutats = cur.fetchone()[0]
    #print(num_ciutats)

    # Make each city of the table Ciutats appear at least once in the Empleats table
    if current_ciutat < num_ciutats:
        cur.execute("SELECT nom FROM Ciutats ORDER BY nom LIMIT 1 OFFSET %s", (current_ciutat,))
        nom_ciutat   = cur.fetchone()[0]
        cur.execute("SELECT codi_postal FROM Ciutats WHERE nom = '%s';" % (nom_ciutat,))
        codi_postal = cur.fetchone()[0]
        #current_ciutat += 1

    # Select a random city from the Ciutats table
    cur.execute("SELECT nom FROM Ciutats ORDER BY RANDOM() LIMIT 1")
    nom_ciutat   = cur.fetchone()[0]
    cur.execute("SELECT codi_postal FROM Ciutats WHERE nom = '%s';" % (nom_ciutat,))
    codi_postal = cur.fetchone()[0]

    # There can't be more than 1 encarregat on the same city
    if empleats_inserted > 0:
        if tipus == 'encarregat':
            cur.execute("SELECT COUNT(*) FROM Empleats WHERE tipus = 'encarregat' AND nom_ciutat = '%s';" % (nom_ciutat,))
            count_encarregats = cur.fetchone()[0]
            if count_encarregats > 0:
                tipus = 'treballador'

    # Check if an employee with the same dni already exists in the table
    cur.execute("SELECT COUNT(*) FROM Empleats WHERE nom = %s AND dni = %s", (nom,dni))
    count_dni = cur.fetchone()[0]

    if count_dni == 0:
        #empleats_inserted += 1
        try:
            cur.execute("INSERT INTO Empleats VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (dni, tipus, sou, nom, cognoms, compte_bancari, telefon, naixement, sexe, horaris, nom_ciutat, codi_postal))
        except psycopg2.IntegrityError as e:
            conn.rollback()
            print("Error inserting (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s). Error information: %s" % (dni, tipus, sou, nom, cognoms, compte_bancari, telefon, naixement, sexe, horaris, nom_ciutat, codi_postal, e))
        conn.commit()
        empleats_inserted += 1
        current_ciutat += 1


def create_gimnasos(cur):
  print("%d Gimnasos will be inserted." % num_gimnasos)
  cur.execute("DROP TABLE IF EXISTS Gimnasos CASCADE")
  cur.execute("""CREATE TABLE Gimnasos (
        codi varchar(8) NOT NULL,
        adreca varchar(255) NOT NULL,
        telefon numeric(9,0) NOT NULL,
        correu_electronic varchar(64) NOT NULL,
        nom_ciutat varchar(50) NOT NULL,
        codi_postal numeric(5,0) NOT NULL,
        encarregat varchar(9) NOT NULL,
        PRIMARY KEY (codi),
        UNIQUE(adreca, nom_ciutat, codi_postal),
        UNIQUE(telefon),
        UNIQUE(correu_electronic),
        FOREIGN KEY (nom_ciutat, codi_postal) REFERENCES Ciutats(nom, codi_postal) ON UPDATE CASCADE ON DELETE RESTRICT,
        FOREIGN KEY (encarregat) REFERENCES Empleats(dni) ON UPDATE CASCADE ON DELETE RESTRICT
    );""")

  gimnasos_inserted = 0
  while gimnasos_inserted < num_gimnasos:
    print(gimnasos_inserted+1, end = '\r')

    codi = ''.join(fake.random_letters(length=4)) + str(fake.random_int(min=1000, max=9999))

    adreca = fake.street_address()
    telefon = fake.random_int(min=600000000, max=699999999)
    correu_electronic = fake.email()

    # Select a random city from the Ciutats table
    cur.execute("SELECT nom FROM Ciutats ORDER BY RANDOM() LIMIT 1")
    nom_ciutat   = cur.fetchone()[0]
    cur.execute("SELECT codi_postal FROM Ciutats WHERE nom = '%s';" % (nom_ciutat,))
    codi_postal = cur.fetchone()[0]

    # get the encarregat from the specific city
    cur.execute("SELECT dni FROM Empleats WHERE tipus = 'encarregat' AND nom_ciutat = '%s';" % (nom_ciutat,))

    r = cur.fetchone()

    if r is not None:
        try:
            encarregat = r[0]
            cur.execute("INSERT INTO Gimnasos VALUES (%s, %s, %s, %s, %s, %s, %s)", (codi, adreca, telefon, correu_electronic, nom_ciutat, codi_postal, encarregat))

        except psycopg2.IntegrityError as e:
            conn.rollback()
            print("Error inserting (%s, %s, %s, %s, %s, %s, %s). Error information: %s" % (codi, adreca, telefon, correu_electronic, nom_ciutat, codi_postal, encarregat, e))
        conn.commit()
        gimnasos_inserted += 1


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
create_gimnasos(cur)

cur.close()
conn.close()
