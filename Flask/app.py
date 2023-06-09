from flask import Flask, render_template, jsonify, redirect, url_for, request
import psycopg2
import random
from urllib.parse import urlencode
from faker import Faker
import datetime
import time

fake = Faker('es_ES')


app = Flask(__name__)
# Configure PostgreSQL connection parameters
conn = psycopg2.connect(
    host="ubiwan.epsevg.upc.edu",
    database="est_a4033441",
    user="est_a4033441",
    password="dB.a4033441",
    options=f'-c search_path=practica'
)
# Define route and view for the index page
@app.route('/')
def index():

    # Render the template with the fetched data
    return render_template('index.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE correu_electronic = %s AND passwords = %s", (email, password))
        data = cursor.fetchall()
        cursor.close()

        

        if email == 'admin' and password == 'admin':
            return redirect('/admin_dashboard')
        elif len(data) > 0:
            query_params = urlencode({'data': data[0]})  # Encode data as query parameter
            return redirect(f'/client_dashboard?{query_params}')

    return render_template('login.html')

#######################################################################
#                           ADMIN DASHBOARD                           #
#######################################################################

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/treballadors', methods=['GET', 'POST'])
def treballadors():

    if request.method == 'POST':
        if 'nom' in request.form:
            dades = request.form['nom'].split(' ')
            nom = dades[0]
            print(dades)
            cursor = conn.cursor()

            if len(dades) == 1:
                cursor.execute("SELECT * FROM empleats where nom = %s", (nom,))

            if len(dades) == 2:
                cognoms = dades[1] + ' '
                cursor.execute("SELECT * FROM empleats where nom = %s and cognoms = %s", (nom, cognoms))
            
            if len(dades) == 3:
                cognoms = dades[1] + ' ' + dades[2]
                cursor.execute("SELECT * FROM empleats where nom = %s and cognoms = %s", (nom, cognoms))
            
            else:       
                cursor.execute("SELECT * FROM empleats LIMIT 1000")
            
            all_empleats = cursor.fetchall()
            cursor.close()
            # Render the template with the fetched data, current page, and total pages
            return render_template('treballadors.html', empleats=all_empleats, current_page=1, total_pages=1)

    # Obtenir el número de pàgina dels paràmetres de la consulta
    page = request.args.get('page', default=1, type=int)
    empleats_per_page = 10

    # Recuperar dades de la base de dades
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleats LIMIT 1000")
    all_empleats = cursor.fetchall()
    cursor.close()

    # calcula el nombre total d'empleats recuperats de la base de dades.
    total_empleats = len(all_empleats)
    # calcula el nombre total de pàgines necessàries per mostrar tots els empleats. Utilitza la divisió entera per arrodonir cap amunt.
    total_pages = (total_empleats + empleats_per_page - 1) // empleats_per_page
    # calcula l'índex inicial de l'empleat a mostrar per a la pàgina actual.
    start_index = (page - 1) * empleats_per_page
    # calcula l'índex final de l'empleat a mostrar per a la pàgina actual.
    end_index = start_index + empleats_per_page
    # selecciona els empleats corresponents a la pàgina actual a partir de la llista completa d'empleats.
    empleats = all_empleats[start_index:end_index]

    # Render the template with the fetched data, current page, and total pages
    return render_template('treballadors.html', empleats=empleats, current_page=page, total_pages=total_pages)

@app.route('/afegir_empleat', methods=['GET', 'POST'])
def afegir_empleat():

    if request.method == 'POST':
        dni = request.form.get('dni')
        tipus = request.form.get('tipus')
        sou = request.form.get('sou')
        nom = request.form.get('nom')
        cognoms = request.form.get('cognoms')
        compte_bancari = request.form.get('compte_bancari')
        telefon = request.form.get('telefon')
        data_naixement = request.form.get('data_naixement')
        sexe = request.form.get('sexe')
        horaris = request.form.get('horaris')
        nom_ciutat = request.form.get('nom_ciutat')
        codi_postal = request.form.get('codi_postal')

        print(dni, tipus, sou, nom, cognoms, compte_bancari, telefon, data_naixement, sexe, horaris, nom_ciutat, codi_postal)

        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Empleats VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (dni, tipus, sou, nom, cognoms, compte_bancari, telefon, data_naixement, sexe, horaris, nom_ciutat, codi_postal))
            conn.commit()
        except psycopg2.IntegrityError as e:
            print(e)
            conn.rollback()
        cursor.close()

    # Render the template with the fetched data, current page, and total pages
    return render_template('afegir_empleat.html')

