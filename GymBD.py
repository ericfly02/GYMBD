import psycopg2
from random import randint
import random
from faker import Faker
from faker_food import FoodProvider
import datetime as dt
from datetime import time, datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta

fake = Faker('es_ES')
fake.add_provider(FoodProvider)

####Estas son los datos que meteremos
num_ciutats = 300
num_empleats = 6000
num_treballadors = 10000
num_gimnasos = 350
num_sales = 5000
num_classes = 10000
num_aliments = 200
num_dietes = 200
num_rutines = 200
num_clients = 30000
num_quantificador_dietes = 10000
num_quantificador_rutines = 10000
num_entrenaments = 50000
num_apats = 50000
num_participacions = 10000
sales_per_exercici = 1000
num_exercicis = 300
##datos para hacer pruebas
num_ciutats = 5
num_empleats = 120
num_treballadors = 140
num_gimnasos = 6
num_sales = 50
num_classes = 100
num_aliments = 20
num_dietes = 20
num_rutines = 100
num_clients = 300
num_quantificador_dietes = 100
num_quantificador_rutines = 100
num_participacions = 100
num_entrenaments = 5
num_apats = 50
sales_per_exercici = 10
num_exercicis = 10

def create_ciutats(cur):
  print("%d ciutats will be inserted." % num_ciutats)
  cur.execute("DROP TABLE IF EXISTS Ciutats CASCADE;")
  cur.execute("""CREATE TABLE Ciutats(
        nom varchar(50) NOT NULL,
        codi_postal numeric(5,0) NOT NULL,
        PRIMARY KEY (nom, codi_postal)
  );""")

  cities_inserted = 0
  while cities_inserted < num_ciutats:
    print(cities_inserted+1, end = '\r')
    nom = fake.city()
    codi_postal = fake.random_int(min=10000, max=99999)

    # Check if the city already exists in the table
    cur.execute("SELECT COUNT(*) FROM Ciutats WHERE nom = %s AND codi_postal =  %s", (nom, codi_postal))
    count = cur.fetchone()[0]

    if count == 0:
        cities_inserted += 1
        try:
            cur.execute("INSERT INTO ciutats VALUES ('%s', '%s')" % (nom, codi_postal))
        except psycopg2.IntegrityError as e:
            conn.rollback()
            #print("Error inserting (%s, %s). Error information: %s" % (nom, codi_postal, e))

        cities_inserted += 1


