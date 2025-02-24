import itertools
import os
import re
import shutil
import sqlite3 as sql
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import xgboost as xgb
# from settings import *
from preprocessing import *
from sklearn import model_selection
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             make_scorer, precision_score, recall_score)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier as DTC
from SSD import *

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
"""Post patient recording in the database"""
def post_patient_recording(DATABASE, patient_id, week, night_id, patient_file, csvData):
    with sql.connect(DATABASE) as con:
        print("DATABASE CONNECTED")
        cur = con.cursor()

        for i,row in csvData.iterrows():

            params = (patient_id, week, night_id, patient_file[-10], row['MR'],row['ML'],row['SU'],row['Microphone'],row['Eye'], row['ECG'], row['Pressure Sensor'])
            query = "INSERT INTO patients_recordings (patient_id, week, night_id, recorder, MR, ML, SU, Microphone, Eye, ECG, Pressure) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

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
def retrieve_patient_recording(DATABASE, patient_id, week, night_id, range_min, SAMPLING_RATE):
    with sql.connect(DATABASE) as con:
            print('connected to db', file=sys.stderr)
            cur = con.cursor()

            if not range_min:
                params = (patient_id, week, night_id)
                patient_recording = f"SELECT * FROM patients_recordings WHERE (patient_id=? AND week=? AND night_id=?)"

            else:
                start_min = range_min["start_min"]
                end_min = range_min["end_min"]

                if start_min <= end_min:
                    start_min_id = start_min * SAMPLING_RATE * 60
                    end_min_id = end_min * SAMPLING_RATE * 60

                    params = (patient_id, week, night_id, start_min_id, end_min_id)
                    patient_recording = f"SELECT * FROM patients_recordings WHERE (patient_id=? AND week=? AND night_id=?) AND (id >= ? AND id <= ?)"
            print('patient_exist query', file=sys.stderr)

            patient_recording_query = cur.execute(patient_recording, params)

            if patient_recording_query.fetchone():
                print('EXIST', file=sys.stderr)

                columns = [description[0] for description in patient_recording_query.description]
                print(columns)
                values = get_json_format_from_query(columns=columns, query_results=patient_recording_query.fetchall(), start_id=0, end_id=9)

                return values, 200

            else:
                print('DOES NOT EXIST', file=sys.stderr)
                return f"There is no data for patient with id {patient_id} on night {night_id} of week {week}", 404


"""Delete predicted label for a specific patient in the Database"""
def remove_pred_label(DATABASE, label):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute(f"DELETE FROM predicted_labels WHERE patient_id={label['patient_id']} AND week='{label['week']}' AND night_id='{label['night_id']}' AND label_id={label['label_id']}")


"""Insert label for a specific patient in the Database"""
def insert_label(DATABASE, labels):
    original_sampling = get_original_sampling(DATABASE)
    cur_cycle = -1
    count = 0
    with sql.connect(DATABASE) as con:
        print("DB connected")
        cur = con.cursor()
        for label in labels:
                # if label["location_begin"] > label["location_end"]:
                #     return "Start time cannot be greater than end time!", 400
            print('label: ', label)
            if(not label['Confirm']):
                continue
            cur.execute(f"INSERT INTO confirmed_labels (patient_id, week, night_id, recorder, label_id, location_begin, location_end, start_index, end_index, start_time, end_time) VALUES {label['patient_id'],label['week'],label['night_id'],label['recorder'],label['label_id'],label['location_begin'],label['location_end'],label['start_index'],label['end_index'],label['Start'],label['End']}")
            print("inserted label")
            cycle = int(np.floor(label['location_begin'] / 90 / 60 / original_sampling))
            print("cycle:", cycle)
            if  (cur_cycle == -1):
                print("first cycle")
                cur_cycle = cycle
                count = 1
            elif cycle == cur_cycle:
                print("same cycle")
                count += 1
            elif (cycle != cur_cycle):
                print("new cycle")
                print("cur cycle:", cur_cycle, "new cycle:", cycle)
                cur.execute(f"SELECT type from week_summary WHERE (patient_id={label['patient_id']} AND week='{label['week']}' AND night_id='{label['night_id']}' AND cycle={cur_cycle})")
                type_ind = cur.fetchone()[0]
                print("type_ind:", type_ind)
                if type_ind != 0:
                    type_ind = count
                cur.execute(f"UPDATE week_summary SET count = {count}, type = {type_ind} WHERE (patient_id={label['patient_id']} AND week='{label['week']}' AND night_id='{label['night_id']}' AND cycle={cur_cycle})")
                print("cycle:", cur_cycle, "count:", count, "type:", type_ind)
                count = 1
                cur_cycle = cycle
            print()
        

