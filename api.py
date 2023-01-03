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
CORS(app, origins='https://space-explorer-nasa.netlify.app/')


PASS=os.getenv('PASS')
HOST=os.getenv('HOST')
port = os.environ['PORT']


def get_db_user_connection():
    try:
        conn = psycopg2.connect(f"dbname=mprhprtx user=mprhprtx host={HOST} port = 5432 password={PASS}")
        return conn
    except:
        print("couldn't connect to server")


conn = get_db_user_connection()

def db_select(conn, query, parameters=()):
    if conn != None:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curs:
            try:
                curs.execute(query, parameters)
                data = curs.fetchall()
                conn.commit()
                return data

            except:
                return {'code': 404, 'message': 'Error'}

    else: 
        return {'code': 500, 'message': 'error connecting to database'}

def db_manipulate(conn, query, parameters=()):
    if conn != None:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curs:
            try:
                curs.execute(query, parameters)
                conn.commit()
                curs.close()
            except:
                return {'code': 404, 'message': 'Error'}

    else: 
        return {'code': 500, 'message': 'error connecting to database'}


def get_all_data():
    data = db_select(conn, 'select * from useraccounts')
    return jsonify(data)

 
def create_hashed_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('UTF-8'), salt)
    # print(salt)
    # print(hashed)
    return hashed.decode('UTF-8')

def compare_hashed_password(password, hashed):

    return bcrypt.checkpw(password.encode('UTF-8'), hashed.encode('UTF-8'))

@app.route('/get_user', methods=['GET', 'POST'])
def getting_user():
    return get_all_data()



@app.route('/create_user', methods=['POST'])
def creating_user():
    credentials = request.json
    data1 = get_all_data()
    data = data1.get_json()
    print(data)
    for email in data:
        # print(email.get('email'))
        if email.get('email') == credentials[0]['email']:
            return jsonify({'message': 'failed'})
        else:
            db_manipulate(conn, "INSERT INTO useraccounts (email, password) VALUES (%s, %s)", ((credentials[0]['email'], create_hashed_password(credentials[0]['password']))))
            return jsonify({'message': 'success'})
   
    return jsonify({'message': 'user-created'})
    


@app.route('/sign_in', methods=['POST'])
def sign_in():
    sign_in_credentials = request.json
    import_all_data = get_all_data()
    database_data = tuple(import_all_data.get_json())
    # print(database_data)

    for credentials in database_data:
        # print(sign_in_credentials)
        # print(credentials.get('password'))
        # print(sign_in_credentials[0]['password'])
        # print(credentials.get('password'))
        if credentials.get('email') == sign_in_credentials[0]['email'] and compare_hashed_password(sign_in_credentials[0]['password'], credentials.get('password')):
            return jsonify({'message':'signed_in'})
    else:
        return jsonify({'message': 'incorrect_details'})

    


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=port)






