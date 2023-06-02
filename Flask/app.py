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

        # Check if email and password are correct in the Clients table
        # Perform your authentication logic here
        # Example code to check if email and password match a user in the Clients table
        data = None
        if email == 'admin' and password == 'admin':
            return redirect('/admin_dashboard')
        elif data:
            # Redirect to a success page or dashboard
            return redirect('/client_dashboard')
        else:
            # Redirect back to the login page with an error message
            return redirect('/login?error=1')

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

@app.route('/treballadors')
def treballadors():
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




if __name__ == '__main__':
    app.run(debug=True)
