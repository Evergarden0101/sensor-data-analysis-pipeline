
import sqlite3 as sql
import pandas as pd 
import datetime
import neurokit2 as nk
import numpy as np


# FUNCTIONS
"""Returns data path stored in db"""
def get_data_path(DATABASE):
    with sql.connect(DATABASE) as con:
        cur = con.cursor()

        data_path = cur.execute("SELECT data_path FROM settings WHERE id=1").fetchone()[0]

    return data_path


"""Gets DATABASE, patient_id, week, recorder and night_id and return a pandas df of the specified patient dataset. If columns are specified, the opening is sped up."""
def open_brux_csv(DATABASE, patient_id, week, night_id, recorder, columns=[]):
    if columns:
        return pd.read_csv(get_data_path(DATABASE) + f"p{patient_id}_wk{week}/{night_id}{recorder}Fnorm.csv", usecols=columns)
    else:
        return pd.read_csv(get_data_path(DATABASE) + f"p{patient_id}_wk{week}/{night_id}{recorder}Fnorm.csv")


"""Gets DATABASE, patient_id, week, recorder and night_id and return a pandas df of the specified loc dataset."""
def open_brux_loc_csv(DATABASE, patient_id, week, night_id, recorder):
    return pd.read_csv(get_data_path(DATABASE) + f"p{patient_id}_wk{week}/{night_id}{recorder}location_Bites.csv")


"""Gets complete patient df and return only the specified column"""
def get_column_data_from_df(df, column_name):
    return df[column_name]


"""Gets one column dataframe and return the list of values"""
def get_column_array(df):
    return df.values.tolist()


"""Gets ECG list (default sampling rate: 2000) and resample the ECG signal to desired rate (default: 1000)"""
def resample_signal(signal, sampling_rate=2000, SAMPLING_RATE=1000):
    return nk.signal_resample(signal, sampling_rate=sampling_rate, desired_sampling_rate=SAMPLING_RATE, method="pandas")


"""Testing purposes: take only first n minutes of the signal list dataset"""
def get_n_minutes(signal, n, SAMPLING_RATE=2000):
    data_points = n*60*SAMPLING_RATE
    return signal[:data_points]


"""Takes ecg list and default sampling rate and returns the duration in hours, minutes and seconds"""
def get_signal_duration(signal, SAMPLING_RATE=2000):
    return datetime.timedelta(seconds=(len(signal)/SAMPLING_RATE))


"""Resample all the signals contained in the df"""
def resample_whole_df(df, sampling_rate=2000, SAMPLING_RATE=1000):
    column_names = list(df.columns)
    column_names.pop(-1)


    MR = get_column_array(get_column_data_from_df(df, "MR"))
    ML = get_column_array(get_column_data_from_df(df, "ML"))
    SU = get_column_array(get_column_data_from_df(df, "SU"))
    Microphone = get_column_array(get_column_data_from_df(df, "Microphone"))
    Eye = get_column_array(get_column_data_from_df(df, "Eye"))
    ECG = get_column_array(get_column_data_from_df(df, "ECG"))
    Pressure = get_column_array(get_column_data_from_df(df, "Pressure Sensor"))

    MR_resampled = resample_signal(signal=MR, sampling_rate=sampling_rate, SAMPLING_RATE=SAMPLING_RATE)
    ML_resampled = resample_signal(signal=ML, sampling_rate=sampling_rate, SAMPLING_RATE=SAMPLING_RATE)
    SU_resampled = resample_signal(signal=SU, sampling_rate=sampling_rate, SAMPLING_RATE=SAMPLING_RATE)
    Microphone_resampled = resample_signal(signal=Microphone, sampling_rate=sampling_rate, SAMPLING_RATE=SAMPLING_RATE)
    Eye_resampled = resample_signal(signal=Eye, sampling_rate=sampling_rate, SAMPLING_RATE=SAMPLING_RATE)
    ECG_resampled = resample_signal(signal=ECG, sampling_rate=sampling_rate, SAMPLING_RATE=SAMPLING_RATE)
    Pressure_resampled = resample_signal(signal=Pressure, sampling_rate=sampling_rate, SAMPLING_RATE=SAMPLING_RATE)

    df_resampled = pd.DataFrame({column_names[0]: MR_resampled,
                                 column_names[1]: ML_resampled,
                                 column_names[2]: SU_resampled,
                                 column_names[3]: Microphone_resampled,
                                 column_names[4]: Eye_resampled,
                                 column_names[5]: ECG_resampled,
                                 column_names[6]: Pressure_resampled})
    print(df_resampled)

    return df_resampled


def nan_helper(y):
    """Helper to handle indices and logical indices of NaNs.

    Input:
        - y, 1d numpy array with possible NaNs
    Output:
        - nans, logical indices of NaNs
        - index, a function, with signature indices= index(logical_indices),
          to convert logical indices of NaNs to 'equivalent' indices
    Example:
        >>> # linear interpolation of NaNs
        >>> nans, x= nan_helper(y)
        >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
    """

    return np.isnan(y), lambda z: z.nonzero()[0]