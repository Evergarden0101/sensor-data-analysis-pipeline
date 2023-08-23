from flask import Flask, request
import werkzeug
import os
import sqlite3 as sql
from database import db
from flask_cors import CORS
from SSD import *
from preprocessing import *
import sys
import pandas as pd
from settings import *

"""Example of possible structure for posting the label data"""
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    cors = CORS(app)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'brux-db.sqlite'),
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

    DATABASE = app.config['DATABASE']
    
    # Helper functions and variables
    def insert_label(label):
        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute(f"INSERT INTO labels (patient, location_begin, location_end, duration) VALUES {label}")

    def get_patient_data(patient_id):
        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            patient_data = cur.execute(f"SELECT * FROM labels WHERE patient = {patient_id}").fetchall()

        return patient_data
    
    def get_SSD_format(columns, query_results):
        values = []
        for query_result in query_results:
            values.append({
                columns[1]: query_result[1],
                columns[2]: query_result[2],
                columns[3]: query_result[3],
                columns[4]: query_result[4],
                columns[5]: query_result[5],
                columns[6]: query_result[6],
                columns[7]: query_result[7],
                columns[8]:  query_result[8],
                columns[9]:  query_result[9],
                columns[10]:  query_result[10],
                columns[11]:  query_result[11],
                columns[12]:  query_result[12]
            })
        return values
             

    @app.route("/patient-recording/<int:patient_id>/<int:week>/<string:day>/<string:hours>/<string:minutes>/<string:seconds>", methods=['POST'])
    def upload_patient_recording(patient_id, week, day, hours, minutes, seconds):
        try:
            patient_file = DATA_PATH + f"p{patient_id}_w{week}/{day}{hours}{minutes}{seconds}cFnorm.csv"
            csvData = pd.read_csv(patient_file)
            #csvData = resample_whole_df(csvData)

            with sql.connect(DATABASE) as con:
                print("DATABASE CONNECTED")
                cur = con.cursor()

                for i,row in csvData.iterrows():
            
                    params = (patient_id, week, day, hours, minutes, seconds, patient_file[-10], row['MR'],row['ML'],row['SU'],row['Microphone'],row['Eye'], row['ECG'], row['Pressure Sensor'])
                    query = "INSERT INTO patients_recordings (patient_id, week, day, hours, minutes, seconds, recorder, MR, ML, SU, Microphone, Eye, ECG, Pressure) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                
                    cur.execute(query, params)
                    print(f"{i} out of {csvData.index[-1]}")

            return "Successfuly inserted into Database.", 200
        
        except Exception as e:
            return f"{e}", 400
    


    @app.route("/patient-recording/<int:patient_id>/<string:week>/<string:day>", methods=["GET"])
    def get_patient_recording(patient_id, week, day):
        try:
            with sql.connect(DATABASE) as con:
                print('connected to db', file=sys.stderr)
                cur = con.cursor()

                params = (patient_id, week, day)
                patient_recording = f"SELECT * FROM patient_recordings WHERE (patient_id=? AND week=? AND day=?)"
                print('patient_exist query', file=sys.stderr)

                patient_recording_query = cur.execute(patient_recording, params).fetchall()

                if patient_recording_query:
                    print('EXIST', file=sys.stderr)

                    df = pd.DataFrame(patient_recording_query)
                    df.columns = patient_recording_query.keys()

                    print(df.info)

                    return df, 200
                
                else:
                    print('DOES NOT EXIST', file=sys.stderr)
                    return f"There is no data for patient with id {patient_id} on day {day} of week {week}", 404

        except Exception as e:
            return f"{e}", 400


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
            print('hey', file=sys.stderr)
            day = str(night_id)[:2]
            hours = str(night_id)[2:4]
            minutes = str(night_id)[4:6]
            seconds =str(night_id)[6]

            print('database variable', file=sys.stderr)
            with sql.connect(DATABASE) as con:
                print('connected to db', file=sys.stderr)
                cur = con.cursor()

                print('cur variable defined', file=sys.stderr)

                params = (patient_id, day, hours, minutes, seconds)
                patient_exist = f"SELECT * FROM sleep_stage_detection WHERE (patient_id=? AND day=? AND hours=? AND minutes=? AND seconds=?)"
                print('patient_exist query', file=sys.stderr)

                if cur.execute(patient_exist, params).fetchall():
                    print('EXIST', file=sys.stderr)
                    params = (patient_id, day, hours, minutes, seconds)
                    query = "SELECT * FROM sleep_stage_detection WHERE (patient_id=? AND day=? AND hours=? AND minutes=? AND seconds=?)"
                    result = cur.execute(query, params)
                    columns = [description[0] for description in result.description]
                    print(f"Columns: {columns}")
                    values = get_SSD_format(columns, result.fetchall())


                    print(f"Values from db: {values}")
                
                else:
                    print('DOES NOT EXIST', file=sys.stderr)
                    values = get_HRV_features(patient_id, week, night_id, 720)

                    for value in values:
                        params = (patient_id, day, hours, minutes, seconds, value['start_id'], value['end_id'], value['LF_HF'], value['SD'], value['stage'], value['y'], value['x'])
                        query = "INSERT INTO sleep_stage_detection (patient_id, day, hours, minutes, seconds, start_id, end_id, LF_HF, SD, stage, y, x) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                        cur.execute(query, params)

                return values
        except Exception as e:
            print('Exception raised', file=sys.stderr)
            print(e)
            return f"{e}"
        
    return app


    
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)