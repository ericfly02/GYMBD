import psycopg2
from random import randint
import random
from faker import Faker
from datetime import time, datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta

fake = Faker('es_ES')


num_ciutats = 100
num_empleats = 100
num_gimnasos = 100
num_sales = 100
num_classes = 100
num_aliments = 100
num_dietes = 100
num_rutines = 100
num_clients = 100
num_s = 100
num_quantificador_dietes = 100
num_quantificador_rutines = 100
num_apats = 100
num_entrenaments = 100
num_realitza_exercicis = 100
num_participacions = 100
sales_per_exercici = 100
num_treballadors = 100


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
    cur.execute("SELECT COUNT(*) FROM Ciutats WHERE nom = %s AND codi_postal =  %s", (nom, codi_postal))
    count = cur.fetchone()[0]

    if count == 0:
        cities_inserted += 1
        try:
            cur.execute("INSERT INTO ciutats VALUES ('%s', '%s')" % (nom, codi_postal))
        except psycopg2.IntegrityError as e:
            conn.rollback()
            print("Error inserting (%s, %s). Error information: %s" % (nom, codi_postal, e))
        #conn.commit()
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
    tipus = fake.random_element(elements=('senyor/a_neteja', 'dietista', 'entrenador/a', 'manteniment', 'recepcionista'))
    sou = fake.pyfloat(left_digits=4, right_digits=2, positive=True, min_value=900, max_value=3800)
    nom = fake.first_name()
    cognoms = fake.last_name() + ' ' + fake.last_name()
    telefon = fake.unique.random_number(digits=9) 
    compte_bancari = fake.iban()
    naixement = fake.date_of_birth(minimum_age=16, maximum_age=90)
    sexe = fake.random_element(elements=('H', 'D'))
    horaris = fake.random_element(elements=('7:00 - 15:00', '8:00 - 16:00', '9:00 - 17:00', '15:00 - 20:00', '16:00 - 21:00', '17:00 - 22:00'))

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
    else:
      # Select a random city from the Ciutats table
      cur.execute("SELECT nom FROM Ciutats ORDER BY RANDOM() LIMIT 1")
      nom_ciutat   = cur.fetchone()[0]
      cur.execute("SELECT codi_postal FROM Ciutats WHERE nom = '%s';" % (nom_ciutat,))
      codi_postal = cur.fetchone()[0]

      #empleats_inserted += 1
      try:
          cur.execute("INSERT INTO Empleats VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (dni, tipus, sou, nom, cognoms, compte_bancari, telefon, naixement, sexe, horaris, nom_ciutat, codi_postal))
      except psycopg2.IntegrityError as e:
          conn.rollback()
          print("Error inserting (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s). Error information: %s" % (dni, tipus, sou, nom, cognoms, compte_bancari, telefon, naixement, sexe, horaris, nom_ciutat, codi_postal, e))
      #conn.commit()
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
    cur.execute("SELECT nom, codi_postal FROM Ciutats ORDER BY RANDOM() LIMIT 1")
    nom_ciutat   = cur.fetchone()[0] 
    codi_postal = cur.fetchone()[1]

    tipus = 'encarregat'
    while tipus == 'encarregat':
      # get the encarregat from the specific city
      cur.execute("SELECT dni, tipus FROM Empleats WHERE nom_ciutat = '%s' AND codi_postal = '%s';" % (nom_ciutat, codi_postal))
      encarregat = cur.fetchone()[0]
      tipus = cur.fetchone()[1]

    # update the encarregat to tipus = 'Encarregat'
    cur.execute("UPDATE Empleats SET tipus = 'Encarregat' WHERE dni = '%s';" % (encarregat,))

    # añadir en la tabla treballadors a este encargado y este gym 
    cur.execute("INSERT INTO Treballadors VALUES (%s, %s)", (encarregat, codi))

    try:
        cur.execute("INSERT INTO Gimnasos VALUES (%s, %s, %s, %s, %s, %s, %s)", (codi, adreca, telefon, correu_electronic, nom_ciutat, codi_postal, encarregat))

    except psycopg2.IntegrityError as e:
        conn.rollback()
        print("Error inserting (%s, %s, %s, %s, %s, %s, %s). Error information: %s" % (codi, adreca, telefon, correu_electronic, nom_ciutat, codi_postal, encarregat, e))
    #conn.commit()
    gimnasos_inserted += 1


def create_treballadors(cur):
  print("%d Participacions will be inserted." % num_treballadors)
  cur.execute("DROP TABLE IF EXISTS Treballadors CASCADE")
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
    cur.execute("SELECT dni FROM Empleats ORDER BY RANDOM() LIMIT 1")
    empleat = cur.fetchone()[0]

    # seleccionem un gimnas aleatori
    cur.execute("SELECT codi FROM Gimnasos ORDER BY RANDOM() LIMIT 1")
    gimnas = cur.fetchone()[0]

        

    try:
        cur.execute("INSERT INTO Treballadors VALUES ('%s', '%s')" % (gimnas, empleat))
    except psycopg2.IntegrityError as e:
        conn.rollback()
        print("Error inserting (%s, %s). Error information: %s" % (gimnas, empleat, e))
    #conn.commit()
    treballadors_inserted += 1


def create_sales(cur):
  print("%d Sales will be inserted." % num_sales)
  cur.execute("DROP TABLE IF EXISTS Sales CASCADE")
  cur.execute("""CREATE TABLE Sales(
        codi varchar(8) NOT NULL,
        codi_gimnas varchar(8) NOT NULL,
        aforament_maxim numeric(3,0),
        PRIMARY KEY (codi, codi_gimnas),
        FOREIGN KEY (codi_gimnas) references Gimnasos(codi) on update cascade on delete cascade
    )""")

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
        print("Error inserting (%s, %s, %s). Error information: %s" % (codi, codi_gimnas, aforament_maxim, e))
        
    #conn.commit()
    sales_inserted += 1


def create_classes(cur):
  print("%d Classes will be inserted." % num_ciutats)
  cur.execute("DROP TABLE IF EXISTS Classes CASCADE")
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
)""")

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
    hora = (time_obj + timedelta(minutes=duracio_minuts)).time()
  


    # seleccionem una sala aleatoria del gimnas
    cur.execute("SELECT codi, codi_gimnas FROM Sales ORDER BY RANDOM() LIMIT 1", (codi_gimnas,))
    codi_sala = cur.fetchone()[0]
    codi_gimnas = cur.fetchone()[1]

    # seleccionem un tutor aleatori del gimnas
    cur.execute("SELECT t.dni FROM Treballadors t JOIN Empleats e WHERE t.gimnas = %s AND e.tipus = 'entrenador' ORDER BY RANDOM() LIMIT 1", (codi_gimnas,))
    tutor = cur.fetchone()[0]

    if classes_inserted > 0:

        try:
            cur.execute("INSERT INTO Classes VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (codi, tipus, data, duracio, hora, codi_sala, codi_gimnas, tutor))
        except psycopg2.IntegrityError as e:
            conn.rollback()
            print("Error inserting (%s, %s, %s, %s, %s, %s, %s, %s). Error information: %s" % (codi, tipus, data, duracio, hora, codi_sala, codi_gimnas, tutor, e))
        #conn.commit()

        
    classes_inserted += 1


def create_dies(cur):
	print("7 dies will be inserted.")
	cur.execute("DROP TABLE IF EXISTS Dies CASCADE")
	cur.execute("""
  	CREATE TABLE Dies(
	dia varchar(9) NOT NULL,
	PRIMARY KEY (dia)
	);
	""")
	days = ['Dilluns', 'Dimarts', 'Dimecres', 'Dijous', 'Divendres', 'Dissabte', 'Diumenge']
	for day in days:
		cur.execute("INSERT INTO Dies (dia) VALUES ('%s')" % (day))
	#conn.commit()


def create_aliments(cur):
  print("7 dies will be inserted.")
  cur.execute("DROP TABLE IF EXISTS Dies CASCADE")
  cur.execute("""CREATE TABLE Aliments(
  nom varchar(20) NOT NULL,
  PRIMARY KEY (nom)
  );""")
  aliments_inserted = 0

  while aliments_inserted < num_aliments:
    print(aliments_inserted+1, end = '\r')
    if aliments_inserted > 0:
      aliment = fake.foods()

  try:
      cur.execute("INSERT INTO Classes VALUES ('%s')" % (aliment,))
  except psycopg2.IntegrityError as e:
      conn.rollback()
      print("Error inserting ('%s')" % (aliment,))        
  
  classes_inserted += 1
  #conn.commit()


def create_dietes(cur):
  print("%d Dietes will be inserted." % num_dietes)
  cur.execute("DROP TABLE IF EXISTS Dietes CASCADE")
  cur.execute("""CREATE TABLE Dietes(
	codi varchar(8) NOT NULL,
	tipus varchar(30) NOT NULL,
	dietista varchar (9) NOT NULL,
PRIMARY KEY (codi),
FOREIGN KEY (dietista) references Empleats(dni) on update cascade on delete restrict
);
""")

  dietes_inserted = 0
  while dietes_inserted < num_dietes:
    print(dietes_inserted+1, end = '\r')

    codi  = ''.join(fake.random_letters(length=4)) + str(fake.random_int(min=1000, max=9999))
    tipus = fake.random_element(elements=("Augment de massa muscular", "Pèrdua de greix", "Augment de força", "Augment de concentració", "Augment de ferro", "Augment de vitamines", "Rendiment esportiu", "Rendiment congitiu"))
    # seleccionem un dietista aleatori
    cur.execute("SELECT dni FROM Empleats WHERE tipus = 'dietista' ORDER BY RANDOM() LIMIT 1")
    dietista = cur.fetchone()[0]
    try:
            cur.execute("INSERT INTO Classes VALUES ('%s', '%s', '%s')" % (codi, tipus, dietista))
    except psycopg2.IntegrityError as e:
            conn.rollback()
            print("Error inserting (%s, %s, %s). Error information: %s" % (codi, tipus, dietista))
    #conn.commit()

    dietes_inserted += 1


def create_rutines(cur):
  print("%d Dietes will be inserted." % num_rutines)
  cur.execute("DROP TABLE IF EXISTS Rutines CASCADE")
  cur.execute("""CREATE TABLE Rutines(
	codi varchar(8) NOT NULL,
	tipus varchar(20) NOT NULL,
	entrenador varchar (9) NOT NULL,
PRIMARY KEY (codi),
FOREIGN KEY (entrenador) references Empleats(dni) on update cascade on delete restrict
);

