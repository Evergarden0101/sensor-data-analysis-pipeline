from flask import Flask, request
import werkzeug
import os, json
import sqlite3 as sql
from database import db
from flask_cors import CORS
from SSD import *

"""Example of possible structure for posting the label data"""
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    cors = CORS(app)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'labels.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    
    # Helper functions and variables
    def insert_label(label):
        DATABASE = app.config['DATABASE']

        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute(f"INSERT INTO labels (patient, location_begin, location_end, duration) VALUES {label}")

    def get_patient_data(patient_id):
        DATABASE = app.config['DATABASE']

        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            patient_data = cur.execute(f"SELECT * FROM labels WHERE patient = {patient_id}").fetchall()

        return patient_data

    @app.route("/upload", methods=['POST'])
    def upload():
        uploaded_file = request.files['file']

        col_names = ['MR', 'ML', 'SU', 'Microphone', 'Eye', 'ECG', 'Pressure Sensor']
        csvData = pd.read_csv(uploaded_file, names=col_names, header=None)

        for i,row in csvData.iterrows():
            sql = "INSERT INTO addresses (MR, ML, SU, Microphone, Eye, ECG, Pressure Sensor) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            value = (row['MR'],row['ML'],row['SU'],row['Microphone'],row['Eye'], row['ECG'], row['Pressure Sensor'])
            mycursor.execute(sql, value, if_exists='append')
            mydb.commit()
            print(i, row['MR'],row['ML'],row['SU'],row['Microphone'],row['Eye'], row['ECG'], row['Pressure Sensor'])
        


    @app.route("/label-brux", methods=["POST"])
    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def post_label_brux():
        try:
            try:
                label = request.json
                print(label)
            except werkzeug.exceptions.BadRequest:
                return "Please sent a Json package!", 400
            if label["location_begin"] > label["location_end"]:
                return "Start time cannot be greater than end time!", 400
           
            print(tuple(label.values()))
            insert_label(tuple(label.values()))
            return "Successfuly inserted into Database", 200
        except Exception as e:
            return f"{e}", 400

    @app.route("/label-brux/<int:patient_id>", methods=["GET"])
    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def get_label_brux(patient_id):
        return get_patient_data(patient_id)

    @app.route("/hrv-features/<int:patient_id>/<int:week>/<int:night_id>", methods=["GET"])
    def get_hrv_features(patient_id, week, night_id):
        try:
            return get_HRV_features(patient_id, week, night_id, 15)
        except Exception as e:
            return f"{e}"
        
    return app


    
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)