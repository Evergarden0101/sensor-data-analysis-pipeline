import sqlite3 as sql
# from settings import *
from preprocessing import *
from SSD2 import *
import sys, os, re, math, itertools
import matplotlib.pyplot as plt
import numpy as np
import xgboost as xgb
import seaborn as sns
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, learning_curve, train_test_split, StratifiedKFold, RandomizedSearchCV, LeaveOneOut, cross_val_score
from sklearn.tree import DecisionTreeClassifier as DTC
from sklearn import tree
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib
matplotlib.use('agg')
sql.register_adapter(np.int64, lambda val: int(val))
sql.register_adapter(np.int32, lambda val: int(val))

# TODO: create all utils function for app here separately to make app.py code lighter

"""
Take column names of table and result of a query and return it in json format.
    columns: list with the column names in the database
    query_results: results from the db query
    start_id: id of the first desired db column
    end_id: id of the last desired db column
"""
def get_json_format_from_query(columns, query_results, start_id, end_id):
        values = []
        for query_result in query_results:
            dictionary = {}
            for i in range(start_id, end_id+1):
                dictionary[columns[i]] = query_result[i]

            values.append(dictionary)

        return values

"""Takes night_id and return day, hours, minutes and seconds values"""
# TODO: adapt get_existing_patients function
def get_patient_time_values(night_id):
    try:
        day = night_id[:2]
        hours = night_id[2:4]
        minutes = night_id[4:6]
        seconds = night_id[6]

    except IndexError:
        day = night_id[:2]
        hours = '0' + night_id[2]
        minutes = night_id[3:5]
        seconds = night_id[5]

    return day, hours, minutes, seconds

"""Post patient recording in the database"""
def post_patient_recording(DATABASE, patient_id, week, day, hours, minutes, seconds, patient_file, csvData):
    with sql.connect(DATABASE) as con:
        print("DATABASE CONNECTED")
        cur = con.cursor()

        for i,row in csvData.iterrows():

            params = (patient_id, week, day, hours, minutes, seconds, patient_file[-10], row['MR'],row['ML'],row['SU'],row['Microphone'],row['Eye'], row['ECG'], row['Pressure Sensor'])
            query = "INSERT INTO patients_recordings (patient_id, week, day, hours, minutes, seconds, recorder, MR, ML, SU, Microphone, Eye, ECG, Pressure) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

            cur.execute(query, params)
            print(f"{i} out of {csvData.index[-1]}")



"""
    Retrieve patient recording from database
        range_min: take entries from a certain minutes range, format:
            {
                start_min: int,
                end_min: int
            }
"""
def retrieve_patient_recording(DATABASE, patient_id, week, day, range_min, SAMPLING_RATE):
    with sql.connect(DATABASE) as con:
            print('connected to db', file=sys.stderr)
            cur = con.cursor()

            if not range_min:
                params = (patient_id, week, day)
                patient_recording = f"SELECT * FROM patients_recordings WHERE (patient_id=? AND week=? AND day=?)"

            else:
                start_min = range_min["start_min"]
                end_min = range_min["end_min"]

                if start_min <= end_min:
                    start_min_id = start_min * SAMPLING_RATE * 60
                    end_min_id = end_min * SAMPLING_RATE * 60

                    params = (patient_id, week, day, start_min_id, end_min_id)
                    patient_recording = f"SELECT * FROM patients_recordings WHERE (patient_id=? AND week=? AND day=?) AND (id >= ? AND id <= ?)"
            print('patient_exist query', file=sys.stderr)

            patient_recording_query = cur.execute(patient_recording, params)

            if patient_recording_query.fetchone():
                print('EXIST', file=sys.stderr)

                columns = [description[0] for description in patient_recording_query.description]
                print(columns)
                values = get_json_format_from_query(columns=columns, query_results=patient_recording_query.fetchall(), start_id=0, end_id=13)

                return values, 200

            else:
                print('DOES NOT EXIST', file=sys.stderr)
                return f"There is no data for patient with id {patient_id} on day {day} of week {week}", 404


"""Delete predicted label for a specific patient in the Database"""
def remove_pred_label(DATABASE, label):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute(f"DELETE FROM Predicted_labels WHERE patient_id={label['patient_id']} AND week={label['week']} AND night_id={label['night_id']} AND label_id={label['label_id']}")


"""Insert label for a specific patient in the Database"""
def insert_label(DATABASE, label):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute(f"INSERT INTO confirmed_labels (patient_id, week, night_id, label_id, location_begin, location_end, corrected) VALUES {label['patient_id'],label['week'],label['night_id'],label['label_id'],label['location_begin'],label['location_end'],label['corrected']}")