@app.route('/esborrar_empleat', methods=['GET', 'POST'])
def esborrar_empleat():
    if request.method == 'POST':
        # Retrieve form data
        dni = request.form.get('dni')
        
        # Perform deletion query using the provided name
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM empleats WHERE dni = %s", (dni,))
            conn.commit()
            
        except psycopg2.IntegrityError as e:
            conn.rollback()
        cursor.close()

    
    return render_template('esborrar_empleat.html')

@app.route('/empleat/<empleat_id>')
def show_empleat_details(empleat_id):

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute the query to retrieve the worker details
    query = "SELECT * FROM empleats WHERE dni = %s"
    cursor.execute(query, (empleat_id,))

    # Fetch the result
    worker_details = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()

    # create random number between 1 and 99
    random_number = random.randint(1, 99)

    worker_details = worker_details + (random_number,)

    # Render the empleat.html template with the worker's details
    return redirect(url_for('show_empleat', worker_details=worker_details))

@app.route('/empleat')
def show_empleat():
    # Get the worker details from the URL parameter
    worker_details = request.args.getlist('worker_details')

    # Render the empleat.html template with the worker's details
    return render_template('empleat.html', data=worker_details)

@app.route('/clients', methods=['GET', 'POST'])
def clients():

    if request.method == 'POST':
        if 'nom' in request.form:
            dades = request.form['nom'].split(' ')
            nom = dades[0]  
            print(dades)
            cursor = conn.cursor()

            if len(dades) == 1:
                cursor.execute("SELECT * FROM clients where nom = %s", (nom,))

            if len(dades) == 2:
                cognoms = dades[1] + ' '
                cursor.execute("SELECT * FROM clients where nom = %s and cognoms = %s", (nom, cognoms))
            
            if len(dades) == 3:
                cognoms = dades[1] + ' ' + dades[2]
                cursor.execute("SELECT * FROM clients where nom = %s and cognoms = %s", (nom, cognoms))
            
            else:       
                cursor.execute("SELECT * FROM clients LIMIT 1000")

            all_clients = cursor.fetchall()
            cursor.close()

            # Render the template with the fetched data, current page, and total pages
            return render_template('clients.html', clients=all_clients, current_page=1, total_pages=1)

    # Obtenir el número de pàgina dels paràmetres de la consulta
    page = request.args.get('page', default=1, type=int)
    clients_per_page = 10

    # Recuperar dades de la base de dades
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients LIMIT 1000")
    all_clients = cursor.fetchall()
    cursor.close()

    # calcula el nombre total d'empleats recuperats de la base de dades.
    total_clients = len(all_clients)
    # calcula el nombre total de pàgines necessàries per mostrar tots els empleats. Utilitza la divisió entera per arrodonir cap amunt.
    total_pages = (total_clients + clients_per_page - 1) // clients_per_page
    # calcula l'índex inicial de l'empleat a mostrar per a la pàgina actual.
    start_index = (page - 1) * clients_per_page
    # calcula l'índex final de l'empleat a mostrar per a la pàgina actual.
    end_index = start_index + clients_per_page
    # selecciona els empleats corresponents a la pàgina actual a partir de la llista completa d'empleats.
    clients = all_clients[start_index:end_index]

    # Render the template with the fetched data, current page, and total pages
    return render_template('clients.html', clients=clients, current_page=page, total_pages=total_pages)

@app.route('/client/<client_id>')
def show_client_details(client_id):

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute the query to retrieve the worker details
    query = "SELECT * FROM clients WHERE dni = %s"
    cursor.execute(query, (client_id,))

    # Fetch the result
    client_details = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()

    # create random number between 1 and 99
    random_number = random.randint(1, 99)

    client_details = client_details

    # Render the empleat.html template with the worker's details
    return redirect(url_for('show_client', client_details=client_details, random_number = random_number))

