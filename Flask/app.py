from flask import Flask, render_template, jsonify, redirect, url_for, request
import psycopg2
import random

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
        elif data:
            # Redirect to a success page or dashboard
            return redirect('/client_dashboard', data=data)

    return render_template('login.html')

# Admin Dashboard Page
@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# Define route and view for the gimnasos page
@app.route('/gimnasos')
def gimnasos():
    # Fetch data from the database
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gimnasos")
    data = cursor.fetchall()
    cursor.close()

    # Render the template with the fetched data
    return render_template('gimnasos.html', data=data)

@app.route('/treballadors', methods=['GET', 'POST'])
def treballadors():

    if request.method == 'POST':
        if 'nom' in request.form:
            nom = request.form['nom']
            # Recuperar dades de la base de dades
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM empleats where nom = %s", (nom,))
            all_empleats = cursor.fetchall()
            cursor.close()

            # Render the template with the fetched data, current page, and total pages
            return render_template('treballadors.html', empleats=all_empleats, current_page=1, total_pages=1)

    # Obtenir el número de pàgina dels paràmetres de la consulta
    page = request.args.get('page', default=1, type=int)
    empleats_per_page = 10

    # Recuperar dades de la base de dades
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleats")
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

        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO empleats VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (dni, tipus, sou, nom, cognoms, compte_bancari, telefon, data_naixement, sexe, horaris, nom_ciutat, codi_postal))
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
            nom = request.form['nom']
            # Recuperar dades de la base de dades
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients where nom = %s", (nom,))
            all_clients = cursor.fetchall()
            cursor.close()

            # Render the template with the fetched data, current page, and total pages
            return render_template('clients.html', clients=all_clients, current_page=1, total_pages=1)

    # Obtenir el número de pàgina dels paràmetres de la consulta
    page = request.args.get('page', default=1, type=int)
    clients_per_page = 10

    # Recuperar dades de la base de dades
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
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

    # Render the empleat.html template with the worker's details
    return render_template('clients_info.html', data=client_details, random_number = random_number)


if __name__ == '__main__':
    app.run(debug=True)