""")

  rutines_inserted = 0
  while rutines_inserted < num_rutines:
    print(rutines_inserted+1, end = '\r')

    codi  = ''.join(fake.random_letters(length=4)) + str(fake.random_int(min=1000, max=9999))
    tipus = fake.random_element(elements=("Augment de massa muscular", "Pèrdua de greix", "Augment de força", "Estiraments", "Rendiment esportiu", "Cardio", "Crossfit", "Calistenia"))
    # seleccionem un entrenador aleatori
    cur.execute("SELECT dni FROM Empleats WHERE tipus = 'entrenador' ORDER BY RANDOM() LIMIT 1")
    entrenador = cur.fetchone()[0]
    try:
            cur.execute("INSERT INTO Classes VALUES ('%s', '%s', '%s')" % (codi, tipus, entrenador))
    except psycopg2.IntegrityError as e:
            conn.rollback()
            print("Error inserting (%s, %s, %s). Error information: %s" % (codi, tipus, entrenador))
    #conn.commit()

    rutines_inserted += 1


def create_clients(cur):
  print("%d empleats will be inserted." % num_clients)
  cur.execute("DROP TABLE IF EXISTS Clients CASCADE")
  cur.execute("""CREATE TABLE Clients(
  dni varchar(9) NOT NULL,
  inici date NOT NULL,
	sou numeric (7,2) NOT NULL,
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
);
""")

  clients_inserted = 0
  current_ciutat = 0
  
  while clients_inserted < num_clients:
    print(clients_inserted+1, end = '\r')
    # Generate unique dni
    dni = str(randint(10000000, 99999999)) + fake.random_letter()
    inici = fake.date_between(start_date='-5y', ens_date='today')
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
    nom_ciutat   = cur.fetchone()[0]
    codi_postal = cur.fetchone()[1]

    try:
        cur.execute("INSERT INTO Empleats VALUES %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (dni, inici, adreca, correu, nom, cognoms, compte_bancari, telefon, naixement, sexe, pes, alcada, greix, massa_ossia, massa_muscular, estat, nom_ciutat, codi_postal))
    except psycopg2.IntegrityError as e:
        conn.rollback()
        print("Error inserting (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s). Error information: %s" % (dni, inici, adreca, correu, nom, cognoms, compte_bancari, telefon, naixement, sexe, pes, alcada, greix, massa_ossia, massa_muscular, estat, nom_ciutat, codi_postal))
    #conn.commit()
    clients_inserted += 1
    current_ciutat += 1


def create_pagaments(cur):
  print("%d Dietes will be inserted." % num_s)
  cur.execute("DROP TABLE IF EXISTS Pagaments CASCADE")
  cur.execute("""CREATE TABLE Pagaments(
data date NOT NULL,
client varchar(9) NOT NULL,	
Pagament_efectuat bool,
PRIMARY KEY (data, client),
FOREIGN KEY (client) references Clients(dni) on update cascade on delete restrict
);