@app.route('/client_info')
def show_client():
    # Get the worker details from the URL parameter
    client_details = request.args.getlist('client_details')
    random_number = request.args.getlist('random_number')
    print(random_number)

    # Render the empleat.html template with the worker's details
    return render_template('clients_info.html', data=client_details, random_number=random_number)

@app.route('/afegir_client', methods=['GET', 'POST'])
def afegir_client():

    if request.method == 'POST':
        dni = request.form.get('dni')
        inici = request.form.get('inici')
        adreca = request.form.get('adreca')
        correu = request.form.get('correu')
        nom = request.form.get('nom')
        cognoms = request.form.get('cognoms')
        compte_bancari = request.form.get('compte_bancari')
        telefon = request.form.get('telefon')
        data_naixement = request.form.get('data_naixement')
        sexe = request.form.get('sexe')
        pes = request.form.get('pes')
        alcada = request.form.get('alcada')
        greix = request.form.get('greix')
        massa_ossia = request.form.get('massa_ossia')
        massa_muscular = request.form.get('massa_muscular')
        estat = request.form.get('estat')
        nom_ciutat = request.form.get('nom_ciutat')
        codi_postal = request.form.get('codi_postal')
        password = request.form.get('password')

        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO Clients VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (dni, inici, adreca, correu, nom, cognoms, compte_bancari, telefon, data_naixement, sexe, pes, alcada, greix, massa_ossia, massa_muscular, estat, nom_ciutat, codi_postal, password))
            conn.commit()
        except psycopg2.IntegrityError as e:
            print(e)
            conn.rollback()
        cursor.close()

    # Render the template with the fetched data, current page, and total pages
    return render_template('afegir_client.html')

@app.route('/esborrar_client', methods=['GET', 'POST'])
def esborrar_client():
    if request.method == 'POST':
        # Retrieve form data
        dni = request.form.get('dni')
       
        # Perform deletion query using the provided name
        cursor = conn.cursor()

        try:
            # Primer borrem a la taula pagaments ja que hi ha una FK de la taula clients a la taula pagaments i no es pot borrar un client si te pagaments
            cursor.execute("DELETE FROM pagaments WHERE client = %s", (dni,))
            cursor.execute("DELETE FROM clients WHERE dni = %s", (dni,))
            conn.commit()
            
        except psycopg2.IntegrityError as e:
            print(e)
            conn.rollback()
        cursor.close()

    
    return render_template('esborrar_client.html')


#######################################################################
#                           CLIENT DASHBOARD                           #
#######################################################################

# Admin Dashboard Page
@app.route('/client_dashboard')
def client_dashboard():

    data = request.args.getlist('data')
    data = (data[0][1:-1]).split(',')
    dni = data[0][1:].strip("'")

    print(data)

    massa_ossia = float(data[16][9:-1].strip("'"))
    massa_muscular = float(data[17][9:-1].strip("'"))
    pes = float(data[13][9:-1].strip("'"))
    alcada = float(data[14][9:-1].strip("'"))
    greix = float(data[15][9:-1].strip("'"))
    
    parametres_medics = [massa_ossia, massa_muscular, pes, alcada, greix]

    dades = get_dades(data)

    return render_template('client_dashboard.html', dades=dades, parametres_medics=parametres_medics)

@app.route('/info_client_actualitzada', methods=['POST'])
def info_client_actualitzada():

    if request.method == 'POST':
        correu = request.form['correu']
        telefon = request.form['telefon']
        adreca = request.form['adreca']
        compte_bancari = request.form['compte_bancari']
        contrassenya = request.form['contrassenya']
        dni = request.form['dni']

        cursor = conn.cursor()
        cursor.execute("UPDATE clients SET correu_electronic = %s, telefon = %s, adreca = %s, compte_bancari = %s, passwords = %s WHERE dni = %s", (correu, telefon, adreca, compte_bancari, contrassenya, dni))
        conn.commit()

        cursor.execute("SELECT * FROM clients WHERE correu_electronic = %s AND passwords = %s", (correu, contrassenya))
        data = cursor.fetchall()
        cursor.close()

        random_number = random.randint(1, 99)

        dades = []
        dades.append(data[0][4] + ' ' + data[0][5])
        dades.append(data[0][3])
        dades.append(data[0][7])
        dades.append(data[0][0])
        dades.append(data[0][2])
        dades.append(data[0][6])
        dades.append(data[0][8])
        dades.append(data[0][15])
        dades.append(data[0][18])
        dades.append(random_number)

        massa_ossia = float(data[0][13])
        massa_muscular = float(data[0][14])
        pes = float(data[0][10])
        alcada = float(data[0][11])
        greix = float(data[0][12])

        parametres_medics = [massa_ossia, massa_muscular, pes, alcada, greix]


    return render_template('client_dashboard.html', dades=dades, parametres_medics=parametres_medics)

