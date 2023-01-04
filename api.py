import psycopg2
import psycopg2.extras
import json
import os
from flask import Flask, current_app, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import bcrypt

app = Flask(__name__)
CORS(app, origins=['https://space-explorer-nasa.netlify.app'])

# Load environment variables from .env file
load_dotenv()

# Get database connection credentials from environment variables
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')

port = os.environ['PORT']

def get_db_user_connection():
    try:
        # Use environment variables to build connection string
        conn_string = f"dbname={DB_USERNAME} user={DB_USERNAME} host={DB_HOST} password={DB_PASSWORD}"
        conn = psycopg2.connect(conn_string)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")

conn = get_db_user_connection()

def db_select(conn, query, parameters=()):
    if conn != None:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curs:
            try:
                curs.execute(query, parameters)
                data = curs.fetchall()
                return data
            except Exception as e:
                return {'code': 404, 'message': f'Error1: {e}'}
    else: 
        return {'code': 500, 'message': 'error connecting to database'}

def db_manipulate(conn, query, parameters=()):
    if conn != None:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curs:
            try:
                curs.execute(query, parameters)
                conn.commit()
                curs.close()
            except Exception as e:
                print(e)
                return {'code': 404, 'message': f'Error: {e}'}
    else: 
        return {'code': 500, 'message': 'error connecting to database'}

def create_hashed_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('UTF-8'), salt)
    return hashed.decode('UTF-8')

def compare_hashed_password(password, hashed):
    return bcrypt.checkpw(password.encode('UTF-8'), hashed.encode('UTF-8'))

@app.route('/get_user', methods=['GET', 'POST'])
def getting_user():
    data = db_select(conn, 'select * from useraccounts')
    return data



@app.route('/create_user', methods=['POST'])
def creating_user():
    credentials = request.json
    data = db_select(conn, 'select * from useraccounts')
    for username in data:
        if username['email'] == credentials[0]['email']:
            return jsonify({'message': 'failed'})
    db_manipulate(conn, "INSERT INTO useraccounts (email, password) VALUES (%s, %s)", (credentials[0]['email'], create_hashed_password(credentials[0]['password'])))
    return jsonify({'message': 'success'})

@app.route('/sign_in', methods=['POST'])
def sign_in():
    sign_in_credentials = request.json
    data = db_select(conn, 'select * from useraccounts')

    for credentials in data:
        if credentials.get('email') == sign_in_credentials[0]['email'] and compare_hashed_password(sign_in_credentials[0]['password'], credentials.get('password')):
            return jsonify({'message':'signed_in'})
    else:
        return jsonify({'message': 'incorrect_details'})

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=port)