def generate_model(DATABASE, patient_id, week, night_id, recorder):
    print("generate_model")
    data = open_brux_csv(DATABASE, patient_id, week, night_id, recorder)
    loc = open_brux_loc_csv(DATABASE, patient_id, week, night_id, recorder)
    original_sampling = get_original_sampling(DATABASE)
    selected_sampling =get_selected_sampling(DATABASE)
    # dsample_rate = np.round(original_sampling / selected_sampling).astype("int")
    range_min = 0
    range_max = int(float(loc.iloc[2,1]))
    bites = np.zeros(data.shape[0], dtype=int)
    print("label bites")
    for i in range(1, range_max):
        if i < int(float(loc.iloc[0,0])) or (i > int(float(loc.iloc[0,1])) and i < int(float(loc.iloc[1,0]))) or (i > int(float(loc.iloc[1,1])) and i < int(float(loc.iloc[2,0]))) or i > int(float(loc.iloc[2,1])):
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

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, shuffle=False) # Split data for test and training
    SC = StandardScaler()
    x_train = pd.DataFrame(SC.fit_transform(x_train))
    x_test = pd.DataFrame(SC.transform(x_test))

    print("fit model")
    model = xgb.XGBClassifier(n_estimators=100, objective='binary:logistic',
        eval_metric='logloss', subsample=0.6, max_depth=3, learning_rate=0.1, colsample_bytree=1.0)
    model.fit(x_train, y_train)

    print("save model")
    gen_model = False
    with sql.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute(f"INSERT INTO models (patient_id, model_path) VALUES {patient_id, get_data_path(DATABASE) + f'p{patient_id}_model.json'}")
        model.save_model(get_data_path(DATABASE) + f"p{patient_id}_model.json")
        
        cur.execute(f"SELECT * FROM models WHERE patient_id = -1")
        general_model = cur.fetchall()
        if not general_model:
            cur.execute(f"INSERT INTO models (patient_id, model_path) VALUES {-1, get_data_path(DATABASE) + f'general_model.json'}")
            model.save_model(get_data_path(DATABASE) + f'general_model.json')
            gen_model = True
        cur.close()

    labels = predict_events(DATABASE, model, patient_id, week, night_id, recorder)
    if (not labels) or (len(labels) < 1):
        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            params = (patient_id)
            query = "DELETE FROM models WHERE patient_id=?"
            cur.execute(query, params)
            # cur.execute(f"DELETE FROM models WHERE patient_id={patient_id}")
            if gen_model:
                cur.execute(f"DELETE FROM models WHERE patient_id=-1")

    return labels


