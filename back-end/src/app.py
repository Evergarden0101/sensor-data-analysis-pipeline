from flask import Flask, request
import werkzeug
import os
import sqlite3 as sql
from database import db
from flask_cors import CORS
from SSD import *
from preprocessing import *
from utils import *
import sys
import pandas as pd
from settings import *
from scipy import stats
import os
import re

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

             
    #TODO: possibly change in future and include all the parameters in json payload
    @app.route("/patient-recording/<int:patient_id>/<int:week>/<string:night_id>", methods=['POST'])
    def upload_patient_recording(patient_id, week, night_id):
        try:
            day, hours, minutes, seconds = get_patient_time_values(night_id)
            patient_file = DATA_PATH + f"p{patient_id}_w{week}/{night_id}cFnorm.csv"
            df = pd.read_csv(patient_file)
            # For the moment the data is automatically resampled when uploaded in DB for efficiency reasons
            # TODO: adapt in the future
            csvData = resample_whole_df(df)

            post_patient_recording(DATABASE, patient_id, week, day, hours, minutes, seconds, patient_file, csvData)

            return "Successfuly inserted into Database.", 200
        
        except Exception as e:
            return f"{e}", 400
    

    """
        Payload (not mandatory)
        {
            start_min: int,
            end_min: int
        }

    """
    @app.route("/patient-recording/<int:patient_id>/<string:week>/<string:day>", methods=["GET"])
    def get_patient_recording(patient_id, week, day):
        try:
            try:
                range_min = request.json
            except:
                range_min = None
            response = retrieve_patient_recording(DATABASE, patient_id, week, day, range_min, SAMPLING_RATE=2000)

            return response

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
                insert_label(DATABASE, tuple(label.values()))
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
    @app.route("/ssd/<int:patient_id>/<int:week>/<string:night_id>", methods=["GET", "POST"])
    def sleep_stage_detection(patient_id, week, night_id):
        if request.method == 'GET':
            try:
                print('database variable', file=sys.stderr)

                values = get_ssd_values(DATABASE, patient_id, week, night_id)
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
                post_ssd_updates(DATABASE, updates)

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
    #TODO: endpoint to perform preprocessing
    @app.route("/preprocess/<int:patient_id>/<int:week>/<string:night_id>", methods=["GET"])
    def get_preprocessing(patient_id, week, night_id):
        try:
            #preprocessing_params = request.json

            day, hours, minutes, seconds = get_patient_time_values(night_id)

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

    @app.route("/existing-patients-recordings/", methods=["GET"])
    def get_existing_patients_datasets():
        try:
            existing_patients_recordings = get_existing_patients_data()

            return existing_patients_recordings, 200
        
        except Exception as e:
            print('Exception raised')
            print(e)
            return f"{e}"
    
    @app.route("/settings/", methods=["POST", "GET"])
    def post_settings():
        if request.method == 'POST':
            try: 
                settings = request.json

                print(settings)
                print(tuple(settings.values()))
                    


                with sql.connect(DATABASE) as con:
                    cur = con.cursor()
                    cur.execute("DELETE FROM settings")
                    params = tuple(settings.values())
                    query = "INSERT  INTO settings (study_type, activity, original_sampling, REM_sampling, NREM_sampling, dataset_format, filtered, normalized) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                    cur.execute(query, params)

                return "Inserted settings into DB", 200
            except Exception as e:
                print('Exception raised')
                print(e)
                return f"{e}", 500
            
        if request.method == "GET":
            settings = get_settings(DATABASE)
            return settings
        
    @app.route("/sensors/", methods=["POST"])
    def post_sensors():
        try: 
            sensors = request.json

            with sql.connect(DATABASE) as con:
                cur = con.cursor()
                cur.execute("DELETE FROM sensors")

                for sensor in sensors:
                    params = tuple(sensor.values())
                    query = "INSERT  INTO sensors (type, name) VALUES (?, ?)"
                    cur.execute(query, params)

            return "Inserted sensors into DB", 200
        except Exception as e:
            print('Exception raised')
            print(e)
            return f"{e}", 500

 
    @app.route("/lineplot-data/<int:patient_id>/<int:week>/<string:night_id>", methods=["GET"])
    def get_lineplot_data(patient_id, week, night_id):
        try:
            df = open_brux_csv(patient_id, week, night_id)

            mr = df["MR"].values.tolist()
            ml = df["ML"].values.tolist()
            su = df["SU"].values.tolist()

            rem_ranges =  get_rem_intervals(patient_id, week, night_id, DATABASE)

            sampling_ranges = get_sampling_ranges(mr, ml, su, rem_ranges)

            resampled_ranges = get_resampled_ranges(sampling_ranges)

            return resampled_ranges, 200


        except Exception as e:
            print('Exception raised')
            print(e)
            return f"{e}", 500

    return app



    
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)