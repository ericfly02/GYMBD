import psycopg2
from random import randint
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

    # Check if a gimnas already exists with the same codi
    cur.execute("SELECT COUNT(*) FROM Gimnasos WHERE codi = %s", (codi,))
    count_codi = cur.fetchone()[0]

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

    if r is not None and count_codi == 0:
        try:
            encarregat = r[0]
            cur.execute("INSERT INTO Gimnasos VALUES (%s, %s, %s, %s, %s, %s, %s)", (codi, adreca, telefon, correu_electronic, nom_ciutat, codi_postal, encarregat))

        except psycopg2.IntegrityError as e:
            conn.rollback()
            print("Error inserting (%s, %s, %s, %s, %s, %s, %s). Error information: %s" % (codi, adreca, telefon, correu_electronic, nom_ciutat, codi_postal, encarregat, e))
        conn.commit()
        gimnasos_inserted += 1


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
    # Check if a sala already exists with the same codi
    cur.execute("SELECT COUNT(*) FROM Sales WHERE codi = %s", (codi,))
    count_codi = cur.fetchone()[0]

    # Select a random gimnas and its codi
    cur.execute("SELECT codi FROM Gimnasos ORDER BY RANDOM() LIMIT 1")
    codi_gimnas   = cur.fetchone()[0]

    aforament_maxim = fake.random_int(min=50, max=500)

    if count_codi == 0:
        try:
            cur.execute("INSERT INTO Sales VALUES ('%s', '%s', '%s')" % (codi, codi_gimnas, aforament_maxim))
        except psycopg2.IntegrityError as e:
            conn.rollback()
            print("Error inserting (%s, %s, %s). Error information: %s" % (codi, codi_gimnas, aforament_maxim, e))
        conn.commit()
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
    data = fake.date_between(start_date='-1y', end_date='+1y')

    duracio = fake.random_int(min=10, max=120)

    # Calculem horari random
    start = fake.random_int(min=7, max=21)  # Hours
    time_str = f"{start}:00" 
    time_obj = datetime.strptime(time_str, "%H:%M")
    final_time = (time_obj + timedelta(minutes=duracio)).time()
    hora = final_time

    # seleccionem una gimnas aleatori
    cur.execute("SELECT codi_gimnas FROM Sales ORDER BY RANDOM() LIMIT 1")
    codi_gimnas = cur.fetchone()[0]

    # seleccionem una sala aleatoria del gimnas
    cur.execute("SELECT codi FROM Sales WHERE codi_gimnas = %s ORDER BY RANDOM() LIMIT 1", (codi_gimnas,))
    
    codi_sala = cur.fetchone()[0]

    # seleccionem un tutor aleatori del gimnas
    cur.execute("SELECT codi_postal FROM Gimnasos WHERE codi = %s ORDER BY RANDOM() LIMIT 1", (codi_gimnas,))
    result = cur.fetchone()[0]
    cur.execute("SELECT dni FROM Empleats WHERE codi_postal = %s ORDER BY RANDOM() LIMIT 1", (result,))
    tutor = cur.fetchone()[0]

    if classes_inserted > 0:

        # mirar si el codi ya existe i assignarle el tipus
        cur.execute("SELECT COUNT(*) FROM Classes WHERE codi = %s", (codi,))
        count_codi = cur.fetchone()[0]

        if count_codi > 0:
            cur.execute("SELECT tipus FROM Classes WHERE codi = %s", (codi,))
            tipus = cur.fetchone()[0]

        try:
            cur.execute("INSERT INTO Classes VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (codi, tipus, data, duracio, hora, codi_sala, codi_gimnas, tutor))
        except psycopg2.IntegrityError as e:
            conn.rollback()
            print("Error inserting (%s, %s, %s, %s, %s, %s, %s, %s). Error information: %s" % (codi, tipus, data, duracio, hora, codi_sala, codi_gimnas, tutor, e))
        conn.commit()

        
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
	conn.commit()

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
    conn.commit()

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
    conn.commit()

    rutines_inserted += 1
    
def create_clients(cur):
  print("%d empleats will be inserted." % num_clients)
  cur.execute("DROP TABLE IF EXISTS Clients CASCADE")
  cur.execute("""CREATE TABLE Clients(
   	dni varchar(9) NOT NULL,
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
    if clients_inserted > 0:
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
            cur.execute("INSERT INTO Empleats VALUES %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (dni, inici, adreca, correu, nom, cognoms, compte_bancari, telefon, naixement, sexe, pes, alcada, greix, massa_ossia, massa_muscular, estat, nom_ciutat, codi_postal))
        except psycopg2.IntegrityError as e:
            conn.rollback()
            print("Error inserting (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s). Error information: %s" % (dni, inici, adreca, correu, nom, cognoms, compte_bancari, telefon, naixement, sexe, pes, alcada, greix, massa_ossia, massa_muscular, estat, nom_ciutat, codi_postal))
        conn.commit()
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
  conn.commit()


##########################################################Funcions auxiliars a les de crear#######################################################

def primer_laborable(year, month):
    for day in range(1, 8):
        date = datetime.date(year, month, day)
        if date.weekday() < 5:  # Monday = 0, Friday = 4
            return date

def llista_laborables_periode(start_date, end_date):

	dates_list = []

	while start_date < today:
		year = start_date.year
		month = start_date.month
		first_working_day = primer_laborable(year, month)
		dates_list.append(first_working_day.strftime('%d/%m/%Y'))
		start_date = first_working_day + relativedelta(months=1)
	return dates_list


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
#create_gimnasos(cur)
#create_sales(cur)
#create_classes(cur)
#create_dies(cur)


cur.close()
conn.close()