""")

  cur.execute("SELECT dni, inici, estat FROM Clients")
  clients = cur.fetchone()
  for client in clients:
    days = llista_laborables_periode(client[1], datetime.date.today())

  for day in days:
    try:
      cur.execute("INSERT INTO Classes VALUES ('%s', '%s', '%s')" % (day, client[0], True))
    except psycopg2.IntegrityError as e:
      conn.rollback()
      print("Error inserting (%s, %s, %s). Error information: %s" % (day, client[0], True))

  if (client[2] == 'X'):
    try:
      cur.execute("""UPDATE Pagaments 
      SET Pagament_efectuat = False
    WHERE client = 'dni' AND data = (
    SELECT MAX(data) FROM Pagaments WHERE client = 'dni'
    );""")
    except psycopg2.IntegrityError as e:
      conn.rollback()
      print("Error updating last date for client "+str(client))
  #conn.commit()


def create_quantificador_dietes(cur):
  print("%d Dietes will be inserted." % num_quantificador_dietes)
  cur.execute("DROP TABLE IF EXISTS Dietes CASCADE")
  cur.execute("""CREATE TABLE Quantificadors_Dietes(
	quantificador numeric(4,2) NOT NULL,
	dieta varchar(8) NOT NULL,
   	client varchar(9) NOT NULL,
	dietista varchar(9),
PRIMARY KEY (dieta, client),
FOREIGN KEY (dieta) references Dietes(codi) on update cascade on delete cascade,
FOREIGN KEY (client) references Clients(dni) on update cascade on delete cascade,
FOREIGN KEY (dietista) references Empleats(dni) on update cascade on delete restrict
);
""")

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
            cur.execute("INSERT INTO Classes VALUES ('%s', '%s', '%s', '%s')" % (quantificador, dieta, client, dietista))
    except psycopg2.IntegrityError as e:
            conn.rollback()
            print("Error inserting (%s, '%s', %s, %s). Error information: %s" % (quantificador, dieta, client, dietista))
    #conn.commit()

    quantificador_dietes_inserted += 1


def create_quantificador_rutines(cur):
  print("%d Dietes will be inserted." % num_quantificador_rutines)
  cur.execute("DROP TABLE IF EXISTS Dietes CASCADE")
  cur.execute("""
