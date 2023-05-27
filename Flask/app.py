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
    # Fetch data from the database
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gimnasos")
    data = cursor.fetchall()
    cursor.close()

    # Render the template with the fetched data
    return render_template('index.html', data=data)

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
    # Fetch data from the database
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleats")
    data = cursor.fetchall()
    cursor.close()

    # Render the template with the fetched data
    return render_template('treballadors.html', data=data)

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
