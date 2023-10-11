import sqlite3 as sql
from settings import *
from preprocessing import *
from SSD2 import *
import sys, os, re
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use('agg')

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
            

"""Insert label for a specific patient in the Database"""
def insert_label(DATABASE, label):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute(f"INSERT INTO confirmed_labels (patient_id, week, night_id, label_id, location_begin, location_end, corrected) VALUES {label['patient_id'],label['week'],label['night_id'],label['label_id'],label['location_begin'],label['location_end'],label['corrected']}")

def run_prediction(DATABASE, patient_id, week, night_id):
    try:
        with sql.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM confirmed_labels WHERE patient_id={patient_id} AND week={week} AND night_id={night_id}")
            labels = cur.fetchall()

            if labels:
                return labels
            else:
                return "No labels for this patient"
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


def get_ssd_values(DATABASE, patient_id, week, night_id):
    day, hours, minutes, seconds = get_patient_time_values(night_id)
    with sql.connect(DATABASE) as con:
        print('connected to db', file=sys.stderr)
        cur = con.cursor()

        print('cur variable defined', file=sys.stderr)

        params = (patient_id, week, day, hours, minutes, seconds)
        patient_exist = f"SELECT * FROM sleep_stage_detection WHERE (patient_id=? AND week=? AND day=? AND hours=? AND minutes=? AND seconds=?)"
        print('patient_exist query', file=sys.stderr)

        if cur.execute(patient_exist, params).fetchall():
            print('EXIST', file=sys.stderr)
            params = (patient_id, week, day, hours, minutes, seconds)
            query = "SELECT * FROM sleep_stage_detection WHERE (patient_id=? AND week=? AND day=? AND hours=? AND minutes=? AND seconds=?)"
            result = cur.execute(query, params)
            columns = [description[0] for description in result.description]
            print(f"Columns: {columns}")
            values = get_json_format_from_query(columns=columns, query_results=result.fetchall(), start_id=1, end_id=14)
        
        else:
            print('DOES NOT EXIST', file=sys.stderr)
            print(patient_id, week, night_id)
            values = get_HRV_features(patient_id, week, night_id, 2000)

            for value in values:
                params = (patient_id, week, day, hours, minutes, seconds, value['start_id'], value['end_id'], value['LF_HF'], value['SD'], value['stage'], value['y'], value['x'], 0)
                query = "INSERT INTO sleep_stage_detection (patient_id, week, day, hours, minutes, seconds, start_id, end_id, LF_HF, SD, stage, y, x, selected) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
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
def get_existing_patients_data():
    existing_patients_recordings = []

    for folder in os.listdir(DATA_PATH):
        if not os.path.isdir(DATA_PATH + folder):
            continue
        patient_id = re.search('p(.*?)_', folder).group(1)

        patient_week_folder = DATA_PATH + folder

        csv_files = [f for f in os.listdir(patient_week_folder) if f.endswith(".csv")]

        night_id_list= []
        for csv in csv_files:
            night_id = re.search("[0-9]+", csv).group(0)
            night_id_list.append(night_id)

        if night_id_list:
            week = re.search('w(.*)', folder).group(1)
            night_id_list = list(set(night_id_list))
            night_id_list = sorted(night_id_list)
            
            for night_id in night_id_list:
                existing_patients_recordings.append({
                    "patient_id": patient_id,
                    "week": week,
                    "night_id": night_id

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
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        original_sampling = cur.execute("SELECT original_sampling FROM settings WHERE id=1").fetchone()[0]

    return original_sampling


"""Returns selected sampling rate stored in db"""
def get_selected_sampling(DATABASE):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        selected_sampling = cur.execute("SELECT selected_sampling FROM settings WHERE id=1").fetchone()[0]

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


        return get_json_format_from_query(columns, settings.fetchall(), 1, 8)[0]
    

"""Returns sensors stored in db as list of json"""
def get_sensors(DATABASE):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        sensors = cur.execute("SELECT * FROM sensors")
        columns = [description[0] for description in sensors.description]

        return get_json_format_from_query(columns, sensors.fetchall(), 1, 2)



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
def generate_weekly_sum_img(DATABASE, img_local_path):
    len = 74155516
    print(len)
    original_sampling = get_original_sampling(DATABASE)
    cycles = int(np.ceil(len / original_sampling / 60 / 60 / 1.5))
    stages = list(range(1, cycles + 1))
    days = list(range(1, 8))
    print(stages)
    print(days)
    data = np.array([[1,0,0,0,0,0,0],
                [2,1,0,3,3,0,2],
                [1,3,0,0,0,1,0],
                [0,0,0,0,0,0,0],
                [1,1,0,0,4,2,0],
                [7,0,0,0,0,0,0],
                [5,1,0,0,0,0,0]])
    fig, ax = plt.subplots()

    im = heatmap(data, days, stages, ax=ax,
                    cmap="YlOrRd")
    texts = annotate_heatmap(im, valfmt="{x:d}")

    # ax.set_title("Weekly Events Detected for Patient")
    fig.tight_layout()
    plt.savefig(img_local_path)