def create_empleats(cur):
  print("%d empleats will be inserted." % num_empleats)
  cur.execute("DROP TABLE IF EXISTS Empleats CASCADE;")
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
    );""")

  empleats_inserted = 0
  info_ciutats = cur.execute("SELECT * FROM Ciutats")
  ciutats = cur.fetchall()
  num_ciutats = len(ciutats)
  
  while empleats_inserted < num_empleats:
    print(empleats_inserted+1, end = '\r')
    # Generate unique dni
    dni = str(randint(10000000, 99999999)) + fake.random_letter()
    #tipus = fake.random_element(elements=('encarregat', 'treballador'))
    tipus = fake.random_element(elements=('senyor/a_neteja', 'dietista', 'entrenador/a', 'manteniment', 'recepcionista'))
    sou = fake.pyfloat(left_digits=4, right_digits=2, positive=True, min_value=900, max_value=3800)
    nom = fake.first_name()
    cognoms = fake.last_name() + ' ' + fake.last_name()
    telefon = fake.unique.random_number(digits=9) 
    compte_bancari = fake.iban()
    naixement = fake.date_of_birth(minimum_age=16, maximum_age=90)
    sexe = fake.random_element(elements=('H', 'D'))
    horaris = fake.random_element(elements=('7:00 - 15:00', '8:00 - 16:00', '9:00 - 17:00', '15:00 - 20:00', '16:00 - 21:00', '17:00 - 22:00'))

    

    # Make each city of the table Ciutats appear at least once in the Empleats table
    if empleats_inserted < 5*num_ciutats:
        nom_ciutat   = ciutats[empleats_inserted%num_ciutats][0]
        codi_postal = ciutats[empleats_inserted%num_ciutats][1]
    else:
      # Select a random city from the Ciutats table
      cur.execute("SELECT nom, codi_postal FROM Ciutats ORDER BY RANDOM() LIMIT 1")
      result = cur.fetchone()

      nom_ciutat   = result[0]
      codi_postal = result[1]

      #empleats_inserted += 1
      try:
          cur.execute("INSERT INTO Empleats VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (dni, tipus, sou, nom, cognoms, compte_bancari, telefon, naixement, sexe, horaris, nom_ciutat, codi_postal))
      except psycopg2.IntegrityError as e:
          conn.rollback()
          #print("Error inserting (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s). Error information: %s" % (dni, tipus, sou, nom, cognoms, compte_bancari, telefon, naixement, sexe, horaris, nom_ciutat, codi_postal, e))
 
    empleats_inserted += 1


def create_treballadors(cur):
  print("%d Treballadors will be inserted." % num_treballadors)
  ################################################################################quitar después de pruebas
  cur.execute("DROP TABLE IF EXISTS Treballadors CASCADE;")
  cur.execute("""CREATE TABLE Treballadors(
      gimnas varchar(8) NOT NULL,
      empleat varchar(9) NOT NULL,
      PRIMARY KEY (gimnas, empleat),
      FOREIGN KEY (gimnas) references Gimnasos(codi) on update cascade on delete cascade,
      FOREIGN KEY (empleat) references Empleats(dni) on update cascade on delete cascade
  );""")

  treballadors_inserted = 0
  while treballadors_inserted < num_treballadors:
    print(treballadors_inserted+1, end = '\r')

    # seleccionem un empleat aleatori
    cur.execute("SELECT e.dni, g.codi FROM Empleats e JOIN Gimnasos g ON e.codi_postal = g.codi_postal ORDER BY RANDOM() LIMIT 1")
    variable = cur.fetchone()
    empleat = variable[0]
    gimnas = variable[1]

    try:
        cur.execute("INSERT INTO Treballadors VALUES ('%s', '%s')" % (gimnas, empleat))
        treballadors_inserted += 1
    except psycopg2.IntegrityError as e:
        conn.rollback()
        print("Error inserting (%s, %s). Error information: %s" % (gimnas, empleat, e))

    


def create_gimnasos(cur):
  print("%d Gimnasos will be inserted." % num_gimnasos)
  cur.execute("DROP TABLE IF EXISTS Gimnasos CASCADE;")
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
  
  cur.execute("DROP TABLE IF EXISTS Treballadors CASCADE;")
  cur.execute("""CREATE TABLE Treballadors(
      gimnas varchar(8) NOT NULL,
      empleat varchar(9) NOT NULL,
      PRIMARY KEY (gimnas, empleat),
      FOREIGN KEY (gimnas) references Gimnasos(codi) on update cascade on delete cascade,
      FOREIGN KEY (empleat) references Empleats(dni) on update cascade on delete cascade
  );""")

  gimnasos_inserted = 0
  while gimnasos_inserted < num_gimnasos:
    print(gimnasos_inserted+1, end = '\r')

    codi = ''.join(fake.random_letters(length=4)) + str(fake.random_int(min=1000, max=9999))

    adreca = fake.street_address()
    telefon = fake.random_int(min=600000000, max=699999999)
    correu_electronic = fake.email()

    # Select a random city from the Ciutats table
    cur.execute("SELECT nom, codi_postal FROM Ciutats ORDER BY RANDOM() LIMIT 1")
    result = cur.fetchone()
    nom_ciutat = result[0]
    codi_postal = result[1]

    tipus = 'encarregat'
    while tipus == 'encarregat':
      #print(nom_ciutat, codi_postal)
      # get the encarregat from the specific city
      cur.execute("SELECT dni, tipus FROM Empleats WHERE nom_ciutat = '%s' AND codi_postal = '%s';" % (nom_ciutat, codi_postal))
      result = cur.fetchone()
      #print(result)
      encarregat = result[0]
      tipus = result[1]

    # update the encarregat to tipus = 'Encarregat'
    cur.execute("UPDATE Empleats SET tipus = 'Encarregat' WHERE dni = '%s';" % (encarregat,))

    try:
        cur.execute("INSERT INTO Gimnasos VALUES (%s, %s, %s, %s, %s, %s, %s)", (codi, adreca, telefon, correu_electronic, nom_ciutat, codi_postal, encarregat))
        # añadir en la tabla treballadors a este encargado y este gym 
        cur.execute("INSERT INTO Treballadors VALUES (%s, %s)", (codi, encarregat))

    except psycopg2.IntegrityError as e:
        conn.rollback()
        #print("Error inserting (%s, %s, %s, %s, %s, %s, %s). Error information: %s" % (codi, adreca, telefon, correu_electronic, nom_ciutat, codi_postal, encarregat, e))

    gimnasos_inserted += 1


def create_sales(cur):
  print("%d Sales will be inserted." % num_sales)
  cur.execute("DROP TABLE IF EXISTS Sales CASCADE;")
  cur.execute("""CREATE TABLE Sales(
        codi varchar(8) NOT NULL,
        codi_gimnas varchar(8) NOT NULL,
        aforament_maxim numeric(3,0),
        PRIMARY KEY (codi, codi_gimnas),
        FOREIGN KEY (codi_gimnas) references Gimnasos(codi) on update cascade on delete cascade
    );""")

  sales_inserted = 0
  while sales_inserted < num_sales:
    print(sales_inserted+1, end = '\r')

    codi = ''.join(fake.random_letters(length=4)) + str(fake.random_int(min=1000, max=9999))

    # Select a random gimnas and its codi
    cur.execute("SELECT codi FROM Gimnasos ORDER BY RANDOM() LIMIT 1")
    codi_gimnas = cur.fetchone()[0]

    aforament_maxim = fake.random_int(min=50, max=500)

    try:
        cur.execute("INSERT INTO Sales VALUES ('%s', '%s', '%s')" % (codi, codi_gimnas, aforament_maxim))
    except psycopg2.IntegrityError as e:
        conn.rollback()
        #print("Error inserting (%s, %s, %s). Error information: %s" % (codi, codi_gimnas, aforament_maxim, e))

    sales_inserted += 1


def create_classes(cur):
  print("%d Classes will be inserted." % num_classes)
  cur.execute("DROP TABLE IF EXISTS Classes CASCADE;")
  cur.execute("""CREATE TABLE Classes(
        codi varchar(8) NOT NULL,
        tipus varchar(50) NOT NULL,
        data date NOT NULL,
        duració time NOT NULL,
        hora time NOT NULL,
        codi_sala varchar(8) NOT NULL,
        codi_gimnas varchar(8) NOT NULL,
        tutor varchar(9) NOT NULL,
        PRIMARY KEY (codi),
        -- No es pot donar el cas que hi hagin dos classes el mateix dia, a la mateixa hora, al mateix gimnas i a la mateixa sala
        UNIQUE(codi_gimnas, hora, codi_sala, data),
        FOREIGN KEY (codi_gimnas) references Gimnasos(codi) on update cascade on delete restrict,
        FOREIGN KEY (codi_sala, codi_gimnas) references Sales(codi, codi_gimnas) on update cascade on delete restrict,
        FOREIGN KEY (tutor) references Empleats(dni) on update cascade on delete restrict
);""")

  classes_inserted = 0
  while classes_inserted < num_classes:
    print(classes_inserted+1, end = '\r')

    codi  = ''.join(fake.random_letters(length=4)) + str(fake.random_int(min=1000, max=9999))
    tipus = fake.random_element(elements=("Zumba", "Pilates", "Yoga", "Crossfit", "Spinning", "Entrenament funcional", "Bodypump", "Boxa", "TRX", "Aquagym", "Dancefit", "HIIT", "Cardio", "kickboxing", "Bootcamp", "Barre fitness", "Step", "Salsa fitness", "Aero dance", "Cycling"))
    data = fake.date_between(start_date='-5y', end_date='+1y')

    # Create a timedelta object representing a duration of 10 minutes
    duracio_minuts = fake.random_int(min=10, max=120)
    duracio = timedelta(minutes=duracio_minuts)

    # Calculem hora inici random
    start = fake.random_int(min=7, max=21)  # Hours
    time_str = f"{start}:00" 
    time_obj = datetime.strptime(time_str, "%H:%M")
    hora = (time_obj + timedelta(minutes=duracio_minuts))
  


    # seleccionem una sala aleatoria del gimnas
    cur.execute("SELECT codi, codi_gimnas FROM Sales ORDER BY RANDOM() LIMIT 1")
    result = cur.fetchone()
    codi_sala = result[0]
    codi_gimnas = result[1]

    # seleccionem un tutor aleatori del gimnas
    cur.execute("SELECT dni FROM Treballadors t JOIN Empleats e ON t.gimnas = %s AND e.tipus = 'entrenador/a' ORDER BY RANDOM() LIMIT 1", [codi_gimnas])
    #cur.execute("SELECT t.dni FROM Treballadors t JOIN Empleats e ON t.dni = e.dni WHERE t.gimnas = %s AND e.tipus = 'entrenador' ORDER BY RANDOM() LIMIT 1", (codi_gimnas,))
    #print(cur.fetchone())
    result = cur.fetchone()          
    tutor = result[0]

    if classes_inserted > 0:
        try:
            cur.execute("INSERT INTO Classes VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (codi, tipus, data, duracio, hora, codi_sala, codi_gimnas, tutor))
        except psycopg2.IntegrityError as e:
            conn.rollback()
            #print("Error inserting (%s, %s, %s, %s, %s, %s, %s, %s). Error information: %s" % (codi, tipus, data, duracio, hora, codi_sala, codi_gimnas, tutor, e))


            
    classes_inserted += 1


def create_dies(cur):
	print("7 dies will be inserted.")
	cur.execute("DROP TABLE IF EXISTS Dies CASCADE;")
	cur.execute("""CREATE TABLE Dies(
    dia varchar(9) NOT NULL,
    PRIMARY KEY (dia)
	);""")
	days = ['Dilluns', 'Dimarts', 'Dimecres', 'Dijous', 'Divendres', 'Dissabte', 'Diumenge']
	for day in days:
		cur.execute("INSERT INTO Dies (dia) VALUES ('%s')" % (day))


def create_aliments(cur):
  print("%d Aliments will be inserted." % num_aliments)
  cur.execute("DROP TABLE IF EXISTS Aliments CASCADE;")
  cur.execute("""CREATE TABLE Aliments(
    nom varchar(50) NOT NULL,
    PRIMARY KEY (nom)
  );""")
  aliments_inserted = 0

  while aliments_inserted < num_aliments:
      print(aliments_inserted+1, end = '\r')
      
      aliment = fake.ingredient()     

      try:
          cur.execute("INSERT INTO Aliments VALUES ('%s')" % (aliment,))
      except psycopg2.IntegrityError as e:
          conn.rollback()
          #print("Error inserting ('%s')" % (aliment,))        
      
      aliments_inserted += 1


def create_dietes(cur):
  print("%d Dietes will be inserted." % num_dietes)
  cur.execute("DROP TABLE IF EXISTS Dietes CASCADE;")
  cur.execute("""CREATE TABLE Dietes(
    codi varchar(8) NOT NULL,
    tipus varchar(30) NOT NULL,
    dietista varchar (9) NOT NULL,
    PRIMARY KEY (codi),
    FOREIGN KEY (dietista) references Empleats(dni) on update cascade on delete restrict
  );""")

  dietes_inserted = 0
  while dietes_inserted < num_dietes:
    print(dietes_inserted+1, end = '\r')

    codi  = ''.join(fake.random_letters(length=4)) + str(fake.random_int(min=1000, max=9999))
    tipus = fake.random_element(elements=("Augment de massa muscular", "Pèrdua de greix", "Augment de força", "Augment de concentració", "Augment de ferro", "Augment de vitamines", "Rendiment esportiu", "Rendiment congitiu"))
    # seleccionem un dietista aleatori
    cur.execute("SELECT dni FROM Empleats WHERE tipus = 'dietista' ORDER BY RANDOM() LIMIT 1")
    dietista = cur.fetchone()[0]

    try:
            cur.execute("INSERT INTO Dietes VALUES ('%s', '%s', '%s')" % (codi, tipus, dietista))
    except psycopg2.IntegrityError as e:
            conn.rollback()
            #print("Error inserting (%s, %s, %s). Error information: %s" % (codi, tipus, dietista))

    dietes_inserted += 1


def create_rutines(cur):
  print("%d Rutines will be inserted." % num_rutines)
  cur.execute("DROP TABLE IF EXISTS Rutines CASCADE;")
  cur.execute("""CREATE TABLE Rutines(
    codi varchar(8) NOT NULL,
    tipus varchar(25) NOT NULL,
    entrenador varchar (9) NOT NULL,
    PRIMARY KEY (codi),
    FOREIGN KEY (entrenador) references Empleats(dni) on update cascade on delete restrict
  );""")

  rutines_inserted = 0
  while rutines_inserted < num_rutines:
    print(rutines_inserted+1, end = '\r')

    codi  = ''.join(fake.random_letters(length=4)) + str(fake.random_int(min=1000, max=9999))
    tipus = fake.random_element(elements=("Augment de massa muscular", "Pèrdua de greix", "Augment de força", "Estiraments", "Rendiment esportiu", "Cardio", "Crossfit", "Calistenia"))
    # seleccionem un entrenador aleatori
    cur.execute("SELECT dni FROM Empleats WHERE tipus = 'entrenador/a' ORDER BY RANDOM() LIMIT 1")
    entrenador = cur.fetchone()[0]
    try:
            cur.execute("INSERT INTO Rutines VALUES ('%s', '%s', '%s')" % (codi, tipus, entrenador))
    except psycopg2.IntegrityError as e:
            conn.rollback()
            #print("Error inserting (%s, %s, %s). Error information: %s" % (codi, tipus, entrenador))

    rutines_inserted += 1


def create_clients(cur):
  print("%d Clients will be inserted." % num_clients)
  cur.execute("DROP TABLE IF EXISTS Clients CASCADE;")
  cur.execute("""CREATE TABLE Clients(
    dni varchar(9) NOT NULL,
    inici date NOT NULL,
    adreca varchar(255) NOT NULL,
    correu_electronic varchar(64) NOT NULL,
    nom varchar(20) NOT NULL,
    cognoms varchar(40) NOT NULL,
    compte_bancari varchar(24) NOT NULL,
    telefon numeric(9) NOT NULL,
    naixement date NOT NULL,
    sexe char(1) NOT NULL,
    pes numeric (6,3) NOT NULL,
    alcada numeric(3,2) NOT NULL,
    greix numeric (3,1) NOT NULL,
    massa_ossia numeric (3,1) NOT NULL,
    massa_muscular numeric(3,1) NOT NULL,
    estat char(1) NOT NULL,
    nom_ciutat varchar(50) NOT NULL,
    codi_postal numeric(5,0) NOT NULL,
    PRIMARY KEY (dni),
    UNIQUE(telefon),
    UNIQUE(correu_electronic),
    FOREIGN KEY (nom_ciutat, codi_postal) references Ciutats(nom, codi_postal) on update cascade on delete restrict
  );""")

  clients_inserted = 0
  current_ciutat = 0
  
  while clients_inserted < num_clients:
    print(clients_inserted+1, end = '\r')
    # Generate unique dni
    dni = str(randint(10000000, 99999999)) + fake.random_letter()
    inici = fake.date_between(start_date='-5y', end_date='today')
    adreca = fake.street_address()
    pes = fake.pyfloat(left_digits=3, right_digits=3, positive=True, min_value=40, max_value=180)
    alcada = fake.pyfloat(left_digits=1, right_digits=2, positive=True, min_value=1, max_value=2.7)
    
    greix = fake.pyfloat(left_digits=2, right_digits=1, positive=True, min_value=6, max_value=35)
	
    massa_ossia = fake.pyfloat(left_digits=2, right_digits=1, positive=True, min_value=9, max_value=23)
	
    massa_muscular = 100.0-greix-massa_ossia
    estat = random.choices(["O", "X"], weights=[0.9, 0.1], k=1)[0]
	# O vol dir normal i X que no ha pagat
    nom = fake.first_name()
    correu = nom+str(fake.unique.random_number(digits=3))+fake.random_element(elements=("@gmail.com", "@gmail.es", "@xtec.cat", "@upc.edu", "@hotmail.com", "@yahoo.com"))
    cognoms = fake.last_name() + ' ' + fake.last_name()
    telefon = fake.unique.random_number(digits=9) 
    compte_bancari = fake.iban()
    naixement = fake.date_of_birth(minimum_age=16, maximum_age=90)
    sexe = fake.random_element(elements=('H', 'D'))
    horaris = fake.random_element(elements=('7:00 - 15:00', '8:00 - 16:00', '9:00 - 17:00', '15:00 - 20:00', '16:00 - 21:00', '17:00 - 22:00'))


    # Select a random city from the Ciutats table
    cur.execute("SELECT nom, codi_postal FROM Ciutats ORDER BY RANDOM() LIMIT 1")
    result = cur.fetchone()
    nom_ciutat   = result[0]
    codi_postal = result[1]

    try:
        cur.execute("INSERT INTO Clients VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (dni, inici, adreca, correu, nom, cognoms, compte_bancari, telefon, naixement, sexe, pes, alcada, greix, massa_ossia, massa_muscular, estat, nom_ciutat, codi_postal))
    
    except psycopg2.IntegrityError as e:
        conn.rollback()
        #print("Error inserting (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s). Error information: %s" % (dni, inici, adreca, correu, nom, cognoms, compte_bancari, telefon, naixement, sexe, pes, alcada, greix, massa_ossia, massa_muscular, estat, nom_ciutat, codi_postal))

    clients_inserted += 1
    current_ciutat += 1


def create_pagaments(cur):
  print("Pagaments will be inserted.")
  cur.execute("DROP TABLE IF EXISTS Pagaments CASCADE;")
  cur.execute("""CREATE TABLE Pagaments(
    data date NOT NULL,
    client varchar(9) NOT NULL,	
    Pagament_efectuat bool,
    PRIMARY KEY (data, client),
    FOREIGN KEY (client) references Clients(dni) on update cascade on delete restrict
  );""")

  cur.execute("SELECT dni, inici, estat FROM Clients")
  clients = cur.fetchall()
  days = []
  for client in clients:
    days.append(llista_laborables_periode(client[1], dt.date.today()))

  for day in days:
    for dia in day:
      try:
        cur.execute("INSERT INTO Pagaments VALUES ('%s', '%s', '%s')" % (dia, client[0], True))
      except psycopg2.IntegrityError as e:
        conn.rollback()
        #print("Error inserting (%s, %s, %s). Error information: %s" % (dia, client[0], True, e))

    if (client[2] == 'X'):
      try:
        cur.execute("""UPDATE Pagaments 
          SET Pagament_efectuat = False
          WHERE client = 'dni' AND data = (
          SELECT MAX(data) FROM Pagaments WHERE client = 'dni'
        );""")
      except psycopg2.IntegrityError as e:
        conn.rollback()
        #print("Error updating last date for client "+str(client))


def create_quantificador_dietes(cur):
  print("%d Quantificadors_Dietes will be inserted." % num_quantificador_dietes)
  cur.execute("DROP TABLE IF EXISTS Quantificadors_Dietes CASCADE;")
  cur.execute("""CREATE TABLE Quantificadors_Dietes(
    quantificador numeric(4,2) NOT NULL,
    dieta varchar(8) NOT NULL,
   	client varchar(9) NOT NULL,
    dietista varchar(9),
    PRIMARY KEY (dieta, client),
    FOREIGN KEY (dieta) references Dietes(codi) on update cascade on delete cascade,
    FOREIGN KEY (client) references Clients(dni) on update cascade on delete cascade,
    FOREIGN KEY (dietista) references Empleats(dni) on update cascade on delete restrict
  );""")

  quantificador_dietes_inserted = 0
  while quantificador_dietes_inserted < num_quantificador_dietes:
    print(quantificador_dietes_inserted+1, end = '\r')
    quantificador = fake.pyfloat(left_digits=1, right_digits=2, positive=True, min_value=0.2, max_value=3)
    # seleccionem un client aleatori
    cur.execute("SELECT dni FROM Clients ORDER BY RANDOM() LIMIT 1")
    client = cur.fetchone()[0]
    # seleccionem una dieta aleatoria
    cur.execute("SELECT codi FROM Dietes ORDER BY RANDOM() LIMIT 1")
    dieta = cur.fetchone()[0]
    # seleccionem un dietista aleatori
    cur.execute("SELECT dni FROM Empleats WHERE tipus = 'dietista' ORDER BY RANDOM() LIMIT 1")
    dietista = cur.fetchone()[0]
    try:
            cur.execute("INSERT INTO Quantificadors_Dietes VALUES ('%s', '%s', '%s', '%s')" % (quantificador, dieta, client, dietista))
    except psycopg2.IntegrityError as e:
            conn.rollback()
            #print("Error inserting (%s, '%s', %s, %s). Error information: %s" % (quantificador, dieta, client, dietista))

    quantificador_dietes_inserted += 1


def create_quantificador_rutines(cur):
  print("%d Quantificadors_Pesos will be inserted." % num_quantificador_rutines)
  cur.execute("DROP TABLE IF EXISTS Quantificadors_Pesos CASCADE;")
  cur.execute("""CREATE TABLE Quantificadors_Pesos(
	  quantificador numeric(4,2) NOT NULL,
	  rutina varchar(8) NOT NULL,
   	client varchar(9) NOT NULL,
    entrenador varchar(9),
    PRIMARY KEY (rutina, client),
    FOREIGN KEY (rutina) references Rutines(codi) on update cascade on delete cascade,
    FOREIGN KEY (client) references Clients(dni) on update cascade on delete cascade,
    FOREIGN KEY (entrenador) references Empleats(dni) on update cascade on delete restrict
  );""")

  quantificador_rutines_inserted = 0

  while quantificador_rutines_inserted < num_quantificador_rutines:
    print(quantificador_rutines_inserted+1, end = '\r')
    quantificador = fake.pyfloat(left_digits=1, right_digits=2, positive=True, min_value=0.2, max_value=3)
    # seleccionem un client aleatori
    cur.execute("SELECT dni FROM Clients ORDER BY RANDOM() LIMIT 1")
    client = cur.fetchone()[0]
    # seleccionem una dieta aleatoria
    cur.execute("SELECT codi FROM Rutines ORDER BY RANDOM() LIMIT 1")
    rutina = cur.fetchone()[0]
    # seleccionem un dietista aleatori
    cur.execute("SELECT dni FROM Empleats WHERE tipus = 'entrenador/a' ORDER BY RANDOM() LIMIT 1")
    entrenador = cur.fetchone()[0]
    try:
            cur.execute("INSERT INTO Quantificadors_Pesos VALUES ('%s', '%s', '%s', '%s')" % (quantificador, rutina, client, entrenador))
    except psycopg2.IntegrityError as e:
            conn.rollback()
            #print("Error inserting ('%s', '%s', '%s', '%s'). Error information: %s" % (quantificador, rutina, client, entrenador, e))

    quantificador_rutines_inserted += 1


def create_apats(cur):

  print("%d Apats will be inserted." % num_apats)
  cur.execute("""DROP TABLE IF EXISTS Apats CASCADE;
    DROP TABLE IF EXISTS Franges_Horaries CASCADE;
    DROP TABLE IF EXISTS Quantitats_Aliments CASCADE;

    CREATE TABLE Apats(
      dieta varchar(8) NOT NULL,
      dia varchar(9) NOT NULL,
      PRIMARY KEY (dieta,dia)
    ); 

    CREATE TABLE Franges_Horaries(
      hora time NOT NULL,
      dieta varchar(8) NOT NULL,
      dia varchar(9) NOT NULL,
      PRIMARY KEY (hora, dieta, dia),
      FOREIGN KEY (dieta, dia) references Apats(dieta,dia) on update cascade on delete cascade
    );

    CREATE TABLE Quantitats_Aliments(
      quantitat numeric(5, 2) NOT NULL,
      unitats varchar(10) NOT NULL,
      hora time NOT NULL,
      dieta varchar(8) NOT NULL,
      dia varchar(9) NOT NULL,
      aliment varchar(20) NOT NULL,
      PRIMARY KEY (hora, dieta, dia, aliment),
      FOREIGN KEY (aliment) references Aliments(nom) on update cascade on delete cascade
    );""")

  apats_inserted = 0
  while apats_inserted < num_apats:
    n_dia=0
    print(apats_inserted+1, end = '\r')
    nombre_dies = fake.random_int(min=1, max=7)
    # seleccionem un dia aleatori
    cur.execute("SELECT dia FROM dies ORDER BY RANDOM() LIMIT '%s'" % (nombre_dies))
    dies = cur.fetchone()
    # seleccionem una dieta aleatoria
    cur.execute("SELECT codi FROM Dietes ORDER BY RANDOM() LIMIT 1")
    dieta = cur.fetchone()[0]

    try:
            cur.execute("INSERT INTO Apats VALUES ('%s', '%s')" % (dieta, dies[n_dia]))

            nombre_franges = fake.random_int(min=1, max=7)
            for i in range(nombre_franges):
               
                # Calculem hora inici random
                start = fake.random_int(min=7, max=21)  # Hours
                time_str = f"{start}:00" 
                hora = datetime.strptime(time_str, "%H:%M").time()

  
                try: 
                    cur.execute("INSERT INTO Franges_Horaries VALUES ('%s', '%s', '%s')" % (hora, dieta, dies[n_dia]))
                    nombre_quantitats = fake.random_int(min=1, max=10)
                    for j in range(nombre_quantitats):
                        cur.execute("SELECT nom FROM Aliments ORDER BY RANDOM() LIMIT 1")
                        aliment = cur.fetchone()[0]
                        quantitat = fake.pyfloat(left_digits=3, right_digits=2, positive=True, min_value=0.5, max_value=180)
                        unitats = fake.random_element(elements=('litres', 'grams', 'kilograms', 'unitats', 'dotzenes'))
                        try: 
                          cur.execute("INSERT INTO Quantitats_Aliments VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (quantitat, unitats, hora, dieta, dies[n_dia], aliment))
                        except psycopg2.IntegrityError as e:
                          conn.rollback()
                          #print("Error inserting ('%s', '%s', '%s', '%s', '%s', '%s'). Error information: %s" % (quantitat, unitats, hora, dieta, dies[n_dia], aliment, e))
                except psycopg2.IntegrityError as e:
                  conn.rollback()
                  #print("Error inserting ('%s', '%s', '%s'). Error information: %s" % (hora, dieta, dies[n_dia], e))

    except psycopg2.IntegrityError as e:
            conn.rollback()
            print("Error inserting (%s, '%s')." % (dieta, dies[n_dia]))

    n_dia += 1
    apats_inserted += 1


def create_exercicis(cur):
  print("%d Exercicis will be inserted." % num_exercicis)
  cur.execute("DROP TABLE IF EXISTS Exercicis CASCADE;")
  cur.execute("""CREATE TABLE Exercicis(
    codi varchar(8) NOT NULL,
    nom varchar(40) NOT NULL,
    PRIMARY KEY (codi)
  );""")

  exercicis_inserted = 0
  while exercicis_inserted < num_exercicis:
    print(exercicis_inserted+1, end = '\r')

    codi  = ''.join(fake.random_letters(length=4)) + str(fake.random_int(min=1000, max=9999))

    # seleccionem un nom aleatori
    nom = fake.random_element(elements=('Bench press', 'Squats', 'Deadlifts', 'Pull-ups', 'Push-ups', 'Lunges', 'Bicep curls', 'Tricep extensions', 'Shoulder press', 'Lat pull-downs', 'Crunches', 'Planks', 'Side planks', 'Russian twists', 'Leg press', 'Calf raises', 'Hammer curls', 'Dumbbell flys', 'Incline bench press', 'Decline bench press', 'Arnold press', 'Military press', 'Dips', 'Jumping jacks', 'Burpees', 'Mountain climbers', 'Step-ups', 'Leg curls', 'Leg extensions', 'Seated rows', 'Pullovers', 'Renegade rows', 'Reverse flys', 'Good mornings', 'Reverse lunges', 'Hammer strength machines', 'Stairmaster', 'Stationary bike', 'Treadmill', 'Elliptical machine', 'Rowing machine', 'Assault bike', 'Kettlebell swings', 'Box jumps', 'Wall balls', 'Thrusters', 'Clean and jerk', 'Snatch', 'Front squats', 'Back squats', 'Zercher squats', 'Sumo deadlifts', 'Romanian deadlifts', 'Goblet squats', 'Overhead squats', 'Barbell lunges', 'Reverse grip pull-ups', 'Wide grip pull-ups', 'Close grip pull-downs', 'Wide grip pull-downs', 'Neutral grip pull-downs', 'Incline dumbbell press', 'Decline dumbbell press', 'Dumbbell pullovers', 'Straight-arm pulldowns', 'Close grip bench press', 'Skull crushers', 'Seated dumbbell press', 'Standing dumbbell press', 'Standing cable flys', 'Seated cable flys', 'Standing calf raises', 'Seated calf raises', 'Smith machine squats', 'Smith machine lunges', 'Smith machine bench press', 'Smith machine incline bench press', 'Smith machine decline bench press', 'Hip thrusts', 'Glute bridges', 'Donkey kicks', 'Fire hydrants', 'Side-lying leg lifts', 'Hip abductor machine', 'Hip adductor machine', 'Leg press machine', 'Hack squat machine', 'Standing leg curls', 'Seated leg curls', 'Standing leg extensions',
    'Seated leg extensions', 'Cable rows', 'One-arm dumbbell rows', 'Kroc rows', 'Deadlift variations',
    'Reverse grip curls', 'Preacher curls', 'Concentration curls', 'Hanging leg raises', 'Ab wheel rollouts', 'Dragon flags', 'Windshield wipers'))

    if num_exercicis > 1:
        cur.execute("SELECT count(*) FROM Exercicis where nom = '%s'" % nom)

        if cur.fetchone()[0] > 0:            
            cur.execute("SELECT codi FROM Exercicis where nom = '%s'" % nom)
            codi = cur.fetchone()[0]

    try:
            cur.execute("INSERT INTO Exercicis VALUES ('%s', '%s')" % (codi, nom))
    except psycopg2.IntegrityError as e:
            conn.rollback()
            #print("Error inserting (%s, %s). Error information: %s" % (codi, nom, e))

    exercicis_inserted += 1


def create_entrenaments(cur):

  print("%d Entrenaments will be inserted." % num_entrenaments)
  cur.execute("""DROP TABLE IF EXISTS Entrenaments CASCADE;
    DROP TABLE IF EXISTS Entrenaments_diaris CASCADE;
    DROP TABLE IF EXISTS Entrenaments_Personals CASCADE;
    DROP TABLE IF EXISTS Rondes CASCADE;
    DROP TABLE IF EXISTS Series CASCADE;

    CREATE TABLE Entrenaments(
    codi varchar(8) NOT NULL,
    PRIMARY KEY (codi)
  );

  CREATE TABLE Entrenaments_diaris(
    codi varchar(8) NOT NULL,
    rutina varchar (8) NOT NULL,
    dia varchar(9) NOT NULL,
    PRIMARY KEY (codi),
    UNIQUE(rutina, dia),
    FOREIGN KEY (rutina) references Rutines(codi) on update cascade on delete cascade,
    FOREIGN KEY (dia) references Dies(dia) on update cascade on delete cascade,
    FOREIGN KEY (codi) references Entrenaments(codi) on update cascade on delete restrict
  );

  CREATE TABLE Entrenaments_Personals(
    codi varchar(8) NOT NULL,
    data date NOT NULL,
    hora time NOT NULL,
    client varchar(9) NOT NULL,
    plantilla varchar(9) ,
    PRIMARY KEY (codi),
    UNIQUE(client, data, hora),
    FOREIGN KEY (client) references Clients(dni) on update cascade on delete cascade,
    FOREIGN KEY (plantilla) references Entrenaments_Diaris(codi) on update cascade on delete restrict,
    FOREIGN KEY (codi) references Entrenaments(codi) on update cascade on delete cascade
  );

  CREATE TABLE Rondes(
    codi varchar(8) NOT NULL,
    ordre  numeric(2,0) NOT NULL,
    entrenament varchar(9) NOT NULL,
    exercici varchar(40) NOT NULL,
    PRIMARY KEY (codi),
    UNIQUE(entrenament, ordre),
    FOREIGN KEY (entrenament) references Entrenaments(codi) on update cascade on delete cascade,
    FOREIGN KEY (exercici) references Exercicis(codi) on update cascade on delete cascade
  );

  CREATE TABLE Series(
    num_serie numeric(2, 0) NOT NULL,
    pes  numeric (4,1) NOT NULL,
    num_repeticions numeric(2,0),
    duracio time,
    ronda varchar(8) NOT NULL,
    PRIMARY KEY (num_serie, ronda),
    FOREIGN KEY (ronda) references Rondes(codi) on update cascade on delete cascade
  );""")

  entrenaments_inserted = 0.0
  while entrenaments_inserted < num_entrenaments:
    print(entrenaments_inserted+1, end = '\r')
    codi = ''.join(fake.random_letters(length=4)) + str(fake.random_int(min=1000, max=9999))
    try:
      cur.execute("INSERT INTO Entrenaments VALUES ('%s')" % (codi,))
      if entrenaments_inserted > num_entrenaments*0.1:
            cur.execute("SELECT dni, inici FROM Clients ORDER BY RANDOM() LIMIT 1")
            result = cur.fetchone()
            client = result[0]
            inici = result[1]
            data = fake.date_between(inici, end_date='today')
            # Calculem hora inici random
            start = fake.random_int(min=7, max=21)  # Hours
            time_str = f"{start}:00" 
            hora = datetime.strptime(time_str, "%H:%M").time()
            cur.execute("SELECT codi FROM Entrenaments ORDER BY RANDOM() LIMIT 1")
            plantilla = cur.fetchone()[0]
            try:
                cur.execute("INSERT INTO Entrenaments_Personals VALUES ('%s', '%s', '%s', '%s', '%s')" % (codi, data, hora, client, plantilla))
                fill_entrenament(cur, codi)
            except psycopg2.IntegrityError as e:
                conn.rollback()
                print("Error inserting ('%s', '%s', '%s', '%s', '%s'). Error information: %s" % (codi, data, hora, client, plantilla, e))

      else:
            cur.execute("SELECT codi FROM Rutines ORDER BY RANDOM() LIMIT 1")
            rutina = cur.fetchone()[0]
            nombre_dies = fake.random_int(min=1, max=7)
            cur.execute("SELECT dia FROM dies ORDER BY RANDOM() LIMIT '%s'" % (nombre_dies))
            dies = cur.fetchone()
            for dia in dies:
                try:
                    cur.execute("INSERT INTO Entrenaments_Diaris VALUES ('%s', '%s', '%s')" % (codi, rutina, dia))
                    fill_entrenament(cur, codi)
                except psycopg2.IntegrityError as e:
                    conn.rollback()
                    print("Error inserting ('%s', '%s', '%s'). Error information: %s" % (codi, rutina, dia, e))

    except psycopg2.IntegrityError as e:
      conn.rollback()
      print("Error inserting ('%s'). Error information: %s" % (codi, e))

    entrenaments_inserted += 1
    conn.commit()


def create_realitza_exercicis(cur):
  print("'%d' Sales will be inserted per exercici", sales_per_exercici)
  cur.execute("DROP TABLE IF EXISTS Realitza_Exercicis CASCADE;")
  cur.execute("""CREATE TABLE Realitza_Exercicis(
      exercici varchar(8) NOT NULL,
      gimnas varchar(8) NOT NULL,
      sala varchar(8) NOT NULL,
      PRIMARY KEY (exercici, gimnas, sala),
      FOREIGN KEY (sala, gimnas) references Sales(codi, codi_gimnas) on update cascade on delete cascade,
      FOREIGN KEY (exercici) references Exercicis(codi) on update cascade on delete cascade,
      FOREIGN KEY (gimnas) references Gimnasos(codi) on update cascade on delete cascade
  );""")

  realitza_exercicis_inserted = 0

  # seleccionem un exercici aleatori
  cur.execute("SELECT codi FROM Exercicis")
  exercicis = cur.fetchall()

  for exercici in exercicis:
    nombre_quantitats = fake.random_int(min=sales_per_exercici/2, max=1.5*sales_per_exercici)
    for j in range(nombre_quantitats):
      print(realitza_exercicis_inserted+1, end = '\r')

      cur.execute("SELECT codi, codi_gimnas FROM Sales ORDER BY RANDOM() LIMIT 1")
      result = cur.fetchone()
      sala = result[0]
      gimnas = result[1]

      try:
          cur.execute("INSERT INTO Realitza_Exercicis VALUES ('%s', '%s', '%s')" % (exercici[0], gimnas, sala))
      except psycopg2.IntegrityError as e:
          conn.rollback()
          #print("Error inserting (%s, %s, %s). Error information: %s" % (exercici[0], gimnas, sala, e))
      
      realitza_exercicis_inserted += 1


def create_participacions(cur):
  print("%d Participacions will be inserted." % num_participacions)
  cur.execute("DROP TABLE IF EXISTS Participacions CASCADE;")
  cur.execute("""CREATE TABLE Participacions(
      classe varchar(8) NOT NULL,
      client varchar(9) NOT NULL,
      PRIMARY KEY (classe, client),
      FOREIGN KEY (client) references Clients(dni) on update cascade on delete cascade,
      FOREIGN KEY (classe) references Classes(codi) on update cascade on delete cascade
  );""")

  participacions_inserted = 0
  while participacions_inserted < num_participacions:
    print(participacions_inserted+1, end = '\r')

    # seleccionem un client aleatori
    cur.execute("SELECT dni, inici FROM Clients ORDER BY RANDOM() LIMIT 1")
    result = cur.fetchone()
    client = result[0]
    inici = result[1]

    # seleccionem una classe aleatoria
    cur.execute("SELECT codi, data FROM Classes ORDER BY RANDOM() LIMIT 1")
    result = cur.fetchone()
    classe = result[0]
    data = result[1]

    # verificar que la data en la que ha entrat el client es inferior a la data de la classe
    if inici < data:   
      try:
          cur.execute("INSERT INTO Participacions VALUES ('%s', '%s')" % (classe, client))
      except psycopg2.IntegrityError as e:
          conn.rollback()
          #print("Error inserting (%s, %s). Error information: %s" % (client, classe, e))
      participacions_inserted += 1


##########################################################Funcions auxiliars a les de crear#######################################################

def primer_laborable(year, month):
    for day in range(1, 8):
        date = dt.date(year, month, day)
        if date.weekday() < 5:  # Monday = 0, Friday = 4
            return date


def llista_laborables_periode(start_date, end_date):

	dates_list = []

	while start_date < end_date:
		year = start_date.year
		month = start_date.month
		first_working_day = primer_laborable(year, month)
		dates_list.append(first_working_day.strftime('%d/%m/%Y'))
		start_date = first_working_day + relativedelta(months=1)
	return dates_list


def fill_entrenament(cur, entrenament):
    nombre_rondes = fake.random_int(min=1, max=15)

    for ordre in range(1, nombre_rondes):
        codi = ''.join(fake.random_letters(length=4)) + str(fake.random_int(min=1000, max=9999))
        cur.execute("SELECT nom FROM Exercicis ORDER BY RANDOM() LIMIT 1")
        exercici = cur.fetchone()[0]
        try: 
            cur.execute("INSERT INTO Rondes VALUES ('%s', '%s', '%s', '%s')" % (codi, ordre, entrenament, exercici))
            nombre_series = fake.random_int(min=1, max=10)

            for j in range(1, nombre_series):
                cur.execute("SELECT nom FROM Aliments ORDER BY RANDOM() LIMIT 1")
                aliment = cur.fetchone()[0]
                pes = fake.pyfloat(left_digits=3, right_digits=1, positive=True, min_value=0.1, max_value=200)
                if pes < 0.5:
                    pes = 0.0
                tipus = fake.random_int(min=0, max=8)
                if tipus == 8:
                  duracio_segons = fake.random_int(min=5, max=120)
                  duracio = timedelta(seconds=duracio_segons)
                  try: 
                    cur.execute("INSERT INTO Series VALUES ('%s', '%s', NULL, '%s', '%s')" % (j, pes, duracio, codi))
                  except psycopg2.IntegrityError as e:
                    conn.rollback()
                    #print("Error inserting ('%s', '%s', '%s', NULL, '%s'). Error information: %s" % (j, pes, num_repeticions, codi))
                
                else:
                  num_repeticions =  fake.random_int(min=0, max=30)
                  try: 
                    cur.execute("INSERT INTO Series VALUES ('%s', '%s', '%s', NULL, '%s')" % (j, pes, num_repeticions, codi))
                  except psycopg2.IntegrityError as e:
                    conn.rollback()
                    #print("Error inserting ('%s', '%s', '%s', NULL, '%s'). Error information: %s" % (j, pes, num_repeticions, codi))

        except psycopg2.IntegrityError as e:
          conn.rollback()
          #print("Error inserting ('%s', '%s', '%s' '%s'). Error information: %s" % (codi, ordre, entrenament, exercici, e))



##################################################################Programa principal###########################################################

conn = psycopg2.connect(
    host="ubiwan.epsevg.upc.edu",
    database="est_a4033441",
    user="est_a4033441",
    password="dB.a4033441",
    options=f'-c search_path=practica'
)

cur = conn.cursor()

#create_ciutats(cur)
#conn.commit()
#create_empleats(cur)
#conn.commit()
#create_gimnasos(cur)
#conn.commit()
#create_sales(cur)
#conn.commit()

######################################3falta debugar #create_treballadors(cur)
#conn.commit()
#create_classes(cur)
#conn.commit()
#create_dies(cur)
#conn.commit()
#create_aliments(cur)
#conn.commit()
#create_dietes(cur)
#conn.commit()
#create_rutines(cur)
#conn.commit()
#create_clients(cur)
#conn.commit()
#create_quantificador_dietes(cur)
#conn.commit()
#create_quantificador_rutines(cur)
#conn.commit()
#################################################3esta mal#create_apats(cur)
#conn.commit()
#create_exercicis(cur)
conn.commit()
create_entrenaments(cur)
conn.commit()
#############Se corta en algun punto k no deberia #create_realitza_exercicis(cur)
conn.commit()
##Hace algunas de mas create_participacions(cur)
conn.commit()
#create_pagaments(cur)
#conn.commit()

cur.close()
conn.close()