def get_dades (data):

    dades = []

    dni = data[0][1:].strip("'")
    nom = data[6][1:].strip("'")
    cognom = data[7][1:].strip("'")
    compte_bancari = data[8][1:].strip("'")
    correu = data[5][1:].strip("'")
    adreca = data[4][1:].strip("'")
    data_naixement = data[10][15:].strip("'") + '/' + data[11][1:].strip("'") + '/' + data[12][1:-1].strip("'")
    telefon = data[9][9:-1].strip("'")
    estat = data[19][1:].strip("'")
    contrassenya = data[22][1:].strip("'")
    random_number = random.randint(1, 99)

    dades.append(nom + ' ' + cognom)
    dades.append(correu)
    dades.append(telefon)
    dades.append(dni)
    dades.append(adreca)
    dades.append(compte_bancari)
    dades.append(data_naixement)
    dades.append(estat)
    dades.append(contrassenya)
    dades.append(random_number)

    return dades

@app.route('/entrenaments', methods=['GET', 'POST'])
def entrenaments():

    dni = request.args.get('dni')

    return render_template('entrenaments.html', dni=dni)

@app.route('/rutina_propia', methods=['GET', 'POST'])
def rutina_propia():

    dni = request.args.get('dni')
    codi_exercici = request.args.get('exercici')
    pes = request.args.get('pes')
    creat = request.args.get('creat')
    codi_entrenament = request.args.get('codi_entrenament')
    ronda = request.args.get('ronda')
    serie = 1
    codi_ronda = request.args.get('codi_ronda')
    repeticions = request.args.get('repeticions')
    num_exercici = request.args.get('num_exercici')
    num_exercici = int(num_exercici)

    cursor = conn.cursor()

    if creat == 'true':
        # creem codi ronda que no estigui ja a la base de dades
        while True:
            codi_ronda = ''.join(fake.random_letters(length=4)) + str(fake.random_int(min=1000, max=9999))
            print(codi_ronda)
            cursor.execute("select count(*) from rondes where codi = %s", (codi_ronda,))
            ronda = cursor.fetchall()[0][0]
            if ronda == 0:
                break

        # Mirem si hi ha algun entrenament creat
        cursor.execute("select count(*) from rondes where entrenament = %s", (codi_entrenament,))
        entrenament = cursor.fetchall()[0][0]
        if entrenament > 0:
            cursor.execute("select max(ordre) from rondes where entrenament = %s", (codi_entrenament,))
            ordre = cursor.fetchall()[0][0]
            ordre = ordre + 1

        else:
            ordre = 1
        
        cursor.execute("INSERT INTO rondes VALUES(%s, %s, %s, %s)", (codi_ronda, ordre, codi_entrenament, codi_exercici))
        conn.commit()

    if ronda == 'true':
        cursor.execute("select count(*) from series where ronda = %s", (codi_ronda,))
        ronda = cursor.fetchall()[0][0]

        # Si no hi ha cap serie la creem
        if ronda == 0:
            cursor.execute("insert into series values(%s, %s, %s, %s, %s)", (serie, pes, repeticions, None, codi_ronda))
            conn.commit()

        else:
            # obtenim numero series
            cursor.execute("select num_serie from series where ronda = %s", (codi_ronda,))
            serie = cursor.fetchall()[0][0]
            serie = serie + 1
            print(serie)
            cursor.execute("UPDATE series SET num_serie = %s, pes = %s, num_repeticions = %s WHERE ronda = %s", (serie, pes, repeticions, codi_ronda))
            conn.commit()

    cursor.execute("select nom from exercicis where codi = %s", (codi_exercici,))
    exercici = cursor.fetchall()[0]

    cursor.close()

    return render_template('rutina_propia.html', dni=dni, exercici=exercici, codi_exercici=codi_exercici, serie=serie, codi_ronda=codi_ronda, num_exercici=num_exercici, codi_entrenament=codi_entrenament)