def generate_model(DATABASE, patient_id, week, night_id, recorder):
    print("generate_model")
    data = open_brux_csv(DATABASE, patient_id, week, night_id, recorder)
    loc = open_brux_loc_csv(DATABASE, patient_id, week, night_id, recorder)
    original_sampling = get_original_sampling(DATABASE)
    selected_sampling =get_selected_sampling(DATABASE)
    # dsample_rate = np.round(original_sampling / selected_sampling).astype("int")
    range_min = 0
    range_max = loc.iloc[2,1]
    bites = np.zeros(data.shape[0], dtype=int)
    print("label bites")
    for i in range(1, range_max):
        if i < loc.iloc[0,0] or (i > loc.iloc[0,1] and i < loc.iloc[1,0]) or (i > loc.iloc[1,1] and i < loc.iloc[2,0]) or i > loc.iloc[2,1]:
            bites[i] = 0
        else:
            bites[i] = 1
    print("add bites")
    MR = get_column_array(get_column_data_from_df(data, "MR"))
    ML = get_column_array(get_column_data_from_df(data, "ML"))
    MR = resample_signal(signal=MR, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    ML = resample_signal(signal=ML, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)

    # df = resample_whole_df(data,original_sampling,selected_sampling)
    bites = resample_signal(signal=bites, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    # df.loc[:,'Bites'] = bites
    df = pd.DataFrame({'MR': MR, 'ML': ML, 'Bites': bites})

    x = df.iloc[range_min:range_max,:2].copy()
    y = df.iloc[range_min:range_max,-1].copy()
    x = np.array(x.values.tolist())
    y = np.array(y.values.tolist())

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25) # Split data for test and training
    SC = StandardScaler()
    x_train = pd.DataFrame(SC.fit_transform(x_train))
    x_test = pd.DataFrame(SC.transform(x_test))

    print("fit model")
    model = xgb.XGBClassifier(n_estimators=100, objective='binary:logistic',
        eval_metric='logloss', subsample=0.6, max_depth=3, learning_rate=0.1, colsample_bytree=1.0)
    model.fit(x_train, y_train)

    print("save model")
    with sql.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute(f"INSERT INTO models (patient_id, model_path) VALUES {patient_id, get_data_path(DATABASE) + f'p{patient_id}_model.json'}")
        model.save_model(get_data_path(DATABASE) + f"p{patient_id}_model.json")
        
        cur.execute(f"SELECT * FROM models WHERE patient_id = -1")
        general_model = cur.fetchall()
        if not general_model:
            cur.execute(f"INSERT INTO models (patient_id, model_path) VALUES {-1, get_data_path(DATABASE) + f'general_model.json'}")
            model.save_model(get_data_path(DATABASE) + f'general_model.json')
        cur.close()

    model.save_model(get_data_path(DATABASE) + f"p{patient_id}_model.json")
    predict_events(DATABASE, model,patient_id, week, night_id)
    # return model

"""TODO: Run Prediction"""
def predict_events(DATABASE, model, patient_id, week, night_id, recorder):
    print("predict_events")
    filePath = get_data_path(DATABASE)+'p'+str(patient_id)+'_w'+str(week)+f'/'+str(night_id)+f'{recorder}Fnorm.csv'
    # data = open_brux_csv(patient_id, week, night_id, recorder)
    data = pd.read_csv(filePath)
    selected = get_selected_intervals(patient_id, week, night_id, DATABASE)
    # print(selected[0]['start_id'])
    # print(selected[0][0])
    df = pd.DataFrame()
    for i in range(len(selected)):
        df = df._append(data.iloc[selected[i]['start_id']:selected[i]['end_id'],:])
    index = df.index
    # print(index)

    original_sampling = get_original_sampling(DATABASE)
    selected_sampling =get_selected_sampling(DATABASE)
    # df = resample_whole_df(df,original_sampling,selected_sampling)
    MR = get_column_array(get_column_data_from_df(df, "MR"))
    ML = get_column_array(get_column_data_from_df(df, "ML"))
    MR = resample_signal(signal=MR, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    ML = resample_signal(signal=ML, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    df = pd.DataFrame({'MR': MR, 'ML': ML})

    index = resample_signal(signal=index, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    print(index[10])

    x = df.iloc[:,:2].copy()
    x_p = np.array(x.values.tolist())
    # model.set_param({"device": "gpu"})
    y_p = model.predict(x_p)
    y_p_mix = []
    i = 0
    event = 0
    loc_end = 0
    print(len(y_p))
    with sql.connect(DATABASE) as con:
        cur = con.cursor()
        while i < len(y_p):
            y_sum = y_p[i];
            cnt = 1;
            for j in range(1, 5*selected_sampling):
                if(i+j >= len(y_p)):
                    break;
                y_sum += y_p[i+j];
                cnt += 1;
            if y_sum/cnt >= 0.5:
                if(len(y_p_mix)==0 or y_p_mix[-1] != 10):
                    event += 1
                    loc_end = i+cnt
                    location_begin = index[i]
                    location_end = index[loc_end]
                    params = (patient_id, week, night_id, event, location_begin, location_end, i, loc_end)
                    print(params, ' ', location_begin,' ', location_end)
                    query = "INSERT INTO predicted_labels (patient_id, week, night_id, label_id, location_begin, location_end, start_index, end_index) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                    cur.execute(query, params)
                    
                    cycle = np.floor(location_begin / 90 / 60 / original_sampling)+1;
                    params = (patient_id, week, night_id, cycle)
                    query = "SELECT count from week_summary WHERE patient_id=? AND week=? AND night_id=? AND cycle=?"
                    cur.execute(query, params)
                    count = cur.fetchall()
                    if count:
                        print(count[0][0])
                        params = (count[0][0]+1, patient_id, week, night_id, cycle)
                        query = "UPDATE week_summary SET count = ? WHERE patient_id=? AND week=? AND night_id=? AND cycle=?"
                        cur.execute(query, params)
                    else:
                        params = (patient_id, week, night_id, cycle, 1)
                        query = "INSERT INTO week_summary (patient_id, week, night_id, cycle, count) VALUES (?, ?, ?, ?, ?)"
                        cur.execute(query, params)
                    print("current end:", loc_end)
                elif(y_p_mix[-1] == 10):
                    params = (index[loc_end+cnt], loc_end+cnt, patient_id, week, night_id, event)
                    query = "UPDATE predicted_labels SET location_end = ?, end_index = ? WHERE patient_id=? AND week=? AND night_id=? AND label_id=?;"
                    cur.execute(query, params)
                    loc_end += cnt
                    print("update end:", loc_end)
                y_p_mix.extend([10]*cnt);
            else:
                y_p_mix.extend([0]*cnt);
            i += cnt;
            # print(i)
    print(event)
    return y_p_mix



"""TODO: check predictions"""
def run_prediction(DATABASE, patient_id, week, night_id, recorder):
    print("run_prediction")
    try:
        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            params = (patient_id, week, night_id)
            query = "SELECT * from predicted_labels WHERE (patient_id=? AND week=? AND night_id=?)"
            labels = cur.execute(query, params).fetchall()
            print(labels)
            if labels:
                print("Labels already exist")
                return labels

            cur.execute(f"SELECT * FROM models WHERE patient_id={patient_id}")
            model = cur.fetchall()
            cur.close()
        if model:
            print("Model already exist")
            xgbc = xgb.XGBClassifier()
            xgbc.load_model(str(model[0][-1]))
            predict_events(DATABASE, xgbc, patient_id, week, night_id, recorder)
        else:
            print("Model does not exist")
            # loc_file = get_data_path(DATABASE) + f"p{patient_id}_w{week}/{night_id}clocation_Bites.csv"
            # loc = pd.read_csv(loc_file)
            # print(loc)
            # for i,row in loc.iterrows():

            #     params = (patient_id, week, night_id, i+1, row['Location Begin'],row['Location end'])
            #     query = "INSERT INTO predicted_labels (patient_id, week, night_id, label_id, location_begin, location_end) VALUES (?, ?, ?, ?, ?, ?)"
            #     with sql.connect(DATABASE) as con:
            #         cur = con.cursor()
            #         cur.execute(query, params)
            #         cur.close()
            #     print(f"{i} out of {loc.index[-1]}")
            model = generate_model(DATABASE, patient_id, week, night_id, recorder)
            predict_events(DATABASE, model,patient_id, week, night_id, recorder)
        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            params = (patient_id, week, night_id)
            query = "SELECT * from predicted_labels WHERE (patient_id=? AND week=? AND night_id=?)"
            labels = cur.execute(query, params)
            return labels
    except Exception as e:
            print('Exception raised in run_prediction function')
            print(e)
            return f"{e}", 500


def return_img_stream(img_path):
    import base64
    img_stream = ''
    with open(img_path, 'rb') as img_f:
        img_stream = img_f.read()
        img_stream = base64.b64encode(img_stream).decode()
    return img_stream


def get_ssd_values(DATABASE, patient_id, week, night_id, recorder):
    day, hours, minutes, seconds = get_patient_time_values(night_id)
    with sql.connect(DATABASE) as con:
        print('connected to db', file=sys.stderr)
        cur = con.cursor()

        print('cur variable defined', file=sys.stderr)

        params = (patient_id, week, day, hours, minutes, seconds, recorder)
        patient_exist = f"SELECT * FROM sleep_stage_detection WHERE (patient_id=? AND week=? AND day=? AND hours=? AND minutes=? AND seconds=? AND recorder=?)"
        print('patient_exist query', file=sys.stderr)

        if cur.execute(patient_exist, params).fetchall():
            print('EXIST', file=sys.stderr)
            params = (patient_id, week, day, hours, minutes, seconds, recorder)
            query = "SELECT * FROM sleep_stage_detection WHERE (patient_id=? AND week=? AND day=? AND hours=? AND minutes=? AND seconds=? AND recorder=?)"
            result = cur.execute(query, params)
            columns = [description[0] for description in result.description]
            print(f"Columns: {columns}")
            values = get_json_format_from_query(columns=columns, query_results=result.fetchall(), start_id=1, end_id=14)

        else:
            print('DOES NOT EXIST', file=sys.stderr)
            print(patient_id, week, night_id)
            values = get_HRV_features(DATABASE, patient_id, week, night_id, recorder, get_original_sampling(DATABASE))

            for value in values:
                params = (patient_id, week, day, hours, minutes, seconds, value['start_id'], value['end_id'], value['LF_HF'], value['SD'], value['stage'], value['y'], value['x'], 0, recorder)
                query = "INSERT INTO sleep_stage_detection (patient_id, week, day, hours, minutes, seconds, start_id, end_id, LF_HF, SD, stage, y, x, selected, recorder) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                cur.execute(query, params)

        return values

def post_selected_updates(DATABASE, patient_id, week, night_id, updates):
    with sql.connect(DATABASE) as con:
        print('connected to db', file=sys.stderr)
        cur = con.cursor()

        day, hours, minutes, seconds = get_patient_time_values(night_id)

        params = (patient_id, week, day, hours, minutes, seconds)
        query = "UPDATE sleep_stage_detection SET selected = 0 WHERE patient_id=? AND week=? AND day=? AND hours=? AND minutes=? AND seconds=?"

        cur.execute(query, params)

        for update in updates:
            params = (patient_id, week, day, hours, minutes, seconds, update["x"], update["y"])

            query = "UPDATE sleep_stage_detection SET selected = 1 WHERE patient_id=? AND week=? AND day=? AND hours=? AND minutes=? AND seconds=? AND x=? AND y=?"
            cur.execute(query, params)


def get_selected_phases(DATABASE, patient_id, week, night_id):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        day, hours, minutes, seconds = get_patient_time_values(night_id)

        params = (patient_id, week, day, hours, minutes, seconds, 1)

        query = ("SELECT x,y,ROUND(SD),stage, LF_HF FROM sleep_stage_detection WHERE patient_id=? AND week=? AND day=? AND hours=? AND minutes=? AND seconds=? AND selected=?")

        selected = cur.execute(query, params).fetchall()

        result = [list(s) for s in selected]


        return result
        #return get_json_format_from_query(columns=columns, query_results=selected.fetchall(), start_id=0, end_id=1)

def get_standard_selected_phases(DATABASE, patient_id, week, night_id):
    print("standard selected phases")
    SDNNmin = get_herzig_ranges()['SSDNRem']['min']
    SDNNmax = get_herzig_ranges()['SSDNRem']['max']
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        day, hours, minutes, seconds = get_patient_time_values(night_id)

        params = (patient_id, week, day, hours, minutes, seconds, 'rem', SDNNmin, SDNNmax)

        query = ("SELECT x,y,ROUND(SD),stage, LF_HF FROM sleep_stage_detection WHERE patient_id=? AND week=? AND day=? AND hours=? AND minutes=? AND seconds=? AND stage=? AND (SD BETWEEN ? AND ?)")

        selected = cur.execute(query, params).fetchall()

        result = [list(s) for s in selected]


        return result

"""Get all the patients, weeks and night ids"""
def get_existing_patients_data(DATABASE):
    existing_patients_recordings = []

    for folder in os.listdir(get_data_path(DATABASE)):
        if not os.path.isdir(get_data_path(DATABASE) + folder):
            continue
        patient_id = re.search('p(.*?)_', folder).group(1)

        patient_week_folder = get_data_path(DATABASE) + folder

        csv_files = [f for f in os.listdir(patient_week_folder) if f.endswith(".csv")]

        night_id_list= []
        night_id_recorder = {}
        for csv in csv_files:
            night_id = re.search("[0-9]+", csv).group(0)
            night_id_list.append(night_id)

            if "location_Bites" not in csv:
                recorder = re.search('.(?=F)', csv).group(0)
                night_id_recorder[night_id] = recorder

        if night_id_list:
            week = re.search('wk(.*)', folder).group(1)
            night_id_list = list(set(night_id_list))
            night_id_list = sorted(night_id_list)

            for night_id in night_id_list:
                existing_patients_recordings.append({
                    "patient_id": patient_id,
                    "week": week,
                    "night_id": night_id,
                    "recorder": night_id_recorder[night_id]

                })

    return existing_patients_recordings


"""Returns study type stored in db"""
def get_study_type(DATABASE):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        study_type = cur.execute("SELECT study_type FROM settings WHERE id=1").fetchone()[0]

    return study_type

"""Returns activity type stored in db"""
def get_activity(DATABASE):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        activity = cur.execute("SELECT activity FROM settings WHERE id=1").fetchone()[0]

    return activity

"""Returns original sampling rate stored in db"""
def get_original_sampling(DATABASE):
    try:
        with sql.connect(DATABASE) as con:
            cur = con.cursor()

            original_sampling = cur.execute("SELECT original_sampling FROM settings WHERE id=1").fetchone()[0]
    except Exception as e:
        original_sampling = 2000
    return original_sampling


"""Returns selected sampling rate stored in db"""
def get_selected_sampling(DATABASE):
    try:
        with sql.connect(DATABASE) as con:
            cur = con.cursor()

            selected_sampling = cur.execute("SELECT selected_sampling FROM settings WHERE id=1").fetchone()[0]
    except Exception as e:
            selected_sampling = 1000
    return selected_sampling

"""Returns non selected sampling rate stored in db"""
def get_non_selected_sampling(DATABASE):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        non_selected_sampling = cur.execute("SELECT non_selected_sampling FROM settings WHERE id=1").fetchone()[0]

    return non_selected_sampling

"""Returns dataset format stored in db"""
def get_dataset_format(DATABASE):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        dataset_format = cur.execute("SELECT dataset_format FROM settings WHERE id=1").fetchone()[0]

    return dataset_format

"""Returns boolean that indicates if dataset is filtered stored in db"""
def get_is_filtered(DATABASE):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        filtered = cur.execute("SELECT filtered FROM settings WHERE id=1").fetchone()[0]

    return filtered

"""Returns boolean that indicates if dataset is filtered stored in db"""
def get_is_normalized(DATABASE):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        normalized = cur.execute("SELECT normalized FROM settings WHERE id=1").fetchone()[0]

    return normalized


"""Returns settings stored in db as list of json"""
def get_settings(DATABASE):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        settings = cur.execute("SELECT * FROM settings WHERE id=1")
        columns = [description[0] for description in settings.description]


        return get_json_format_from_query(columns, settings.fetchall(), 1, 9)[0]


"""Returns sensors stored in db as list of json"""
def get_sensors(DATABASE):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        sensors = cur.execute("SELECT * FROM sensors")
        columns = [description[0] for description in sensors.description]

        return get_json_format_from_query(columns, sensors.fetchall(), 1, 2)

"""Retrieve selected intervals from DB"""
def get_sleep_cycle_selected_intervals(patient_id, week, night_id, DATABASE, start_id, end_id):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        day, hours, minutes, seconds = get_patient_time_values(night_id)

        params = (1, patient_id, week, day, hours, minutes, seconds, start_id, end_id)
        query = "SELECT start_id, end_id FROM sleep_stage_detection WHERE selected=? AND patient_id=? AND week=? AND day=? AND hours=? AND minutes=? and seconds=? and start_id>=? and end_id<=?"

        result = cur.execute(query, params)
        columns = [description[0] for description in result.description]

        return get_json_format_from_query(columns=columns, query_results=result.fetchall(), start_id=0, end_id=1)

"""Retrieve selected intervals from DB"""
def get_selected_intervals(patient_id, week, night_id, DATABASE):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        day, hours, minutes, seconds = get_patient_time_values(night_id)

        params = (1, patient_id, week, day, hours, minutes, seconds)
        query = "SELECT start_id, end_id FROM sleep_stage_detection WHERE selected=? AND patient_id=? AND week=? AND day=? AND hours=? AND minutes=? and seconds=?"

        result = cur.execute(query, params)
        columns = [description[0] for description in result.description]

        return get_json_format_from_query(columns=columns, query_results=result.fetchall(), start_id=0, end_id=1)


"""Retrieve REM intervals from DB"""
def get_rem_intervals(patient_id, week, night_id, DATABASE):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        day, hours, minutes, seconds = get_patient_time_values(night_id)

        params = ('rem', patient_id, week, day, hours, minutes, seconds)
        query = "SELECT start_id, end_id FROM sleep_stage_detection WHERE stage=? AND patient_id=? AND week=? AND day=? AND hours=? AND minutes=? and seconds=?"

        result = cur.execute(query, params)
        columns = [description[0] for description in result.description]

        return get_json_format_from_query(columns=columns, query_results=result.fetchall(), start_id=0, end_id=1)



def get_sleep_cycle_sampling_ranges(DATABASE, mr, ml, ranges, start_id, end_id):
    if len(mr) == len(ml):
        final_ds = []
        ranges_nr = len(ranges)
        tmp = start_id

        for idx, range in enumerate(ranges):
            # Corner case: start
            if range["start_id"] == start_id:
                mr_start = mr.loc[range["start_id"]: range["end_id"]-1]
                ml_start = ml.loc[range["start_id"]: range["end_id"]-1]

                print(f"print length mr: ")

                final_ds.append({
                    "start_id": range["start_id"],
                    "end_id": range["end_id"],
                    "target_sampling_rate": get_selected_sampling(DATABASE),
                    "mr_array": mr_start.values.tolist(),
                    "ml_array": ml_start.values.tolist()

                })
                tmp = range["end_id"]

            else:
                # non selected ranges
                if tmp != range["start_id"]:
                    mr_ns = mr.loc[tmp: range["start_id"]-1]
                    ml_ns = ml.loc[tmp: range["start_id"]-1]

                    final_ds.append({
                        "start_id": tmp,
                        "end_id": range["start_id"],
                        "target_sampling_rate":  get_non_selected_sampling(DATABASE),
                        "mr_array": mr_ns.values.tolist(),
                        "ml_array": ml_ns.values.tolist(),
                    })


                # selected ranges
                mr_s = mr.loc[range["start_id"]: range["end_id"]-1]
                ml_s = ml.loc[range["start_id"]: range["end_id"]-1]

                final_ds.append({
                    "start_id": range["start_id"],
                    "end_id": range["end_id"],
                    "target_sampling_rate": get_selected_sampling(DATABASE),
                    "mr_array": mr_s.values.tolist(),
                    "ml_array": ml_s.values.tolist()
                })
                tmp = range["end_id"]

                # Corner case: end
                if idx == ranges_nr-1:
                    print("corner case")
                    if range["end_id"] != end_id:
                        mr_end = mr.loc[tmp: end_id-1]
                        ml_end = ml.loc[tmp: end_id-1]

                        final_ds.append({
                        "start_id": tmp,
                        "end_id": end_id,
                        "target_sampling_rate":  get_non_selected_sampling(DATABASE),
                        "mr_array": mr_end.values.tolist(),
                        "ml_array": ml_end.values.tolist()
                    })
        return final_ds

    else:
        return "MR and ML should have the same length."



"""Get the ranges for the resampling of the dataset"""
def get_sampling_ranges(DATABASE, mr, ml, ranges):
    if len(mr) == len(ml):
        final_ds = []
        ranges_nr = len(ranges)
        tmp = 0

        for idx, range in enumerate(ranges):
            # Corner case: start
            if range["start_id"] == 0:
                mr_start = mr[range["start_id"]: range["end_id"]]
                ml_start = ml[range["start_id"]: range["end_id"]]

                final_ds.append({
                    "start_id": range["start_id"],
                    "end_id": range["end_id"],
                    "target_sampling_rate": get_selected_sampling(DATABASE),
                    "mr_array": mr_start,
                    "ml_array": ml_start

                })
                tmp = range["end_id"]

            else:
                # non selected ranges

                if tmp != range["start_id"]:
                    mr_ns = mr[tmp: range["start_id"]]
                    ml_ns = ml[tmp: range["start_id"]]

                    final_ds.append({
                        "start_id": tmp,
                        "end_id": range["start_id"],
                        "target_sampling_rate":  get_non_selected_sampling(DATABASE),
                        "mr_array": mr_ns,
                        "ml_array": ml_ns,
                    })


                # selected ranges
                mr_s = mr[range["start_id"]: range["end_id"]]
                ml_s = ml[range["start_id"]: range["end_id"]]

                final_ds.append({
                    "start_id": range["start_id"],
                    "end_id": range["end_id"],
                    "target_sampling_rate": get_selected_sampling(DATABASE),
                    "mr_array": mr_s,
                    "ml_array": ml_s
                })
                tmp = range["end_id"]

                # Corner case: end
                if idx == ranges_nr-1:
                    if range["end_id"] != len(mr):
                        mr_end = mr[tmp: len(mr)]
                        ml_end = ml[tmp: len(mr)]

                        final_ds.append({
                        "start_id": tmp,
                        "end_id": len(mr),
                        "target_sampling_rate":  get_non_selected_sampling(DATABASE),
                        "mr_array": mr_end,
                        "ml_array": ml_end
                    })
        return final_ds

    else:
        return "MR and ML should have the same length."


"""Resample the ranges obtained from the function above and return dataframe with columns"""
def get_resampled_ranges(DATABASE, sampling_ranges):
    for sampling_range in sampling_ranges:
        sampling_range["mr_array"] = nk.signal_resample(sampling_range['mr_array'], method="interpolation", sampling_rate=get_original_sampling(DATABASE), desired_sampling_rate=sampling_range["target_sampling_rate"]).tolist()
        sampling_range["ml_array"] = nk.signal_resample(sampling_range["ml_array"], method="interpolation", sampling_rate=get_original_sampling(DATABASE), desired_sampling_rate=sampling_range["target_sampling_rate"]).tolist()

    return sampling_ranges

def get_event_data(DATABASE, desired_chunk, start_id, end_id, location_begin, location_end):
    # Extract the interesting 5 minutes (or more)
    mr = desired_chunk["MR"].loc[start_id:end_id-1]
    ml = desired_chunk["ML"].loc[start_id:end_id-1]
    
    original_sampling = get_original_sampling(DATABASE)
    selected_sampling = get_selected_sampling(DATABASE)
    cnt = [(start_id+i)/original_sampling for i in range(len(mr))]

    # Extract the portion in which event occurs to find indices (we do it only for mr since indices are the same)
    mr_event_data = desired_chunk["MR"].loc[location_begin:location_end-1]

    # Find start and end indices of event list in original 5 minute of data
    new_event_subindices = find_sub_list(mr_event_data.values.tolist(), mr.values.tolist())

    # Divide MR data in 3 chunks
    mr_first_chunk = mr.values.tolist()[: new_event_subindices[0]]
    mr_event_chunk = mr.values.tolist()[new_event_subindices[0]: new_event_subindices[1] + 1]
    mr_third_chunk = mr.values.tolist()[new_event_subindices[1]+1:]

    # Divide ML data in 3 chunks
    ml_first_chunk = ml.values.tolist()[: new_event_subindices[0]]
    ml_event_chunk = ml.values.tolist()[new_event_subindices[0]: new_event_subindices[1] + 1]
    ml_third_chunk = ml.values.tolist()[new_event_subindices[1]+1:]

    # Resample MR data
    resmapled_mr_first_chunk =  nk.signal_resample(mr_first_chunk, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()
    resmapled_mr_event_chunk =  nk.signal_resample(mr_event_chunk, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()
    resmapled_mr_third_chunk =  nk.signal_resample(mr_third_chunk, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()

    # Resample ML data
    resmapled_ml_first_chunk =  nk.signal_resample(ml_first_chunk, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()
    resmapled_ml_event_chunk =  nk.signal_resample(ml_event_chunk, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()
    resmapled_ml_third_chunk =  nk.signal_resample(ml_third_chunk, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()

    # Concatenate MR and ML chunks
    mr_resampled = list(itertools.chain(resmapled_mr_first_chunk, resmapled_mr_event_chunk, resmapled_mr_third_chunk))
    ml_resampled = list(itertools.chain(resmapled_ml_first_chunk, resmapled_ml_event_chunk, resmapled_ml_third_chunk))
    
    cnt = nk.signal_resample(cnt, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()

    # Find event indices of the new resampled data
    new_event_resampled_subindices = find_sub_list(resmapled_mr_event_chunk, mr_resampled)

    result = {
        "5min_start_id": start_id,
        "5min_end_id": end_id,
        "start_id": 0,
        "end_id": len(mr_resampled)-1,
        "MR": mr_resampled,
        "ML": ml_resampled,
        "event_start_id": new_event_resampled_subindices[0],
        "event_end_id": new_event_resampled_subindices[1],
        "cnt": cnt
    }

    return result

def find_sub_list(sl,l):
    sll=len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll]==sl:
            return ind,ind+sll-1

def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw=None, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (M, N).
    row_labels
        A list or array of length M with the labels for the rows.
    col_labels
        A list or array of length N with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if ax is None:
        ax = plt.gca()

    if cbar_kw is None:
        cbar_kw = {}

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    # cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    # cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # Show all ticks and label them with the respective list entries.
    ax.set_xticks(np.arange(data.shape[1]), labels=col_labels)
    ax.set_yticks(np.arange(data.shape[0]), labels=row_labels)

    ax.set_aspect(0.66)

    # Let the horizontal axes labeling appear on top.
    # ax.tick_params(top=True, bottom=False,
    #                labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    # plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
    #          rotation_mode="anchor")

    # Turn spines off and create white grid.
    ax.spines[:].set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im


def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=("black", "white"),
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A pair of colors.  The first is used for values below a threshold,
        the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts


"""Generate weekly summary image"""
"""TODO: get len and data"""
def generate_weekly_sum_img(DATABASE, img_local_path):
    len = 74155516
    print(len)
    original_sampling = get_original_sampling(DATABASE)
    cycle_num = int(np.ceil(len / original_sampling / 90 / 60))
    cycles = list(range(1, cycle_num + 1))
    days = list(range(1, 8))
    data = np.array([[1,0,0,0,0,0,0],
                [2,1,0,3,3,0,2],
                [1,3,0,0,0,1,0],
                [0,0,0,0,0,0,0],
                [1,1,0,0,4,2,0],
                [7,0,0,0,0,0,0],
                [5,1,0,0,0,0,0]])
    fig, ax = plt.subplots()

    im = heatmap(data, days, cycles, ax=ax,
                    cmap="YlOrRd")
    texts = annotate_heatmap(im, valfmt="{x:d}")

    # ax.set_title("Weekly Events Detected for Patient")
    fig.tight_layout()
    plt.savefig(img_local_path)
    print("Image saved")


"""Generate night prediction image"""
def generate_night_pred_img(DATABASE, patient_id, week, night_id, recorder):
    # data = pd.read_csv(night_path+night+f'{recorder}Fnorm.csv')
    # loc = pd.read_csv(night_path+night+'clocation_Bites.csv')
    # original_sampling = get_original_sampling(DATABASE)
    # selected_sampling = get_selected_sampling(DATABASE)
    # dsample_rate = np.round(original_sampling / selected_sampling).astype("int")
    # print(dsample_rate)
    # df = resample_whole_df(data)
    # print(df.shape)
    # print(loc.iloc[-1,:])
    # range_min = 0
    # range_max = loc.iloc[2,1]
    # bites = np.zeros(data.shape[0], dtype=int)
    # for i in range(1, range_max*dsample_rate):
    #     if i < loc.iloc[0,0] or (i > loc.iloc[0,1] and i < loc.iloc[1,0]) or (i > loc.iloc[1,1] and i < loc.iloc[2,0]) or i > loc.iloc[2,1]:
    #         bites[i] = 0
    #     else:
    #         bites[i] = 1

    # df.loc[:,'Bites'] = bites[::dsample_rate]
    # x = df.iloc[range_min:range_max,:2].copy()
    # y = df.iloc[range_min:range_max,-1].copy()
    # x = np.array(x.values.tolist())
    # y = np.array(y.values.tolist())
    # print(x.shape)
    # print(y.shape)

    # x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25) # Split data for test and training
    # SC = StandardScaler()
    # x_train = pd.DataFrame(SC.fit_transform(x_train))
    # x_test = pd.DataFrame(SC.transform(x_test))

    # best_xgb = xgb.XGBClassifier(n_estimators=100, objective='binary:logistic',
    #     eval_metric='logloss', subsample=0.6, max_depth=3, learning_rate=0.1, colsample_bytree=1.0)
    # best_xgb.fit(x_train, y_train)

    # accuracies = cross_val_score(estimator = best_xgb, X = x_train, y = y_train, cv = 10)
    # print(accuracies.mean(), accuracies.std())
    # x_p = df.iloc[:,:2].copy()
    # x_p = np.array(x_p.values.tolist())
    # y_p = best_xgb.predict(x_p)
    # y_p_mix = []
    # i = 0
    # event = 0
    # while i < len(y_p):
    #     y_sum = y_p[i];
    #     cnt = 1;
    #     for j in range(1, 5000):
    #         if(i+j >= len(y_p)):
    #             break;
    #         y_sum += y_p[i+j];
    #         cnt += 1;
    #     if y_sum/cnt >= 0.5:
    #         if(len(y_p_mix)==0 or y_p_mix[-1] != 10):
    #             event += 1
    #         y_p_mix.extend([10]*cnt);
    #     else:
    #         y_p_mix.extend([0]*cnt);
    #     i += cnt;
    week_path = get_data_path(DATABASE)+'p'+str(patient_id)+'_wk'+str(week)+f'/'
    data = pd.read_csv(week_path+night_id+f'{recorder}Fnorm.csv')
    selected = get_selected_intervals(patient_id, week, night_id, DATABASE)
    print(selected[0]['start_id'])
    # print(selected[0][0])
    df = pd.DataFrame()
    for i in range(len(selected)):
        df = df._append(data.iloc[selected[i]['start_id']:selected[i]['end_id'],:])
    # index = df.index
    print(df.shape)
    original_sampling = get_original_sampling(DATABASE)
    selected_sampling =get_selected_sampling(DATABASE)
    MR = get_column_array(get_column_data_from_df(df, "MR"))
    ML = get_column_array(get_column_data_from_df(df, "ML"))
    MR = resample_signal(signal=MR, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    ML = resample_signal(signal=ML, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    # index = resample_signal(signal=index, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    x_p = pd.DataFrame({'MR': MR, 'ML': ML})
    x_p = np.array(x_p.values.tolist())

    with sql.connect(DATABASE) as con:
        print("DB connected")
        params = (patient_id, week, night_id)
        query = "SELECT * from predicted_labels WHERE (patient_id=? AND week=? AND night_id=?)"
        cur = con.cursor()
        predicted_labels = cur.execute(query, params)
        columns = [description[0] for description in predicted_labels.description]
        print(columns)
        #df = get_patients_recordings_df(columns, patient_data.fetchall())
        predicted_labels_json = get_json_format_from_query(columns=columns, query_results=predicted_labels.fetchall(), start_id=1, end_id=10)
        cur.close()
    print(predicted_labels_json)

    y_p_mix = []
    prev = 0
    for i in range(len(predicted_labels_json)):
        y_p_mix.extend([0]*(predicted_labels_json[i]['start_index']-prev))
        y_p_mix.extend([10]*(predicted_labels_json[i]['end_index']-predicted_labels_json[i]['start_index']))
        prev = predicted_labels_json[i]['end_index']
    print(len(y_p_mix))
    if(len(y_p_mix) < len(x_p)):
        y_p_mix.extend([0]*(len(x_p)-len(y_p_mix)))

    fig, ax = plt.subplots(1,1, figsize=(50, 15), sharey=True)
    X = np.linspace(0, x_p.shape[0]/selected_sampling, x_p.shape[0])
    ax.plot(X, x_p[:,0],color='r',alpha=0.3, label='MR')
    print("print MR")
    ax.plot(X, x_p[:,1],color='b',alpha=0.3, label='ML')
    print("print ML")
    ax.plot(X, y_p_mix[:],color='g',alpha=0.6,linewidth=4, label='Predicted Brux')
    print("print predicted")
    neg_pred = [-x for x in y_p_mix]
    ax.plot(X, neg_pred[:],color='g',alpha=0.6,linewidth=4)
    ax.legend(loc='upper left', fontsize=20)
    ax.set_ylim(-11,11)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude (mV)')
    plt.savefig(week_path+str(night_id)+'.png',bbox_inches='tight')
    # best_xgb.save_model("p1.json")