CREATE TABLE Quantificadors_Pesos(
	quantificador numeric(4,2) NOT NULL,
	rutina varchar(8) NOT NULL,
   	client varchar(9) NOT NULL,
	entrenador varchar(9),
PRIMARY KEY (rutina, client),
FOREIGN KEY (rutina) references Rutines(codi) on update cascade on delete cascade,
FOREIGN KEY (client) references Clients(dni) on update cascade on delete cascade,
FOREIGN KEY (entrenador) references Empleats(dni) on update cascade on delete restrict
);
""")

  quantificador_rutines_inserted = 0
  while quantificador_rutines_inserted < num_quantificador_rutines:
    print(quantificador_rutines_inserted+1, end = '\r')
    quantificador = fake.pyfloat(left_digits=1, right_digits=2, positive=True, min_value=0.2, max_value=3)
    # seleccionem un client aleatori
    cur.execute("SELECT dni FROM Clients ORDER BY RANDOM() LIMIT 1")
    client = cur.fetchone()[0]
    # seleccionem una dieta aleatoria
    cur.execute("SELECT codi FROM Dietes ORDER BY RANDOM() LIMIT 1")
    dieta = cur.fetchone()[0]
    # seleccionem un dietista aleatori
    cur.execute("SELECT dni FROM Empleats WHERE tipus = 'entrenador' ORDER BY RANDOM() LIMIT 1")
    entrenador = cur.fetchone()[0]
    try:
            cur.execute("INSERT INTO Classes VALUES ('%s', '%s', '%s', '%s')" % (quantificador, dieta, client, entrenador))
    except psycopg2.IntegrityError as e:
            conn.rollback()
            print("Error inserting (%s, '%s', %s, %s). Error information: %s" % (quantificador, dieta, client, entrenador))
    #conn.commit()

    quantificador_rutines_inserted += 1


def create_apats(cur):

  print("%d Dietes will be inserted." % num_apats)
  cur.execute("DROP TABLE IF EXISTS Apats CASCADE")
  cur.execute("""CREATE TABLE Apats(
dieta varchar(8) NOT NULL,
dia varchar(9) NOT NULL,
PRIMARY KEY (dieta,dia)
);

