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
from scipy import stats

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

    def get_json_format_from_query(columns, query_results, start_id, end_id):
        values = []
        for query_result in query_results:
            dictionary = {}
            for i in range(start_id, end_id+1):
                dictionary[columns[i]] = query_result[i]

            values.append(dictionary)

        return values
             
    #TODO: possibly change in future and include all the parameters in json payload
    @app.route("/patient-recording/<int:patient_id>/<int:week>/<string:day>/<string:hours>/<string:minutes>/<string:seconds>", methods=['POST'])
    def upload_patient_recording(patient_id, week, day, hours, minutes, seconds):
        try:
            patient_file = DATA_PATH + f"p{patient_id}_w{week}/{day}{hours}{minutes}{seconds}cFnorm.csv"
            df = pd.read_csv(patient_file)
            # For the moment the data is automatically resampled when uploaded in DB for efficiency reasons
            # TODO: adapt in the future
            csvData = resample_whole_df(df)

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

    """
    request.json format:
        {
            "patient": int,
            "location_begin": int,
            "location_end": int,
            "duration": int
        }
    """
    @app.route("/label-brux", methods=["POST"])
    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def post_label_brux():
        try:
            try:
                labels = request.json
                print(labels)
            except werkzeug.exceptions.BadRequest:
                return "Please sent a Json package!", 400

            for label in labels:
                if label["location_begin"] > label["location_end"]:
                    return "Start time cannot be greater than end time!", 400
                insert_label(tuple(label.values()))
            return "Successfuly inserted into Database", 200
        except Exception as e:
            return f"{e}", 400

    #TODO: possibly get labels from specific patient on a specific week?
    @app.route("/label-brux/", methods=["GET"], defaults={'patient_id': None})
    @app.route("/label-brux/<int:patient_id>", methods=["GET"])
    def get_label_brux(patient_id):
        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            if patient_id != None:
                patient_data = cur.execute(f"SELECT * FROM labels WHERE patient = {patient_id}").fetchall()

                if not patient_data:
                    return f"No labels found for patient {patient_id}.", 404
            else:
                patient_data = cur.execute(f"SELECT * FROM labels").fetchall()

        return patient_data
    
    #TODO: adapt this to take the dataset directly from the DB
    @app.route("/ssd/<int:patient_id>/<int:week>/<int:night_id>", methods=["GET", "POST"])
    def sleep_stage_detection(patient_id, week, night_id):
        if request.method == 'GET':
            try:
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
                        values = get_json_format_from_query(columns=columns, query_results=result.fetchall(), start_id=1, end_id=12)
                        #values = get_SSD_format(columns, result.fetchall())


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
            
        if request.method == 'POST':
            #code for posting here
            """
                payload:
                    {
                        'x': int,
                        'y': int,
                        'stage': string

                    }
            """
            try:
                updates = request.json

                for update in updates:
                    with sql.connect(DATABASE) as con:
                        print('connected to db', file=sys.stderr)
                        cur = con.cursor()
                        params = (update["x"], update["y"])

                        if update["stage"] == 'rem':
                            query = "UPDATE sleep_stage_detection SET stage = 'nrem' WHERE x=? AND y=?"
                            cur.execute(query, params)
                        elif update["stage"] == 'nrem':
                            query = "UPDATE sleep_stage_detection SET stage = 'rem' WHERE x=? AND y=?"
                            cur.execute(query, params)

                return "sleep_stage_detection table updated successfully", 200

                    

            except Exception as e:
                print('Exception raised')
                print(e)
                return f"{e}"
                        

        
    """
        To include in preprocessing:
        - Normalization
        - Filtering
        - Resampling
    """
    @app.route("/preprocess/<int:patient_id>/<int:week>/<string:night_id>", methods=["GET"])
    def get_preprocessing(patient_id, week, night_id):
        try:
            #preprocessing_params = request.json

            day = night_id[:2]
            hours = night_id[2:4]
            minutes = night_id[4:6]
            seconds = night_id[6]

            print("night id params okay")

            params = (patient_id, week, day, hours, minutes, seconds)
            query = "SELECT * from patients_recordings WHERE (patient_id=? AND week=? AND day=? AND hours=? AND minutes=? AND seconds=?)"

            with sql.connect(DATABASE) as con:
                print("DB connected")
                cur = con.cursor()
                patient_data = cur.execute(query, params)
                columns = [description[0] for description in patient_data.description]
                print(columns)
                #df = get_patients_recordings_df(columns, patient_data.fetchall())
                patient_data_json = get_json_format_from_query(columns=columns, query_results=patient_data.fetchall(), start_id=1, end_id=14)

            return patient_data_json, 200
        
        except Exception as e:
            print('Exception raised')
            print(e)
            return f"{e}"

        
    return app


    
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)