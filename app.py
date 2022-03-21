from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import json
import os

#load environment to get DB username & password
load_dotenv()

app = Flask(__name__)

app.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
app.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = "crocosoft_task"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

@app.before_first_request
def create_tables():
    try:
        #create tables once for the first app run
        cursor = mysql.connection.cursor()
        cursor.execute('''
            CREATE TABLE vehicle(id INT NOT NULL AUTO_INCREMENT,
            model VARCHAR(50),
            category enum("small","family","van"),
            available_to_hire INT,
            price_per_day FLOAT,
            PRIMARY KEY (id));

            CREATE TABLE customer(id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(100),
            PRIMARY KEY (id));

            CREATE TABLE customer_hires_vehicle(hire_date DATE,
            return_date DATE, 
            vehicle_id INT,
            customer_id INT,
            FOREIGN KEY (vehicle_id) REFERENCES vehicle(id),
            FOREIGN KEY (customer_id) REFERENCES customer(id),
            PRIMARY KEY (vehicle_id,customer_id),
            CONSTRAINT check_return_date CHECK(return_date >= hire_date AND DATEDIFF(return_date,hire_date) <= 7));
        ''')
    except:
        #tables already created
        return True

#Get customer with ID
@app.route("/get_customer/<int:pk>", methods=["GET"])
def get_customer(pk):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(f'''SELECT * FROM customer WHERE id = {pk}''')
        result = cursor.fetchall()[0]
        return jsonify({
            'data': result,
        }) , 200
    except Exception as e:
        return jsonify({
            'error': f'Error: {e}',
        }) , 404

#Get all customers
@app.route("/get_customers", methods=["GET"])
def get_customers():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(f'''SELECT * FROM customer''')
        result = cursor.fetchall()
        return jsonify({
            'data': result,
        }) , 200
    except Exception as e:
        return jsonify({
            'error': f'Error: {e}',
        }) , 404

#Create new customer
@app.route("/create_customer", methods=["POST"])
def create_customer():
    customer_data = json.loads(request.data)
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(f'''INSERT INTO customer (name) values ("{customer_data.get('name')}");''')
        mysql.connection.commit()
        cursor.execute(f'''SELECT * FROM customer WHERE id = {cursor.lastrowid}''')
        result = cursor.fetchall()[0]
        return jsonify({
            'data': result,
            'msg':"Customer created successfully"
        }) , 201
    except Exception as e:
        return jsonify({
            'error': f'Error: {e}',
        }) , 400

#Update existing customer with ID
@app.route("/update_customer/<int:pk>", methods=["PUT"])
def update_customer(pk):
    customer_data = json.loads(request.data)
    try:
        print(pk)
        print(type(pk))
        cursor = mysql.connection.cursor()
        cursor.execute(f'''UPDATE customer SET name = "{customer_data.get('name')}" WHERE id = {pk};''')
        mysql.connection.commit()
        cursor.execute(f'''SELECT * FROM customer WHERE id = {pk}''')
        result = cursor.fetchall()[0]
        return jsonify({
            'data': result,
            'msg':"Customer updated successfully"
        }) , 200
    except Exception as e:
        return jsonify({
            'error': f'Error: {e}',
        }) , 400

#Delete customer with ID
@app.route("/delete_customer/<int:pk>", methods=["DELETE"])
def delete_customer(pk):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(f'''DELETE FROM customer WHERE id = {pk};''')
        mysql.connection.commit()
        return jsonify({
            'msg':"Customer deleted successfully"
        }) , 200
    except Exception as e:
        return jsonify({
            'error': f'Error: {e}',
        }) , 400

app.run(host='localhost',debug=True)