@app.route('/selecciona_exercici', methods=['GET', 'POST'])
def selecciona_exercici():

    dni = request.args.get('dni')
    creat = request.args.get('creat')
    num_exercici = request.args.get('num_exercici')
    nou_exercici = request.args.get('nou_exercici')
    

    if num_exercici == None:
        num_exercici = 0

    if nou_exercici == 'true':
        num_exercici = int(num_exercici)+1

    cursor = conn.cursor()

    if creat == 'true':
        codi = ''.join(fake.random_letters(length=4)) + str(fake.random_int(min=1000, max=9999))
        data = time.strftime("%Y-%m-%d")
        hora = time.strftime("%H:%M:%S")

        cursor.execute("INSERT INTO Entrenaments VALUES ('%s')" % (codi,))
        conn.commit()
        cursor.execute("insert into entrenaments_personals values (%s, %s, %s, %s, %s)", (codi, data, hora, dni, None))
        conn.commit()

    elif creat == 'false':
        codi = request.args.get('codi_entrenament')
    
    cursor.execute("select * from exercicis groupby(nom)")
    exercicis = cursor.fetchall()
    cursor.close()

    return render_template('selecciona_exercici.html', exercicis=exercicis, codi=codi, num_exercici=num_exercici)

@app.route('/hist_Classes')
def hist_Classes():

    dni = request.args.get('dni')

    # Obtenim les classes per aquest client
    classes_realitzades = []
    cursor = conn.cursor()
    cursor.execute("select classe from participacions where client = %s", (dni,))
    classes = cursor.fetchall()
    for classe in classes:
        cursor.execute("select * from classes where codi = %s", (classe[0],))
        nom_classe = cursor.fetchall()
        classes_realitzades.append(nom_classe[0])

    tutors = []
    for tutor in classes_realitzades:
        cursor.execute("select * from empleats where dni = %s", (tutor[7],))
        nom_tutor = cursor.fetchall()
        tutors.append(nom_tutor[0][3] + ' ' + nom_tutor[0][4])

    cursor.close()

    longitud = len(classes_realitzades)

    return render_template('hist_Classes.html', longitud=longitud, classes_realitzades=classes_realitzades, tutors=tutors)

@app.route('/hist_Rutines')
def hist_Rutines():

    dni = request.args.get('dni')

    # Obtenim les classes per aquest client
    rutines_realitzades = []
    cursor = conn.cursor()
    cursor.execute("select * from entrenaments_personals where client = %s", (dni,))
    classes = cursor.fetchall()
    for classe in classes:
        rutines_realitzades.append(classe)
        print(classe)

    cursor.close()

    longitud = len(rutines_realitzades)

    return render_template('hist_Rutines.html', longitud=longitud, rutines_realitzades=rutines_realitzades)

from flask import request

@app.route('/apuntar_classe', methods=['GET', 'POST'])
def apuntar_classe():
    dni = request.args.get('dni')  # Get the 'dni' value from the query parameters
    print(dni)

    if request.method == 'POST':
        classe_seleccionada = request.json.get('selectedClass')
        print(classe_seleccionada)
        cursor = conn.cursor()
        cursor.execute("select codi from classes where tipus = %s", (classe_seleccionada,))
        codi_classe = cursor.fetchall()[0][0]
        cursor.execute("INSERT INTO participacions VALUES (%s, %s)", (codi_classe, dni))
        conn.commit()
        cursor.close()

    cursor = conn.cursor()
    cursor.execute("select distinct tipus from classes")
    classes = cursor.fetchall()
    cursor.close()

    return render_template('apuntar_classe.html', classes=classes, dni=dni)

if __name__ == '__main__':
    app.run(debug=True)
