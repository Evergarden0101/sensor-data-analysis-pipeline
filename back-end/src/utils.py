import sqlite3 as sql
from settings import *
from preprocessing import *
from SSD import *
import sys

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
def get_patient_time_values(night_id):
        day = night_id[:2]
        hours = night_id[2:4]
        minutes = night_id[4:6]
        seconds = night_id[6]

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
def retrieve_patient_recording(DATABASE, patient_id, week, day, range_min):
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
            

"""Insert label for a specific patient in the Database"""
def insert_label(DATABASE, label):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute(f"INSERT INTO labels (patient, location_begin, location_end, duration) VALUES {label}")


def get_ssd_values(DATABASE, patient_id, week, night_id):
    day, hours, minutes, seconds = get_patient_time_values(night_id)
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
    
def post_ssd_updates(DATABASE, updates):
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