"""TODO: check prediction length, save 0 predictions """
def predict_events(DATABASE, model, patient_id, week, night_id, recorder):
    print("predict_events")
    original_sampling = get_original_sampling(DATABASE)
    selected_sampling =get_selected_sampling(DATABASE)
    data = open_brux_csv(DATABASE, patient_id, week, night_id, recorder)
    cycle_num = int(np.ceil(data.shape[0] / original_sampling / 90 / 60))
    
    selected = get_selected_intervals(patient_id, week, night_id, DATABASE)
    # print(selected[0]['start_id'])
    # print(selected[0][0])
    df = pd.DataFrame()
    for i in range(len(selected)):
        df = df._append(data.iloc[selected[i]['start_id']:selected[i]['end_id'],:])
    index = df.index
    # print(index)

    # df = resample_whole_df(df,original_sampling,selected_sampling)
    MR = get_column_array(get_column_data_from_df(df, "MR"))
    ML = get_column_array(get_column_data_from_df(df, "ML"))
    MR = resample_signal(signal=MR, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    ML = resample_signal(signal=ML, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    df = pd.DataFrame({'MR': MR, 'ML': ML})

    index = resample_signal(signal=index, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    print(index[:10])

    x = df.iloc[:,:2].copy()
    x_p = np.array(x.values.tolist())
    y_p = model.predict(x_p)
    y_p_mix = []
    i = 0
    event = 0
    loc_end = 0
    print(len(y_p))
    with sql.connect(DATABASE) as con:
        cur = con.cursor()
        loc_start = 0
        loc_end = 0
        while i < len(y_p):
            y_sum = y_p[i];
            cnt = 1;
            for j in range(1, 5*selected_sampling+1):
                if(i+j >= len(y_p) or ((index[i+j] - index[i])>5*original_sampling)):
                    # print("dur:", cnt/selected_sampling)
                    break;
                y_sum += y_p[i+j];
                cnt += 1;
            if y_sum/cnt >= 0.6:
                if(loc_start == 0 or loc_end-loc_start > 55*selected_sampling):
                    event += 1
                    loc_start = i
                    loc_end = i+cnt-1
                    location_begin = index[i]
                    location_end = index[loc_end]
                    params = (patient_id, week, night_id, recorder, event, location_begin, location_end, i, loc_end)
                    print(params)
                    query = "INSERT INTO predicted_labels (patient_id, week, night_id, recorder, label_id, location_begin, location_end, start_index, end_index) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    cur.execute(query, params)
                    
                    cycle = np.floor(location_begin / 90 / 60 / original_sampling);
                    params = (patient_id, week, night_id, cycle)
                    query = "SELECT count,type from week_summary WHERE (patient_id=? AND week=? AND night_id=? AND cycle=?)"
                    cur.execute(query, params)
                    count = cur.fetchall()
                    if count:
                        # print(count[0][0])
                        if cycle < cycle_num/2:
                            type_ind = 0
                        else:
                            type_ind = count[0][1] + 1
                        params = (count[0][0]+1, type_ind, patient_id, week, night_id, cycle)
                        query = "UPDATE week_summary SET count = ?, type = ? WHERE (patient_id=? AND week=? AND night_id=? AND cycle=?)"
                        cur.execute(query, params)
                    else:
                        if cycle < cycle_num/2:
                            type_ind = 0
                        else:
                            type_ind = 1
                        params = (patient_id, week, night_id, cycle, cycle_num, 1, type_ind)
                        query = "INSERT INTO week_summary (patient_id, week, night_id, cycle, max_cycle, count, type) VALUES (?, ?, ?, ?, ?, ?, ?)"
                        cur.execute(query, params)
                    print("current end idx:", location_end)
                elif(y_p_mix[-1] == 10):
                    loc_end += cnt-1
                    params = (index[loc_end], loc_end, patient_id, week, night_id, recorder, event)
                    query = "UPDATE predicted_labels SET location_end = ?, end_index = ? WHERE (patient_id=? AND week=? AND night_id=? AND recorder=? AND label_id=?)"
                    cur.execute(query, params)
                    print("update end:", loc_end)
                    print("update end idx:", index[loc_end])
                y_p_mix.extend([10]*cnt);
            else:
                loc_start = 0
                y_p_mix.extend([0]*cnt);
            i += cnt;
            # print(i)
        # print(event)
        params = (patient_id, week, night_id, recorder)
        query = "SELECT DISTINCT * from predicted_labels WHERE (patient_id=? AND week=? AND night_id=? AND recorder=?)"
        labels = cur.execute(query, params).fetchall()
    return labels


def run_prediction(DATABASE, patient_id, week, night_id, recorder):
    print("run_prediction")
    try:
        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            params = (patient_id, week, night_id, recorder)
            query = "SELECT DISTINCT * from predicted_labels WHERE (patient_id=? AND week=? AND night_id=? AND recorder=?)"
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
            labels = predict_events(DATABASE, xgbc, patient_id, week, night_id, recorder)
        else:
            # init_model_path =  get_data_path(DATABASE)+'models/initial/p'+str(patient_id)+'_model.json'
            cur_dir = os.path.dirname(os.path.abspath(__file__))
            init_model_path = './models/initial/p'+str(patient_id)+'_model.json'
            init_general_model_path = './models/initial/general_model.json'
            
            init_model_path = os.path.abspath(init_model_path)
            init_general_model_path = os.path.abspath(init_general_model_path)
            print('init_model_path: ',init_model_path)
            print('init_general_model_path', init_general_model_path)
            
            if os.path.exists(init_model_path):
                print("Initial Model exists")
                shutil.copy2(init_model_path, get_data_path(DATABASE))
                model_path = get_data_path(DATABASE) + f"p{patient_id}_model.json"

                with sql.connect(DATABASE) as con:
                    cur = con.cursor()
                    cur.execute(f"INSERT INTO models (patient_id, model_path) VALUES {patient_id, model_path}")
                    cur.execute(f"SELECT * FROM models WHERE patient_id= -1")
                    model = cur.fetchall()
                    if not model:
                        if os.path.exists(init_general_model_path):
                            print("General model exists")
                            init_model_path = init_general_model_path
                        shutil.copy2(init_model_path, get_data_path(DATABASE) + f"general_model.json")
                        cur.execute(f"INSERT INTO models (patient_id, model_path) VALUES {-1, get_data_path(DATABASE) + f'general_model.json'}")
                    cur.close()
                
                xgbc = xgb.XGBClassifier()
                xgbc.load_model(init_model_path)
                labels = predict_events(DATABASE, xgbc, patient_id, week, night_id, recorder)
            else:
                print("Model does not exist")
                labels = generate_model(DATABASE, patient_id, week, night_id, recorder)
            # predict_events(DATABASE, model,patient_id, week, night_id, recorder)
        
        return labels
    except Exception as e:
            print('Exception raised in run_prediction function')
            print(e)
            return f"{e}", 500


def run_confirmation(DATABASE, model_path, patient_id, week, night_id, recorder, study):
    original_sampling = get_original_sampling(DATABASE)
    selected_sampling = get_selected_sampling(DATABASE)
    data = open_brux_csv(DATABASE, patient_id, week, night_id, recorder)
    
    if (not study) or (not 'Bites' in data.columns):
        with sql.connect(DATABASE) as con:
            print("DB connected")
            cur = con.cursor()
            cur.execute(f"SELECT * FROM confirmed_labels WHERE patient_id={patient_id} AND week='{week}' AND night_id='{night_id}'")
            labels = cur.fetchall()
            cur.close()
        print(labels)
        bites = np.zeros(data.shape[0], dtype=int)
        print("label bites")
        for label in labels:
            for i in range(label[6], label[7]):
                bites[i] = 1
        print("add bites")
        data['Bites'] = bites
    
        print("save data")
        data.to_csv(get_data_path(DATABASE) + f"p{patient_id}_wk{week}/{night_id}{recorder}Fnorm.csv", encoding='utf-8', index=False)
    
    selected = get_selected_intervals(patient_id, week, night_id, DATABASE)
    df = pd.DataFrame()
    for i in range(len(selected)):
        df = df._append(data.iloc[selected[i]['start_id']:selected[i]['end_id'],:])
    
    MR = get_column_array(get_column_data_from_df(df, "MR"))
    ML = get_column_array(get_column_data_from_df(df, "ML"))
    bites = get_column_array(get_column_data_from_df(df, "Bites"))
    MR = resample_signal(signal=MR, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    ML = resample_signal(signal=ML, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    bites = resample_signal(signal=bites, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    # df.loc[:,'Bites'] = bites
    df = pd.DataFrame({'MR': MR, 'ML': ML, 'Bites': bites})

    x = df.iloc[:,:2].copy()
    y = df.iloc[:,-1].copy()
    x = np.array(x.values.tolist())
    y = np.array(y.values.tolist())

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, shuffle=False) # Split data for test and training
    SC = StandardScaler()
    x_train = pd.DataFrame(SC.fit_transform(x_train))
    x_test = pd.DataFrame(SC.transform(x_test))

    print("fit model")
    model = xgb.XGBClassifier(n_estimators=100, objective='binary:logistic',
    eval_metric='logloss', subsample=0.6, max_depth=3, learning_rate=0.1, colsample_bytree=1.0)
    print("load model: ", model_path)
    model.fit(x_train, y_train, xgb_model = model_path)

    print("save model")
    model.save_model(model_path)
    
    if study:
        p = -1
    else:
        p = patient_id
    
    return calc_model_accuracy(DATABASE, model, patient_id, week, night_id, recorder, p)


def false_positive(y_true, y_pred):
    # false positive
    return ((y_pred == 1) & (y_true == 0)).sum()


def false_negative(y_true, y_pred):
    # false negative
    return ((y_pred == 0) & (y_true == 1)).sum()


def true_positive(y_true, y_pred):
    # true positive
    return ((y_pred == 1) & (y_true == 1)).sum()


def true_negative(y_true, y_pred):
    # true negative
    return ((y_pred == 0) & (y_true == 0)).sum()


def calc_model_accuracy(DATABASE, model, patient_id, week, night_id, recorder, p):
    original_sampling = get_original_sampling(DATABASE)
    selected_sampling = get_selected_sampling(DATABASE)
    with sql.connect(DATABASE) as con:
        cur = con.cursor()
        # TODO: update path
        cur.execute(f"SELECT validation_file_path FROM models WHERE patient_id={patient_id}")
        # cur.execute(f"SELECT validation_file_path FROM models WHERE patient_id={p}")
        path = cur.fetchone()[0]
        cur.close()
    print(path)
    # file_path = get_data_path(DATABASE) + f"p{patient_id}_wk{week}/{night_id}{recorder}Fnorm.csv"
    # print(file_path)
    # if file_path == path:
    #     return {'accuracy': 0, 'precision': 0};
    print("get selected intervals")
    pp = re.search('/p(.*?)_', path).group(1)
    print('pp: ', pp)
    nn = re.search("/[0-9]+", path).group(0)
    if not nn[0].isnumeric():
        nn = nn[1:]
    print('nn: ', nn)
    ww = re.search('wk(.*)/', path).group(1)
    print('ww: ', ww)
    selected = get_selected_intervals(pp, ww, nn, DATABASE)
    
    print("open validation file")
    data = pd.read_csv(path)
    
    df = pd.DataFrame()
    for i in range(len(selected)):
        df = df._append(data.iloc[selected[i]['start_id']:selected[i]['end_id'],:])
    print("resample validation file")
    MR = get_column_array(get_column_data_from_df(df, "MR"))
    ML = get_column_array(get_column_data_from_df(df, "ML"))
    Bites = get_column_array(get_column_data_from_df(df, "Bites"))
    MR = resample_signal(signal=MR, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    ML = resample_signal(signal=ML, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    Bites = resample_signal(signal=Bites, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
    df = pd.DataFrame({'MR': MR, 'ML': ML, 'Bites': Bites})
    x = df.iloc[:,:2].copy()
    y = df.iloc[:,-1].copy()
    x = np.array(x.values.tolist())
    y = np.array(y.values.tolist())
    print("validation")
    scoring = {'accuracy' : make_scorer(accuracy_score), 
            'precision' : make_scorer(precision_score),
            'fn' : make_scorer(false_negative),
            'fp' : make_scorer(false_positive),
            'tp' : make_scorer(true_positive),
            'tn' : make_scorer(true_negative)
        #    'recall' : make_scorer(recall_score), 
        #    'f1_score' : make_scorer(f1_score)
           }
    cv = model_selection.KFold(n_splits=10, shuffle=True)
    accuracies = model_selection.cross_validate(estimator = model, X = x, y = y, cv = cv, scoring=scoring)
    print(accuracies)
    
    # TODO: add to db
    accuracy = np.floor(accuracies['test_accuracy'].mean()*10000)/100
    precision = np.floor(accuracies['test_precision'].mean()*10000)/100
    print('accuracy: ', accuracy)
    print('precision: ', precision)
    
    cm = np.array([[accuracies['test_tn'].mean(), accuracies['test_fp'].mean()], [accuracies['test_fn'].mean(), accuracies['test_tp'].mean()]])
    print('cm: ', cm)
    cmn = cm.astype('float') / cm.sum(axis=0)[np.newaxis,:]
    cmn = np.floor(cmn*10000)/100
    print('cmn 100: ', cmn)
    
    with sql.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute(f"UPDATE models SET accuracy={accuracy}, precision={precision} WHERE patient_id={p}")
        
        # cur.execute(f"SELECT location_begin, location_end FROM predicted_labels WHERE patient_id={patient_id} AND week={week} AND night_id={night_id}")
        # labels = cur.fetchall()
        
        # # TODO: can add day_no to log if need
        # # cur.execute(f"SELECT day_no FROM week_summary WHERE patient_id={patient_id} AND week={week} AND night_id={night_id}")
        # # day_no = cur.fetchone()[0]
        
        # p_bites = np.zeros(data.shape[0], dtype=int)
        # print("label bites")
        # for label in labels:
        #     print('label: ', label)
        #     for i in range(label[0], label[1]+1):
        #         p_bites[i] = 1
        # print("select bites")
        # p_bites = p_bites[df.index]
        # print("resample bites")
        # p_bites = resample_signal(signal=p_bites, sampling_rate=original_sampling, SAMPLING_RATE=selected_sampling)
        # print('p_bites: ', p_bites.shape)
        # print('Bites: ', Bites.shape)
        # cm = confusion_matrix(Bites, p_bites)
        # print('cm: ', cm)
        # cmn = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        # print('cmn: ', cmn)
        # cmn = cmn*100
        # print('cmn 100: ', cmn)
        if p == -1:
            week = patient_id
        cur.execute(f"INSERT INTO accuracy_log (patient_id, week, night_id, accuracy, precision, TN, FP, FN, TP) VALUES {p, week, night_id, accuracy, precision, cmn[0][0], cmn[0][1], cmn[1][0], cmn[1][1]}")
        cur.close()
    return {'accuracy': accuracy, 'precision': precision}


def return_img_stream(img_path):
    import base64
    img_stream = ''
    with open(img_path, 'rb') as img_f:
        img_stream = img_f.read()
        img_stream = base64.b64encode(img_stream).decode()
    return img_stream


"""Returns SSD values for the frontend heatmap for specific patient_id, week, night_id and recorder.
   If no data is available in the DB, it gets the HRV features from the SSD.py script, insert them into the DB, and returns them.
"""
def get_ssd_values(DATABASE, patient_id, week, night_id, recorder):
    with sql.connect(DATABASE) as con:
        print('connected to db', file=sys.stderr)
        cur = con.cursor()

        print('cur variable defined', file=sys.stderr)

        params = (patient_id, week, night_id, recorder)
        patient_exist = f"SELECT * FROM sleep_stage_detection WHERE (patient_id=? AND week=? AND night_id=? AND recorder=?)"
        print('patient_exist query', file=sys.stderr)

        if cur.execute(patient_exist, params).fetchall():
            print('EXIST', file=sys.stderr)
            params = (patient_id, week, night_id, recorder)
            query = "SELECT * FROM sleep_stage_detection WHERE (patient_id=? AND week=? AND night_id=? AND recorder=?)"
            result = cur.execute(query, params)
            columns = [description[0] for description in result.description]
            print(f"Columns: {columns}")
            values = get_json_format_from_query(columns=columns, query_results=result.fetchall(), start_id=1, end_id=10)

        else:
            print('DOES NOT EXIST', file=sys.stderr)
            print(patient_id, week, night_id)
            values = get_HRV_features(DATABASE, patient_id, week, night_id, recorder, get_original_sampling(DATABASE))

            for value in values:
                params = (patient_id, week, night_id, value['start_id'], value['end_id'], value['LF_HF'], value['SD'], value['stage'], value['y'], value['x'], 0, recorder)
                query = "INSERT INTO sleep_stage_detection (patient_id, week, night_id, start_id, end_id, LF_HF, SD, stage, y, x, selected, recorder) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                cur.execute(query, params)

        return values


"""Update the selected tiles on the heatmap, specifying patient_id, week, night_id, and updates.
   updates is a list of json in the form {'x': int, 'y': int}
"""
def post_selected_updates(DATABASE, patient_id, week, night_id, updates):
    with sql.connect(DATABASE) as con:
        print('connected to db', file=sys.stderr)
        cur = con.cursor()

        params = (patient_id, week, night_id)
        query = "UPDATE sleep_stage_detection SET selected = 0 WHERE patient_id=? AND week=? AND night_id=?"

        cur.execute(query, params)

        for update in updates:
            params = (patient_id, week, night_id, update["x"], update["y"])

            query = "UPDATE sleep_stage_detection SET selected = 1 WHERE patient_id=? AND week=? AND night_id=? AND x=? AND y=?"
            cur.execute(query, params)


"""Returns the selected tiles specifying patient_id, week, and night_id"""
def get_selected_phases(DATABASE, patient_id, week, night_id):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        params = (patient_id, week, night_id, 1)

        query = ("SELECT x,y,ROUND(SD),stage, LF_HF FROM sleep_stage_detection WHERE patient_id=? AND week=? AND night_id=? AND selected=?")

        selected = cur.execute(query, params).fetchall()

        result = [list(s) for s in selected]


        return result
        #return get_json_format_from_query(columns=columns, query_results=selected.fetchall(), start_id=0, end_id=1)


"""Gets the standard selected phases for specific patient on specific week and night_id. The standard selection are the 5-min intervals, whose the standard deviation falls between the range of the Herzig et al. study."""
def get_standard_selected_phases(DATABASE, patient_id, week, night_id):
    print("standard selected phases")
    SDNNmin = get_herzig_ranges()['SSDNRem']['min']
    SDNNmax = get_herzig_ranges()['SSDNRem']['max']
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        params = (patient_id, week, night_id, 'rem', SDNNmin, SDNNmax)

        query = ("SELECT x,y,ROUND(SD),stage, LF_HF FROM sleep_stage_detection WHERE patient_id=? AND week=? AND night_id=? AND stage=? AND (SD BETWEEN ? AND ?)")

        selected = cur.execute(query, params).fetchall()

        result = [list(s) for s in selected]


        return result


"""Get all the patients, weeks and night ids"""
def get_existing_patients_data(DATABASE):
    existing_patients_recordings = []

    for folder in os.listdir(get_data_path(DATABASE)):
        if not os.path.isdir(get_data_path(DATABASE) + folder):
            continue
        if not re.search('p(.*?)_', folder):
            continue
        patient_id = re.search('p(.*?)_', folder).group(1)

        patient_week_folder = get_data_path(DATABASE) + folder

        csv_files = [f for f in os.listdir(patient_week_folder) if f.endswith("Fnorm.csv")]

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


"""Returns activity duration stored in db"""
def get_activity_duration(DATABASE):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        activity_duration = cur.execute("SELECT activity_duration FROM settings WHERE id=1").fetchone()[0]
    
    return activity_duration


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


        return get_json_format_from_query(columns, settings.fetchall(), 1, 10)[0]


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

        params = (1, patient_id, week, night_id, start_id, end_id)
        query = "SELECT start_id, end_id FROM sleep_stage_detection WHERE selected=? AND patient_id=? AND week=? AND night_id=? and start_id>=? and end_id<=?"

        result = cur.execute(query, params)
        columns = [description[0] for description in result.description]

        return get_json_format_from_query(columns=columns, query_results=result.fetchall(), start_id=0, end_id=1)


"""Retrieve selected intervals from DB"""
def get_selected_intervals(patient_id, week, night_id, DATABASE):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        params = (1, patient_id, week, night_id)
        query = "SELECT start_id, end_id FROM sleep_stage_detection WHERE selected=? AND patient_id=? AND week=? AND night_id=?"

        result = cur.execute(query, params)
        columns = [description[0] for description in result.description]

        return get_json_format_from_query(columns=columns, query_results=result.fetchall(), start_id=0, end_id=1)


"""Retrieve REM intervals from DB"""
def get_rem_intervals(patient_id, week, night_id, DATABASE):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        params = ('rem', patient_id, week, night_id)
        query = "SELECT x,y,ROUND(SD),stage, LF_HF FROM sleep_stage_detection WHERE stage=? AND patient_id=? AND week=? AND night_id=?"

        rem = cur.execute(query, params).fetchall()
        
        result = [list(r) for r in rem]

        return result


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


"""Get the portion of data in which the event occurs."""
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

    if start_id == location_begin and end_id == location_end:
        print("Event has duration of whole 5 min chunk")
        
        mr_resampled = nk.signal_resample(mr, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()
        ml_resampled = nk.signal_resample(ml, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()
        new_event_resampled_subindices = location_begin, location_end

    elif start_id == location_begin:
        print("Special case- 5 minute start with event")
        
        mr_event_chunk = mr.values.tolist()[new_event_subindices[0]: new_event_subindices[1] + 1]
        mr_second_chunk = mr.values.tolist()[new_event_subindices[1]+1:]

        resmapled_mr_event_chunk =  nk.signal_resample(mr_event_chunk, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()
        resmapled_mr_second_chunk =  nk.signal_resample(mr_second_chunk, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()


        ml_event_chunk = ml.values.tolist()[new_event_subindices[0]: new_event_subindices[1] + 1]
        ml_second_chunk = ml.values.tolist()[new_event_subindices[1]+1:]

        resmapled_ml_event_chunk =  nk.signal_resample(ml_event_chunk, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()
        resmapled_ml_second_chunk =  nk.signal_resample(ml_second_chunk, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()

        mr_resampled = list(itertools.chain(resmapled_mr_event_chunk, resmapled_mr_second_chunk))
        ml_resampled = list(itertools.chain(resmapled_ml_event_chunk, resmapled_ml_second_chunk))

        new_event_resampled_subindices = find_sub_list(resmapled_mr_event_chunk, mr_resampled)

    elif end_id == location_end:
        print("Special case - 5 minute ends with event")

        mr_first_chunk = mr.values.tolist()[: new_event_subindices[0]]
        mr_event_chunk = mr.values.tolist()[new_event_subindices[0]: new_event_subindices[1] + 1]

        ml_first_chunk = ml.values.tolist()[: new_event_subindices[0]]
        ml_event_chunk = ml.values.tolist()[new_event_subindices[0]: new_event_subindices[1] + 1]

        resmapled_mr_first_chunk =  nk.signal_resample(mr_first_chunk, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()
        resmapled_mr_event_chunk =  nk.signal_resample(mr_event_chunk, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()

        resmapled_ml_first_chunk =  nk.signal_resample(ml_first_chunk, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()
        resmapled_ml_event_chunk =  nk.signal_resample(ml_event_chunk, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()

        mr_resampled = list(itertools.chain(resmapled_mr_first_chunk, resmapled_mr_event_chunk))
        ml_resampled = list(itertools.chain(resmapled_ml_first_chunk, resmapled_ml_event_chunk))

        new_event_resampled_subindices = find_sub_list(resmapled_mr_event_chunk, mr_resampled)

    else:
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
        
        # Find event indices of the new resampled data
        new_event_resampled_subindices = find_sub_list(resmapled_mr_event_chunk, mr_resampled)
    
    cnt = nk.signal_resample(cnt, method="interpolation", sampling_rate=original_sampling, desired_sampling_rate=selected_sampling).tolist()

    result = {
        #TODO: rename 5 min start and end id
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


def heatmap(data, col_labels, row_labels, ax=None,
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
def generate_weekly_sum_img(DATABASE, img_local_path, patient_id, week):
    print("Generating weekly summary image")
    days = list(range(1, 8))
    data = None
    cycle_num = 7
    day_cnt = 0
    weeknum = int(week.split('-')[0]) - 1
    print("weeknum: ",weeknum)
    with sql.connect(DATABASE) as con:
        print("DB connected")
        cur = con.cursor()
        params = (patient_id, week)
        query = "SELECT DISTINCT night_id from week_summary WHERE (patient_id=? AND week=?) ORDER BY night_id ASC;"
        nights = cur.execute(query, params).fetchall()
        print(nights)
        query = "SELECT max(max_cycle) from week_summary WHERE (patient_id=? AND week=?)"
        params = (patient_id, week)
        max_cycle = cur.execute(query, params).fetchone()[0]
        print(max_cycle)
        
        for i in nights:
            # print(i[0])
            params = (patient_id, week, i[0])
            query = "SELECT max_cycle, cycle, count from week_summary WHERE (patient_id=? AND week=? AND night_id=?)"
            cycle_count = cur.execute(query, params).fetchall()
            night_summary = np.zeros(max_cycle, dtype=int)
            cycle_num = max_cycle
            day_no = weeknum*7 + day_cnt
            print("day no: ", day_no)
            for j in cycle_count:
                # print(j)
                night_summary[j[1]] = j[2]
                params = (day_no, patient_id, week, i[0], j[1])
                query = "UPDATE week_summary SET day_no = ? WHERE (patient_id=? AND week=? AND night_id=? AND cycle=?)"
                cur.execute(query, params)
            print(night_summary)
            if(day_cnt == 0):
                data = night_summary
            else:
                data = np.vstack((np.array(data), np.array(night_summary)))
            
            day_cnt += 1
            
        # cur.close()
    
    # data = np.array([[1,0,0,0,0,0,0],
    #             [2,1,0,3,3,0,2],
    #             [1,3,0,0,0,1,0],
    #             [0,0,0,0,0,0,0],
    #             [1,1,0,0,4,2,0],
    #             [7,0,0,0,0,0,0],
    #             [5,1,0,0,0,0,0]])
        while(day_cnt < 7):
            data = np.vstack((np.array(data), np.zeros(cycle_num, dtype=int)))
            day_cnt += 1
        data = np.array(data).transpose()
        cycles = list(range(1, cycle_num + 1))
        print(data)
        print(cycles)
        fig, ax = plt.subplots()

        im = heatmap(data, days, cycles, ax=ax,
                        cmap="YlOrRd")
        # texts = annotate_heatmap(im, valfmt="{x:d}")

        # ax.set_title("Weekly Events Detected for Patient")
        fig.tight_layout()
        plt.savefig(img_local_path)
        print("Image saved")


"""Generate night prediction image"""
def generate_night_pred_img(DATABASE, patient_id, week, night_id, recorder):
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
        query = "SELECT DISTINCT * from confirmed_labels WHERE (patient_id=? AND week=? AND night_id=?)"
        cur = con.cursor()
        predicted_labels = cur.execute(query, params)
        if predicted_labels.fetchall() == None or len(predicted_labels.fetchall()) == 0:
            query = "SELECT DISTINCT * from predicted_labels WHERE (patient_id=? AND week=? AND night_id=?)"
            predicted_labels = cur.execute(query, params)
        columns = [description[0] for description in predicted_labels.description]
        print(columns)
        #df = get_patients_recordings_df(columns, patient_data.fetchall())
        predicted_labels_json = get_json_format_from_query(columns=columns, query_results=predicted_labels.fetchall(), start_id=1, end_id=9)
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
    # ax.plot(X, x_p[:,0],color='r',alpha=0.3, label='MR')
    ax.plot(X, x_p[:,0],color='#FF5454',alpha=0.8, label='MR')
    print("print MR")
    # ax.plot(X, x_p[:,1],color='b',alpha=0.3, label='ML')
    ax.plot(X, x_p[:,1],color='#4B7CFF',alpha=0.8, label='ML')
    print("print ML")
    # ax.plot(X, y_p_mix[:],color='g',alpha=0.6,linewidth=4, label='Predicted Brux')
    ax.plot(X, y_p_mix[:],color='#585858',alpha=0.8,linewidth=4, label='Predicted Brux')
    print("print predicted")
    neg_pred = [-x for x in y_p_mix]
    # ax.plot(X, neg_pred[:],color='g',alpha=0.6,linewidth=4)
    ax.plot(X, neg_pred[:],color='#585858',alpha=0.8,linewidth=4)
    if(y_p_mix[0] == 10):
        # ax.vlines(x=0, ymin=-10, ymax=10, color='g',alpha=0.6,linewidth=4)
        ax.vlines(x=0, ymin=-10, ymax=10, color='#585858',alpha=0.8,linewidth=4)
    if(y_p_mix[-1] == 10):
        # ax.vlines(x=X[-1], ymin=-10, ymax=10, color='g',alpha=0.6,linewidth=4)
        ax.vlines(x=X[-1], ymin=-10, ymax=10, color='#585858',alpha=0.8,linewidth=4)
    ax.legend(loc='upper left', fontsize=20)
    ax.set_ylim(-11,11)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude (mV)')
    plt.savefig(week_path+str(night_id)+'.png',bbox_inches='tight')
    # best_xgb.save_model("p1.json")
