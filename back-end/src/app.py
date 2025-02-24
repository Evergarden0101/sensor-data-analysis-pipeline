from flask import Flask, request, make_response, jsonify
import werkzeug
from werkzeug.middleware.proxy_fix import ProxyFix
import os, json
import sqlite3 as sql
from database import db
from flask_cors import CORS
from preprocessing import *
from utils import *
import sys
import pandas as pd
# from settings import *
import os, math
from datetime import datetime
import json
import xgboost as xgb


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    cors = CORS(app)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'brux-db.sqlite'),
        SESSION_COOKIE_SAMESITE = None
    )
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
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
    @app.route("/patient-recording/<int:patient_id>/<string:week>/<string:night_id>/<string:recorder>", methods=['POST'])
    def upload_patient_recording(patient_id, week, night_id, recorder):
        try:
            patient_file = get_data_path(DATABASE) + f"p{patient_id}_wk{week}/{night_id}{recorder}Fnorm.csv"
            df = pd.read_csv(patient_file)
            # For the moment the data is automatically resampled when uploaded in DB for efficiency reasons
            # TODO: adapt in the future
            csvData = resample_whole_df(df)

            post_patient_recording(DATABASE, patient_id, week, night_id, patient_file, csvData)

            return "Successfuly inserted into Database.", 200
        
        except Exception as e:
            return f"{e}", 500
    

    """
        Payload (not mandatory)
        {
            start_min: int,
            end_min: int
        }

    """
    @app.route("/patient-recording/<int:patient_id>/<string:week>/<string:night_id>", methods=["GET"])
    def get_patient_recording(patient_id, week, night_id):
        try:
            try:
                range_min = request.json
            except:
                range_min = None
            response = retrieve_patient_recording(DATABASE, patient_id, week, night_id, range_min, SAMPLING_RATE=2000)

            return response

        except Exception as e:
            return f"{e}", 500


    """
    request.json format:
        {
            "patient": int,
            "location_begin": int,
            "location_end": int,
            "duration": int
        }
    """
    @app.route("/label-brux/", methods=["POST"])
    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def post_label_brux():
        try:
            try:
                labels = request.json
                print(labels)
            except werkzeug.exceptions.BadRequest:
                return "Please sent a Json package!", 500
            
            # remove_pred_label(DATABASE, labels)
            insert_label(DATABASE, labels)
            
            img_local_path =  get_data_path(DATABASE)+'p'+str(labels[0]['patient_id'])+'_wk'+str(labels[0]['week'])+f'/'+str(labels[0]['night_id'])+f'.png'
            print('img_local_path: ',img_local_path)
            if os.path.exists(img_local_path):
                # Delete the file
                os.remove(img_local_path)
                print(f"Night image deleted.")
            
            valid_set = get_data_path(DATABASE)+'p'+str(labels[0]['patient_id'])+'_wk'+str(labels[0]['week'])+f'/'+str(labels[0]['night_id']) +str(labels[0]['recorder'])+f'Fnorm.csv'
            print('valid_set: ',str(valid_set))
            with sql.connect(DATABASE) as con:
                cur = con.cursor()
                cur.execute(f"SELECT * FROM models WHERE patient_id={labels[0]['patient_id']}")
                model = cur.fetchone()
                print(model)
                if(model[4] == None):
                    print("update validation set")
                    cur.execute(f"UPDATE models SET validation_file_path='{valid_set}' WHERE patient_id={labels[0]['patient_id']}")
                
                cur.execute(f"SELECT * FROM models WHERE patient_id= -1")
                model = cur.fetchone()
                if(model[4] == None):
                    print("update validation set")
                    cur.execute(f"UPDATE models SET validation_file_path='{valid_set}' WHERE patient_id= -1")
            
            return "Successfuly inserted into Database", 200
        except Exception as e:
            print('Exception raised in confirming labels', e)
            return f"{e}", 500


    @app.route("/label-brux/", methods=["GET"], defaults={'patient_id': None})
    @app.route("/label-brux/<int:patient_id>/<string:week>/<string:night_id>/<string:recorder>", methods=["GET"])
    def get_label_brux(patient_id, week, night_id, recorder):
        try:
            print('get_label_brux')
            params = (patient_id, week, night_id, recorder)
            query = "SELECT * from confirmed_labels WHERE (patient_id=? AND week=? AND night_id=? AND recorder=?)"
            with sql.connect(DATABASE) as con:
                print("DB connected")
                cur = con.cursor()
                comfirmed_labels = cur.execute(query, params)
                if comfirmed_labels.fetchall() != None and len(comfirmed_labels.fetchall()) != 0:
                    columns = [description[0] for description in comfirmed_labels.description]
                    print(columns)
                    #df = get_patients_recordings_df(columns, patient_data.fetchall())
                    predicted_labels_json = get_json_format_from_query(columns=columns, query_results=comfirmed_labels.fetchall(), start_id=1, end_id=9)
                    print(comfirmed_labels)
                    return comfirmed_labels, 200
                cur.close()
            
            run_prediction(DATABASE, patient_id, week, night_id, recorder)
            params = (patient_id, week, night_id, recorder)
            query = "SELECT * from predicted_labels WHERE (patient_id=? AND week=? AND night_id=? AND recorder=?)"

            with sql.connect(DATABASE) as con:
                print("DB connected")
                cur = con.cursor()
                predicted_labels = cur.execute(query, params)
                columns = [description[0] for description in predicted_labels.description]
                print(columns)
                #df = get_patients_recordings_df(columns, patient_data.fetchall())
                predicted_labels_json = get_json_format_from_query(columns=columns, query_results=predicted_labels.fetchall(), start_id=1, end_id=9)
                print(predicted_labels_json)
            return predicted_labels_json, 200


        except Exception as e:
            print('Exception raised in getting predicted labels')
            print(e)
            return f"{e}", 500
    

    @app.route("/ssd/<int:patient_id>/<string:week>/<string:night_id>/<string:recorder>/", methods=["GET"])
    def sleep_stage_detection(patient_id, week, night_id, recorder):
        try:
            print('database variable', file=sys.stderr)

            values = get_ssd_values(DATABASE, patient_id, week, night_id, recorder)
            return values, 200
        
        except Exception as e:
            print('Exception raised', file=sys.stderr)
            print(e)
            return f"{e}", 500


    @app.route("/selected-sleep-phases/<int:patient_id>/<string:week>/<string:night_id>/", methods=["GET", "POST"])
    def selected_phases(patient_id, week, night_id):
        if request.method == 'GET':
            try:
                selected = get_selected_phases(DATABASE, patient_id, week, night_id)

                if len(selected) > 0:
                    return selected, 200
                
                else:
                    standard_selected = get_standard_selected_phases(DATABASE, patient_id, week, night_id)
                    updates = []
                    for s in standard_selected:
                        print(s)
                        updates.append({'x': s[0], 'y': s[1]})

                    if len(updates) == 0:
                        standard_selected = get_rem_intervals(patient_id, week, night_id, DATABASE)
                        for s in standard_selected:
                            updates.append({'x': s[0], 'y': s[1]})
                    
                    post_selected_updates(DATABASE, patient_id, week, night_id, updates)

                    return standard_selected, 200
            
            except Exception as e:
                print('Exception raised')
                print(e)
                return f"{e}", 500

        if request.method == 'POST':
            """
                payload:
                    {
                        'x': int,
                        'y': int,

                    }
            """
            try:
                updates = request.json
                print(night_id)
                post_selected_updates(DATABASE, patient_id, week, night_id, updates)

                with sql.connect(DATABASE) as con:
                    print("DB connected")
                    cur = con.cursor()
                    params = (patient_id, week, night_id)
                    query = "DELETE FROM predicted_labels WHERE patient_id=? AND week=? AND night_id=?"
                    cur.execute(query, params)
                    # cur.execute(f"DELETE FROM predicted_labels WHERE patient_id={patient_id} AND week={week} AND night_id={night_id}")
                    print("predicted_labels deleted")
                    
                    query = "DELETE FROM week_summary WHERE patient_id=? AND week=? AND night_id=?"
                    cur.execute(query, params)
                    # cur.execute(f"DELETE FROM week_summary WHERE patient_id={patient_id} AND week={week} AND night_id={night_id}")
                    print("week_summary deleted")
                    cur.close()
                    
                img_local_path =  get_data_path(DATABASE)+'p'+str(patient_id)+'_wk'+str(week)+f'/'+str(night_id)+f'.png'
                if os.path.exists(img_local_path):
                    # Delete the file
                    os.remove(img_local_path)
                    print(f"Night image deleted.")
                img_local_path = get_data_path(DATABASE)+'p'+str(patient_id)+'_wk'+str(week)+f'/summary.png'
                if os.path.exists(img_local_path):
                    # Delete the file
                    os.remove(img_local_path)
                    print(f"Week image deleted.")
                return "sleep_stage_detection table updated successfully", 200

                    
            except Exception as e:
                print('Exception raised')
                print(e)
                return f"{e}", 500

        
    """
        To include in preprocessing:
        - Normalization
        - Filtering
        - Resampling
    """
    #TODO: endpoint to perform preprocessing
    @app.route("/preprocess/<int:patient_id>/<string:week>/<string:night_id>", methods=["GET"])
    def get_preprocessing(patient_id, week, night_id):
        try:
            #preprocessing_params = request.json

            print("night id params okay")

            params = (patient_id, week, night_id)
            query = "SELECT * from patients_recordings WHERE (patient_id=? AND week=? AND night_id=?)"

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


    @app.route("/monitoring-allowed/<int:patient_id>/<string:week>/", methods=["GET"])
    def is_monitoring_allowed(patient_id, week):
        try:
            with sql.connect(DATABASE) as con:
                print("DB connected")
                cur = con.cursor()
                params = (patient_id, week)
                query = "SELECT * FROM week_summary WHERE (patient_id=? AND week=?)"
                result = cur.execute(query, params).fetchall()

                return {'is_allowed': 1} if len(result)>0 else {'is_allowed': 0}, 200

        except Exception as e:
            print('Exception raised')
            print(e)
            return f"{e}", 500
    

    @app.route("/settings-exist/", methods=["GET"])
    def do_settings_exist():
        settings_exist = 0
        try:
            with sql.connect(DATABASE) as con:
                cur = con.cursor()
                settings = cur.execute("SELECT COUNT(*) FROM settings").fetchone()[0]
                sensors = cur.execute("SELECT COUNT(*) FROM sensors").fetchone()[0]

                if (settings == 1) and (sensors > 0):
                    settings_exist = 1
                return {'settings_exist': settings_exist}, 200
        except Exception as e:
            print('Exception raised')
            print(e)
            return f"{e}", 500


    @app.route("/existing-patients-recordings/", methods=["GET"])
    def get_existing_patients_datasets():
        try:
            existing_patients_recordings = get_existing_patients_data(DATABASE)

            return existing_patients_recordings, 200
        
        except Exception as e:
            print('Exception raised')
            print(e)
            return f"{e}", 500
    

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
                    query = "INSERT  INTO settings (study_type, activity, activity_duration, original_sampling, selected_sampling, non_selected_sampling, dataset_format, filtered, normalized, data_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    cur.execute(query, params)

                return "Inserted settings into DB", 200
            except Exception as e:
                print('Exception raised')
                print(e)
                return f"{e}", 500
            
        if request.method == "GET":
            try: 
                settings = get_settings(DATABASE)
                return settings, 200
            
            except Exception as e:
                print('Exception raised')
                print(e)
                return f"{e}", 500


    @app.route("/sensors/", methods=["POST", "GET"])
    def post_sensors():
        if request.method == "POST":
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
            
        if request.method == "GET":
            try:
                return get_sensors(DATABASE), 200
            
            except Exception as e:
                print('Exception raised')
                print(e)
                return f"{e}", 500

 
    @app.route("/sleep-cycle/<int:patient_id>/<string:week>/<string:night_id>/<int:sleep_cycle>/<string:recorder>", methods=["GET"])
    def get_sleep_cycle_data(patient_id, week, night_id, sleep_cycle, recorder):

        # Amount of data points in a sleep cycle
        chunk_size = 2000*60*90

        df =  pd.read_csv(get_data_path(DATABASE) + f"p{patient_id}_wk{week}/{night_id}{recorder}Fnorm.csv", usecols=['MR', 'ML'], chunksize=chunk_size)

        chunks = []
        max_chunk = 0
        for chunk in df:
            max_chunk+=1
            chunks.append(chunk)

        if sleep_cycle > max_chunk:
            return f"Sleep cycle nr {sleep_cycle} does not exist for patient {patient_id} on week {week} and night id {night_id}", 500
        
        else:
            df = chunks[sleep_cycle-1]

            start_id = df.index.start
            end_id = df.index.stop

            mr = df["MR"]
            ml = df["ML"]

            ranges = get_sleep_cycle_selected_intervals(patient_id, week, night_id, DATABASE, start_id, end_id)

            sampling_ranges = get_sleep_cycle_sampling_ranges(DATABASE, mr, ml, ranges, start_id, end_id)
            resampled_ranges = get_resampled_ranges(DATABASE, sampling_ranges)


            return resampled_ranges, 200


    @app.route("/lineplot-data/<int:patient_id>/<string:week>/<string:night_id>/<string:recorder>", methods=["GET"])
    def get_lineplot_data(patient_id, week, night_id, recorder):
        try:
            df = open_brux_csv(DATABASE, patient_id, week, night_id, recorder, columns=['MR', 'ML'])

            mr = df["MR"].values.tolist()
            ml = df["ML"].values.tolist()

            ranges =  get_selected_intervals(patient_id, week, night_id, DATABASE)

            sampling_ranges = get_sampling_ranges(DATABASE, mr, ml, ranges)

            resampled_ranges = get_resampled_ranges(DATABASE, sampling_ranges)

            return resampled_ranges, 200

        except Exception as e:
            print('Exception raised')
            print(e)
            return f"{e}", 500


    """
    label: 
        {
            "location_begin": int
            "location_end": int
        }
    """
    @app.route('/event-interval/<int:patient_id>/<string:week>/<string:night_id>/<string:recorder>/<int:location_begin>/<int:location_end>', methods=["GET"])
    def get_event_interval(patient_id, week, night_id, recorder, location_begin, location_end):
        try: 
            print("get event interval")
            # label = request.json
            # print(label)
            original_sampling = get_original_sampling(DATABASE)
            activity_duration_data_points = get_activity_duration(DATABASE) * original_sampling

            #1h data
            chunk_size = original_sampling*60*60

            # location_begin = math.floor(location_begin * get_original_sampling(DATABASE))
            # location_end = math.ceil(location_end * get_original_sampling(DATABASE))

            print(f"duration in index: {location_end - location_begin}")
            print(f"location_begin: {location_begin}, location_end: {location_end}")

            with sql.connect(DATABASE) as con:
                cur = con.cursor()

                params = (patient_id, week, night_id, recorder, location_begin, location_end)
                query = "SELECT start_id, end_id FROM sleep_stage_detection WHERE patient_id=? AND week=? AND night_id=? AND recorder=? AND ? >= start_id AND ? <= end_id"
                result = cur.execute(query, params).fetchall()

                print(f"DB 5 min result: {result}")

                # If the event is in between two 5 minute intervals we might wanto to return more than 5 minute of data
                if result==[]:
                    print("Corner case")
                    start_id = math.floor(location_begin - activity_duration_data_points)
                    end_id = math.ceil(location_end + activity_duration_data_points)

                # The event is in a 5 minute interval
                else:
                    print("Normal case")
                    start_id = result[0][0]
                    end_id = result[0][1]

                    print(f"Selected 5 min -  start_id: {start_id}, end_id: {end_id}")
                
                # Open the df with a chunk size of 1h because the interval might be > 5 min
                df =  pd.read_csv(get_data_path(DATABASE) + f"p{patient_id}_wk{week}/{night_id}{recorder}Fnorm.csv", usecols=['MR', 'ML'], chunksize=chunk_size)

                for chunk in df:
                    print(f"chunk start_id: {chunk.index.start}, start_id: {start_id}")
                    if (chunk.index.start <= start_id) and (chunk.index.stop >= end_id):
                        # Find desired chunk
                        desired_chunk = chunk
                        break
                print(f"desired chunk: {desired_chunk}")

                result = get_event_data(DATABASE, desired_chunk, start_id, end_id, location_begin, location_end)

                return result, 200
            
        except Exception as e:
            print(e)
            return f"{e}", 500


    @app.route('/weekly-sum-img', methods=["GET"])
    def get_weekly_sum_img():
        try:
            # img_path = '/home/hogan/Googlelogo.png'
            # img_stream = return_img_stream(img_path)
            # return render_template('BruxismPage.vue',
            #                     img_stream=img_stream)
            patient_id = request.args.get('p')
            week = request.args.get('w')
            img_local_path =  get_data_path(DATABASE) +"p"+str(patient_id)+"_wk"+str(week)+ f"/summary.png"
            print('img_local_path: ',img_local_path)
            generate_weekly_sum_img(DATABASE, img_local_path, patient_id, week)
            img_f = open(img_local_path, 'rb')
            print(img_f)
            res = make_response(img_f.read())   # 用flask提供的make_response 方法来自定义自己的response对象
            res.headers['Content-Type'] = 'image/png'   # 设置response对象的请求头属性'Content-Type'为图片格式
            img_f.close()
            return res, 200
        except Exception as e:
            print('Exception raised in getting weekly summary image')
            img_local_path =  get_data_path(DATABASE) +"p"+str(patient_id)+"_wk"+str(week)+ f"/summary.png"
            
            try:
                img_f = open(img_local_path, 'rb')
                res = make_response(img_f.read())   # 用flask提供的make_response 方法来自定义自己的response对象
                res.headers['Content-Type'] = 'image/png'   # 设置response对象的请求头属性'Content-Type'为图片格式
                img_f.close()
                return res, 200
            except:
                print(e)
                return f"{e}", 500


    @app.route('/night-pred-img', methods=["GET"])
    def get_night_pred_img():
        try:
            # img_path = '/home/hogan/Googlelogo.png'
            # img_stream = return_img_stream(img_path)
            # return render_template('BruxismPage.vue',
            #                     img_stream=img_stream)
            patient_id = request.args.get('p')
            week = request.args.get('w')
            night = request.args.get('n')
            recorder = request.args.get('r')

            print(f"recorder: {recorder}")
            # week_path = get_data_path(DATABASE)+'p'+str(patient_id)+'_wk'+str(week)+f'/'
            # print('night_path: ',week_path)
            # img_local_path =  week_path+str(night)+f'.png'
            img_local_path =  get_data_path(DATABASE)+'p'+str(patient_id)+'_wk'+str(week)+f'/'+str(night)+f'.png'
            print('img_local_path: ',img_local_path)
            
            if os.path.exists(img_local_path) and os.path.getsize(img_local_path) < 50:
                print(f"File size is {file_size} bytes. Deleting file.")
                os.remove(img_local_path)
            
            if not os.path.exists(img_local_path):
                generate_night_pred_img(DATABASE, patient_id, week, night, recorder)
                
            img_f = open(img_local_path, 'rb')
            print(img_f)
            res = make_response(img_f.read())
            res.headers['Content-Type'] = 'image/png'
            img_f.close()
            
            # Check if the file size is below the threshold
            file_size = os.path.getsize(img_local_path)
            if file_size < 50:
                # Delete the file
                print(f"File size is {file_size} bytes. Deleting file.")
                os.remove(img_local_path)
            return res, 200
        except Exception as e:
            print('Exception raised in getting night prediction image')
            print(e)
            
            img_local_path =  get_data_path(DATABASE)+'p'+str(patient_id)+'_wk'+str(week)+f'/'+str(night)+f'.png'
            if os.path.exists(img_local_path):
                os.remove(img_local_path)
            return f"{e}", 500


    # TODO: rerun model and general model
    @app.route('/rerun-model/<int:patient_id>/<string:week>/<string:night_id>/<string:recorder>', methods=["GET"])
    def rerun_model(patient_id, week, night_id, recorder):
        try:
            # params = (patient_id, week, night_id, recorder)
            # query = "SELECT * from bite_records WHERE (patient_id=? AND week=? AND night_id=? AND labelId=?)"
            # patient model
            with sql.connect(DATABASE) as con:
                print("DB connected")
                cur = con.cursor()
                cur.execute(f"SELECT * FROM models WHERE patient_id={patient_id}")
                model = cur.fetchall()
                cur.close()
            
            # TODO: update accuracy
            try:
                patient_accuracy = run_confirmation(DATABASE, str(model[0][-1]), patient_id, week, night_id, recorder, False)
                # xgbc = xgb.XGBClassifier()
                # xgbc.load_model(str(model[0][-1]))
                # patient_accuracy = calc_model_accuracy(DATABASE, xgbc, patient_id, week, night_id, recorder, patient_id)
            except Exception as e:
                print(e)
                patient_accuracy = {'accuracy': None, 'precision': None}
            
            
            # TODO: study model
            with sql.connect(DATABASE) as con:
                print("DB connected")
                cur = con.cursor()
                cur.execute(f"SELECT * FROM models WHERE patient_id=-1")
                model = cur.fetchall()
                cur.close()
            try:
                study_accuracy = run_confirmation(DATABASE, str(model[0][-1]), patient_id, week, night_id, recorder, True)
                # xgbc = xgb.XGBClassifier()
                # xgbc.load_model(str(model[0][-1]))
                # study_accuracy = calc_model_accuracy(DATABASE, xgbc, patient_id, week, night_id, recorder, -1)
            except Exception as es:
                study_accuracy = {'accuracy': None, 'precision': None}
            if(patient_accuracy['precision'] == None and study_accuracy['precision'] == None):
                return f"{es}", 500
            
            return jsonify(patient_accuracy=patient_accuracy, study_accuracy=study_accuracy), 200
        except Exception as e:
            print('Exception raised in rerunning model')
            print(e)
            return f"{e}", 500
    
    
    @app.route('/model-accuracy/<int:patient_id>', methods=["GET"])
    def get_model_accuracy(patient_id):
        try:
            with sql.connect(DATABASE) as con:
                print("DB connected")
                cur = con.cursor()
                cur.execute(f"SELECT accuracy, precision FROM models WHERE patient_id={patient_id}")
                patient_accuracy = cur.fetchall()
                if(len(patient_accuracy)==0):
                    patient_accuracy = None
                else:
                    patient_accuracy = patient_accuracy[0]
                print('patient_accuracy: ',patient_accuracy)
                cur.execute(f"SELECT accuracy, precision FROM models WHERE patient_id=-1")
                study_accuracy = cur.fetchall()
                if(len(study_accuracy)==0):
                    study_accuracy = None
                else:
                    study_accuracy = study_accuracy[0]
                print('study_accuracy: ',study_accuracy)
                cur.close()
            return jsonify(patient_accuracy=patient_accuracy, study_accuracy=study_accuracy), 200
        except Exception as e:
            print('Exception raised in getting model accuracy')
            print(e)
            return f"{e}", 500
    

    # TODO: confusion matrix
    @app.route('/confusion-matrix/<int:patient_id>', methods=["GET"])
    def get_confusion_matrix(patient_id):
        try:
            with sql.connect(DATABASE) as con:
                print("DB connected")
                cur = con.cursor()
                patient_accuracy = cur.execute(f"SELECT id, TN, FP, FN, TP FROM accuracy_log WHERE patient_id={patient_id}")
                columns = [description[0] for description in patient_accuracy.description]
                patient_accuracy_json = get_json_format_from_query(columns=columns, query_results=patient_accuracy.fetchall(), start_id=0, end_id=4)
                if(len(patient_accuracy_json)==0):
                    patient_accuracy_json = None
                
                cur.execute(f"SELECT id, TN, FP, FN, TP FROM accuracy_log WHERE patient_id=-1")
                study_accuracy = cur.execute(f"SELECT id, TN, FP, FN, TP FROM accuracy_log WHERE patient_id=-1")
                columns = [description[0] for description in study_accuracy.description]
                study_accuracy_json = get_json_format_from_query(columns=columns, query_results=study_accuracy.fetchall(), start_id=0, end_id=4)
                if(len(study_accuracy_json)==0):
                    study_accuracy_json = None
                cur.close()
            # print('patient_accuracy: ',patient_accuracy_json)
            # print('study_accuracy: ',study_accuracy_json)
            return jsonify(patient_accuracy=patient_accuracy_json, study_accuracy=study_accuracy_json), 200
        except Exception as e:
            print('Exception raised in getting confusion matrix')
            print(e)
            return f"{e}", 500


    @app.route('/weekly-summary/<int:patient_id>/<string:week>/', methods=["GET"])
    def get_weekly_summary(patient_id, week):
        try:
            with sql.connect(DATABASE) as con:
                cur = con.cursor()

                query = """SELECT id, patient_id, week, night_id, cycle,
                           max_cycle, count, type, day_no
                           FROM week_summary
                           WHERE patient_id = ? AND week = ?;"""


                cur.execute(query, (patient_id, week))

                rows = cur.fetchall()

                week_summaries = [
                    {
                        'id': row[0],
                        'patient_id': row[1],
                        'week': row[2],
                        'night_id': row[3],
                        'cycle': row[4],
                        'max_cycle': row[5],
                        'count': row[6],
                        'type': row[7],
                        'day_no': row[8]
                    } for row in rows
                ]

                return jsonify(week_summaries), 200

        except Exception as e:
            print('Exception raised in getting week summary:', e)
            return jsonify({'error': str(e)}), 500


    @app.route('/event-trend-patients-ids/', methods=["GET"])
    def get_event_trend_patient_ids():
        try:
            with sql.connect(DATABASE) as con:
                print("DB connected")
                cur = con.cursor()
                result = cur.execute("SELECT DISTINCT patient_id FROM week_summary").fetchall()
                return [str(r[0]) for r in result], 200

        except Exception as e:
            print('Exception raised in getting event trend')
            print(e)
            return f"{e}", 500


    @app.route('/event-trend', methods=["GET"])
    def get_event_trend():
        try:
            patient_id = json.loads(request.args.get('patient_id'))
            # patient_id = request.json["patient_id"]
            # print(f"patient_id: {patient_id}")
            patient_id = tuple(patient_id)
            print("tuple patient id: ",patient_id)
           
            with sql.connect(DATABASE) as con:
                print("DB connected")
                cur = con.cursor()
                if(len(patient_id)>1):
                    cur.execute(f"SELECT patient_id, week, night_id, day_no, SUM(count) AS count, AVG(type) AS type FROM week_summary WHERE patient_id IN {patient_id} GROUP BY day_no, patient_id ORDER BY patient_id, day_no")
                elif(len(patient_id)==1):
                    cur.execute(f"SELECT patient_id, week, night_id, day_no, SUM(count) AS count, AVG(type) AS type FROM week_summary WHERE patient_id={patient_id[0]} GROUP BY day_no, patient_id ORDER BY patient_id, day_no")
                data = cur.fetchall()
                # print(data)
                columns = ['patient_id', 'week', 'night', 'day', 'count', 'type']
                df = pd.DataFrame(data, columns=columns)
                # print(df)
                df['type'] = df['type'].ge(df['count']/2).astype(int)
                df['night'] = df['night'].astype(int)
                print('df: ',df)
                
                if(len(patient_id)>1):
                    cur.execute(f"SELECT MIN(day_no) AS min_day, MAX(day_no) AS max_day FROM week_summary WHERE patient_id IN {patient_id}")
                elif(len(patient_id)==1):
                    cur.execute(f"SELECT MIN(day_no) AS min_day, MAX(day_no) AS max_day FROM week_summary WHERE patient_id={patient_id[0]}")
                day_info = cur.fetchone()
                print('day_info: ',day_info) 
                if(day_info == None or day_info[0]==None or day_info[1]==None):
                    return_list = [{str(i):None} for i in patient_id]
                    return json.dumps(return_list), 200
                # day_list = [0,day_info[1]]
                if day_info[0] == day_info[1]:
                    day_list = [day_info[0]]
                else:
                    day_list = [day_info[0],day_info[1]]
                day_list = pd.DataFrame(day_list,columns=['day'])
                day_list['date'] = pd.to_datetime(day_list['day'], unit='D', origin='2023-01-01')
                day_list = day_list.set_index('date').resample('D').asfreq()
                day_list['day'] = day_list['day'].interpolate(method='linear', limit_direction='both').astype(int)
                print(day_list.index)
                day_lists = pd.DataFrame(day_list['day'],columns=['day'])
                type_lists = pd.DataFrame(day_list['day'],columns=['day'])
                result_lists = pd.DataFrame(day_list['day'],columns=['day'])
                print(day_lists)
                patient_no = len(patient_id)
                for i in range(patient_no):
                    print(i)
                    # cur.execute(f"SELECT MIN(day_no) AS min_day, MAX(day_no) AS max_day FROM week_summary WHERE patient_id={i}")
                    # day_info = cur.fetchone()
                    # print(day_info)
                    df_patient = df[df['patient_id']==patient_id[i]]
                    print('df_patient: ',df_patient)
                    if(df_patient.empty or df_patient.shape[0]==0):
                        print('empty')
                        day_lists[i] = None
                        has_value = False
                    else:
                        with sql.connect(DATABASE) as con:
                            cur = con.cursor()
                            cur.execute(f"SELECT MIN(day_no) AS min_day FROM week_summary WHERE patient_id={patient_id[i]}")
                            day_range = cur.fetchone()
                            first_day = day_range[0]
                            cur.close()
                        df_patient['date'] = day_list.index[df_patient['day']-day_info[0]]
                        daily_df = df_patient.set_index('date').resample('D').asfreq()
                        # print(daily_df)
                        # Interpolate the 'count' column
                        type_lists[i] = daily_df['type']
                        type_lists[i] = type_lists[i].fillna(-1)
                        print('typelists: ',type_lists[i])
                        
                        # daily_df = daily_df.iloc[day_info[0]:day_info[1]+1]
                        cnt = daily_df
                        # print(cnt)
                        # try:
                        #     cnt['count'] = cnt['count'].interpolate(method='spline', order=1).astype(int)
                        # except:
                        cnt['count'] = cnt['count'].interpolate(method='linear', limit_direction='both').astype(int)
                        day_lists[i] = cnt['count']
                        has_value = True
                        # print('day list: ',day_lists[i])
                        print('cnt: ',cnt)
                    
                    nights = []
                    start = 0
                    end = 0
                    # first_day = 0
                    for j in range(len(day_lists)):
                        # print('cnt.shape[0]: ',cnt.shape[0])
                        print('patient_id: ',patient_id[i])
                        print('night: ',j)
                        print('first day: ',first_day)
                        print('week_origin: ', cnt)
                        print('day lists: ',day_lists)
                        print('count: ',day_lists.iloc[j,i+1])
                        if((not has_value) or pd.isna(day_lists.iloc[j,i+1]) or j-first_day+day_info[0]>=cnt.shape[0] ):
                            print('No value :', j)
                            nights.append(None)
                            continue
                        # if(first_day==0):
                        #     first_day = j
                        # print("week1: ",cnt['week'].values[j])
                        if(not pd.isna(cnt.iloc[j-first_day+day_info[0],1])):
                            week = str(cnt['week'].values[j-first_day+day_info[0]])
                            # print('week list: ',week.split('-'))
                            if('-' in week):
                                start = int(week.split('-')[0])
                                end = int(week.split('-')[1])
                            else:
                                start = int(week)
                                end = int(week)
                            # print('start: ',start)
                            # print('end: ',end)
                            # continue
                        week_no = int(np.floor((j+day_info[0])/7)+1)
                        print('week_no: ',week_no)
                        if(week_no>end):
                            if(end>start):
                                week = f"{week_no}-{week_no+1}"
                            else:
                                week = week_no
                        print('week2: ',week)
                        cnt['week'].values[j-first_day+day_info[0]] = str(week)
                        # print('night: ',cnt['night'].values)
                        obj = {'day':j+day_info[0],'count':day_lists[i][j], 'type':type_lists[i][j], 'week':cnt['week'].values[j-first_day+day_info[0]], 'night':cnt['night'].values[j-first_day+day_info[0]]}
                        # print('obj: ',obj)
                        nights.append(obj)
                    print(nights)
                    result_lists.loc[:, patient_id[i]] = nights
                    
                    
            # day_lists = day_lists.set_index('day')
            # day_lists.columns = pd.to_numeric(day_lists.columns)
            # print(day_lists)
            # type_lists = type_lists.set_index('day')
            # type_lists.columns = pd.to_numeric(type_lists.columns)
            # print(type_lists)
            
            # for i in patient_id:
            #     night_info = df[df['patient_id']==i]
            #     if(night_info.empty or night_info.shape[0]==0):
            #         continue
            #     print(night_info)
            #     nights = []
            #     for j in range(len(day_lists)):
            #         night = night_info[night_info['day']==j]
            #         print(night)
            #         if(night.empty or night.shape[0]==0):
            #             week = None
            #             night = None
            #         else:
            #             week = str(night['week'].values[0])
            #             night = int(night['night'].values[0])
            #         obj = {'count':day_lists[i][j], 'type':type_lists[i][j], 'week':week, 'night':night}
            #         # print(obj)
            #         nights.append(obj)
            #     print(nights)
            #     result_lists.loc[:, i] = nights
            result_lists = result_lists.set_index('day')
            print(result_lists)
            # result = {
            #     "day_lists": json.loads(day_lists.to_json(orient="records")),
            #     "type_lists": json.loads(type_lists.to_json(orient="records")),
            #     "result_lists": json.loads(result_lists.to_json(orient="records")),
            # }
            # return json.dumps(result,indent=4), 200
            return json.loads(result_lists.to_json(orient="records")), 200
        except Exception as e:
            print('Exception raised in getting event trend')
            print(e)
            return f"{e}", 500


    @app.route('/label-statistics/<int:patient_id>/<string:week>/<string:night_id>/<int:labelId>', methods=["GET"])
    def get_label_statistics(patient_id, week, night_id, labelId):
        try:
            params = (patient_id, week, night_id, labelId)
            query = "SELECT * from bite_records WHERE (patient_id=? AND week=? AND night_id=? AND labelId=?)"

            with sql.connect(DATABASE) as con:
                print("DB connected")
                cur = con.cursor()
                bite_records = cur.execute(query, params)
                columns = [description[0] for description in bite_records.description]
                print(columns)
                #df = get_patients_recordings_df(columns, patient_data.fetchall())
                bite_records_json = get_json_format_from_query(columns=columns, query_results=bite_records.fetchall()) #, start_id=1, end_id=14)
                
            return bite_records_json, 200
        except Exception as e:
            print('Exception raised in getting label statistics')
            print(e)
            return f"{e}", 500

    return app



    
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)