""")
  cur.execute("DROP TABLE IF EXISTS Franges_Horaries CASCADE")
  cur.execute("""CREATE TABLE Franges_Horaries(
hora time NOT NULL,
dieta varchar(8) NOT NULL,
dia varchar(9) NOT NULL,
PRIMARY KEY (hora, dieta, dia),
FOREIGN KEY (dieta, dia) references Apats(dieta,dia) on update cascade on delete cascade,
);
""")
  cur.execute("DROP TABLE IF EXISTS Quantitats_Aliments CASCADE")
  cur.execute("""CREATE TABLE Quantitats_Aliments(
quantitat numeric(3, 2) NOT NULL,
unitats varchar(10) NOT NULL,
hora time NOT NULL,
dieta varchar(8) NOT NULL,
dia varchar(9) NOT NULL,
aliment varchar(20) NOT NULL,
PRIMARY KEY (hora, dieta, dia, aliment),
FOREIGN KEY (aliment) references Aliments(nom) on update cascade on delete cascade
);
""")

  apats_inserted = 0
  while apats_inserted < num_apats:
    n_dia=0
    print(apats_inserted+1, end = '\r')
    nombre_dies = fake.fake.random_int(min=1, max=7)
    # seleccionem un client aleatori
    cur.execute("SELECT dia FROM dies ORDER BY RANDOM() LIMIT '%s'" % (nombre_dies))
    dies = cur.fetchone()
    # seleccionem una dieta aleatoria
    cur.execute("SELECT codi FROM Dietes ORDER BY RANDOM() LIMIT 1")
    dieta = cur.fetchone()[0]
    try:
            cur.execute("INSERT INTO Apats VALUES ('%s', '%s')" % (dieta, dies[n_dia]))

            nombre_franges = fake.fake.random_int(min=1, max=7)
            for i in range(nombre_franges):
                random_datetime = fake.pydatetime()
                hora = random_datetime.hour
                try: 
                    cur.execute("INSERT INTO Franges_Horaries VALUES ('%s', '%s', '%s')" % (hora, dieta, dies[n_dia]))
                    nombre_quantitats = fake.fake.random_int(min=1, max=10)
                    for j in range(nombre_quantitats):
                        cur.execute("SELECT nom FROM Aliments ORDER BY RANDOM() LIMIT 1")
                        aliment = cur.fetchone()[0]
                        quantitat = fake.pyfloat(left_digits=3, right_digits=1, positive=True, min_value=0.5, max_value=180)
                        unitats = fake.random_element(elements=('litres', 'grams', 'kilograms', 'unitats', 'dotzenes'))
                        try: 
                          cur.execute("INSERT INTO Quantitats_Aliments VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (quantitat, unitats, hora, dieta, dies[n_dia], aliment))
                        except:
                          conn.rollback()
                          print("Error 43785687 - Call your system manager for more detailed information")
                except:
                  conn.rollback()
                  print("Error 43785687 - Call your system manager for more detailed information")

    except psycopg2.IntegrityError as e:
            conn.rollback()
            print("Error inserting (%s, '%s')." % (dieta, dies[n_dia]))
    #conn.commit()
    n_dia += 1
    apats_inserted += 1


def create_entrenaments(cur):

  print("%d Entrenaments will be inserted." % num_entrenaments)
  cur.execute("""DROP TABLE IF EXISTS Entrenaments CASCADE
  DROP TABLE IF EXISTS Entrenaments_diaris CASCADE
  DROP TABLE IF EXISTS Entrenaments_Personals CASCADE
  DROP TABLE IF EXISTS Rondes CASCADE
  DROP TABLE IF EXISTS Series CASCADE
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
entrenament varchar(8) NOT NULL,
exercici varchar(8) NOT NULL,
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
);
""")

  entrenaments_inserted = 0
  while entrenaments_inserted < num_entrenaments:
    print(entrenaments_inserted+1, end = '\r')
    codi = ''.join(fake.random_letters(length=4)) + str(fake.random_int(min=1000, max=9999))
    try:
      cur.execute("INSERT INTO Entrenaments VALUES ('%s')" % (codi,))
      if entrenaments_inserted > num_entrenaments*0.1:
            cur.execute("SELECT dni, inici FROM Clients ORDER BY RANDOM() LIMIT 1")
            client = cur.fetchone()[0]
            inici = cur.fetchone()[1]
            data = fake.date_between(inici, end_date='today')
            hora = random_datetime.hour()
            cur.execute("SELECT codi FROM Entrenaments_Personals ORDER BY RANDOM() LIMIT 1")
            plantilla = cur.fetchone()[0]
            try:
                cur.execute("INSERT INTO Entrenaments_Personals VALUES ('%s', '%s', '%s', '%s', '%s')" % (codi, data, hora, client, plantilla))
                fill_entrenament(cur, codi)
            except:
                conn.rollback()
                print("Error 465354 - Call your system manager for more detailed information")
      else:
            cur.execute("SELECT codi FROM Rutines ORDER BY RANDOM() LIMIT 1")
            rutina = cur.fetchone()[0]
            nombre_dies = fake.fake.random_int(min=1, max=7)
            cur.execute("SELECT dia FROM dies ORDER BY RANDOM() LIMIT '%s'" % (nombre_dies))
            dies = cur.fetchone()
            for dia in dies:
                try:
                    cur.execute("INSERT INTO Entrenaments_Personals VALUES ('%s', '%s', '%s')" % (codi, rutina, dia))
                    fill_entrenament(cur, codi)
                except:
                    conn.rollback()
                    print("Error 345465 - Call your system manager for more detailed information")
    except:
      conn.rollback()
      print("Error 54656 - Call your system manager for more detailed information")
    entrenaments_inserted += 1



def create_realitza_exercicis(cur):
  print("%d Realitza_Exercicis will be inserted." % num_realitza_exercicis)
  cur.execute("DROP TABLE IF EXISTS Realitza_Exercicis CASCADE")
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
  exercicis = cur.fetchone()

  for exercici in exercicis:
    nombre_quantitats = fake.fake.random_int(min=sales_per_exercici/2, max=1.5*sales_per_exercici)
    for j in range(nombre_quantitats):
      print(realitza_exercicis_inserted+1, end = '\r')

      cur.execute("SELECT codi, codi_gimnas FROM Sales ORDER BY RANDOM() LIMIT 1")
      sala = cur.fetchone()[0]
      gimnas = cur.fetchone()[1]

      try:
          cur.execute("INSERT INTO Realitza_Exercicis VALUES ('%s', '%s')" % (exercici, gimnas, sala))
      except psycopg2.IntegrityError as e:
          conn.rollback()
          print("Error inserting (%s, %s). Error information: %s" % (exercici, gimnas, sala, e))
      #conn.commit()
      
      realitza_exercicis_inserted += 1


def create_participacions(cur):
  print("%d Participacions will be inserted." % num_participacions)
  cur.execute("DROP TABLE IF EXISTS Participacions CASCADE")
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
    client = cur.fetchone()[0]
    inici = cur.fetchone()[1]

    # seleccionem una classe aleatoria
    cur.execute("SELECT codi, data FROM Classes ORDER BY RANDOM() LIMIT 1")
    classe = cur.fetchone()[0]
    data = cur.fetchone()[1]

    # verificar que la data en la que ha entrat el client es inferior a la data de la classe
    if inici < data:   
      try:
          cur.execute("INSERT INTO Participacions VALUES ('%s', '%s')" % (client, classe))
      except psycopg2.IntegrityError as e:
          conn.rollback()
          print("Error inserting (%s, %s). Error information: %s" % (client, classe, e))
      #conn.commit()
      participacions_inserted += 1


##########################################################Funcions auxiliars a les de crear#######################################################

def primer_laborable(year, month):
    for day in range(1, 8):
        date = datetime.date(year, month, day)
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
    nombre_rondes = fake.fake.random_int(min=1, max=15)
    for ordre in range(1, nombre_rondes):
        codi = ''.join(fake.random_letters(length=4)) + str(fake.random_int(min=1000, max=9999))
        cur.execute("SELECT nom FROM Exercicis ORDER BY RANDOM() LIMIT 1")
        exercici = cur.fetchone()[0]
        try: 
            cur.execute("INSERT INTO Franges_Horaries VALUES ('%s', '%s', '%s')" % (codi, ordre, entrenament, exercici))
            nombre_series = fake.fake.random_int(min=1, max=10)
            for j in range(1, nombre_series):
                cur.execute("SELECT nom FROM Aliments ORDER BY RANDOM() LIMIT 1")
                aliment = cur.fetchone()[0]
                pes = fake.pyfloat(left_digits=3, right_digits=1, positive=True, min_value=0, max_value=200)
                tipus = fake.fake.random_int(min=0, max=8)
                if tipus == 8:
                  duracio_segons = fake.random_int(min=5, max=120)
                  duracio = timedelta(seconds=duracio_segons)
                  try: 
                    cur.execute("INSERT INTO Series VALUES ('%s', '%s', NULL, '%s', '%s')" % (j, pes, duracio, codi))
                  except:
                    conn.rollback()
                    print("Error 4387596847 - Call your system manager for more detailed information")
                else:
                  num_repeticions =  fake.fake.random_int(min=0, max=30)
                  try: 
                    cur.execute("INSERT INTO Series VALUES ('%s', '%s', '%s', NULL, '%s')" % (j, pes, num_repeticions, codi))
                  except:
                    conn.rollback()
                    print("Error 3954867587 - Call your system manager for more detailed information")
        except:
          conn.rollback()
          print("Error 54651635 - Call your system manager for more detailed information")



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
#create_empleats(cur)
create_gimnasos(cur)
create_treballadors(cur)
create_sales(cur)
create_classes(cur)
create_dies(cur)
create_aliments(cur)
create_dietes(cur)
create_rutines(cur)
create_clients(cur)
create_pagaments(cur)
create_quantificador_dietes(cur)
create_quantificador_rutines(cur)
create_apats(cur)
create_entrenaments(cur)
create_realitza_exercicis(cur)
create_participacions(cur)



conn.commit()
cur.close()
conn.close()
