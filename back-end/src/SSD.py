import pandas as pd 
import matplotlib.pyplot as plt
import datetime
import neurokit2 as nk
import hrvanalysis as hrvana
from preprocessing import *
from settings import *


# FUNCTIONS

"""Take cleaned ecg as input and return RR intervals"""
def find_rr_intervals(cleaned_ecg):
    pantompkins1985 = nk.ecg_findpeaks(cleaned_ecg, method="pantompkins1985") # find the R peaks
    hrv_df = pd.DataFrame(pantompkins1985)
    hrv_df["RR Intervals"] = hrv_df["ECG_R_Peaks"].diff() # calculate the value difference between two adjacent points
    hrv_df.loc[0, "RR Intervals"]=hrv_df.loc[0]['ECG_R_Peaks'] # the first datapoint contain Nan 

    return hrv_df


"""Take the RR intervals and returns a cleaned version of them"""
def clean_rr_intervals(hrv_df):
    clean_rri = hrv_df['RR Intervals'].values
    clean_rri = hrvana.remove_outliers(rr_intervals=clean_rri, low_rri=300, high_rri=2000)
    clean_rri = hrvana.interpolate_nan_values(rr_intervals=clean_rri, interpolation_method="linear")
    clean_rri = hrvana.remove_ectopic_beats(rr_intervals=clean_rri, method="malik")
    clean_rri = hrvana.interpolate_nan_values(rr_intervals=clean_rri, interpolation_method="linear")

    return clean_rri


"""Return the REM and NREM LF/HF ranges from: Herzig et al., Reproducibility of Heart Rate Variability Is Parameter and Sleep Stage Dependent (2017).
    All the values as a reference:
    stage_2 = {'min': 0.68, 'median': 1.11, 'max': 2.02}
    sws = {'min': 0.31 , 'median': 0.51, 'max': 0.90}
    nrem = {'min': 0.31, 'median': (2.02-0.31)/2 , 'max': 2.02}
    rem = {'min': 1.30, 'median': 2.02 , 'max': 3.22}
"""
def get_herzig_ranges():
    return {
        'nrem': {'min': 0.31, 'median': (2.02-0.31)/2 , 'max': 2.02},
        'rem' : {'min': 1.30, 'median': 2.02 , 'max': 3.22}
    }


"""Return REM and NREM LF/HF ranges from: Ako et al., Correlation between electroencephalography and heart rate variability during sleep (2003)
    All the values as a reference:
    stage_1 = {'min': 2.30-0.29, 'median': 2.30, 'max': 2.30+0.29}
    stage_2 = {'min': 1.85-0.09 , 'median': 1.85 , 'max': 1.85+0.09}
    stage_3 = {'min': 0.78-0.06 , 'median': 0.78, 'max': 0.78+0.06}
    stage_4 = {'min': 0.86-0.14, 'median': 0.86, 'max': 0.86+0.14}
    rem = {'min': 2.51-0.17, 'median': 2.51, 'max': 2.51+0.17}
"""
def get_ako_ranges():
    return {
        'nrem': {'min':0.72, 'median': (2.59-0.72)/2, 'max': 2.59},
        'rem': {'min': 2.51-0.17, 'median': 2.51 , 'max': 2.51+0.17}
    }


# COMPLETE PIPELINE FUNCTION
"""
- patient_id: id of the patient
- week: week number
- night_id: id of the night that specifies which file to open 
- n: first n minutes of data are selected
- SAMPLING_RATE: desired sampling rate (default: 1000)
"""

def get_HRV_features(patient_id, week, night_id, n,  SAMPLING_RATE=SAMPLING_RATE):
    start = 0
    # Number of data points in 5 minutes
    window_size = INTERVAL*60*SAMPLING_RATE
    end = window_size
    values = []
    y=0
    x=0
    
    # Open right CSV file and get ECG data
    df = open_brux_csv(patient_id=patient_id, week=week, night_id=night_id)
    ecg = get_column_data_from_df(df, "ECG")
    ecg_array = get_column_array(ecg)

    # Downsample to 1000Hz
    ecg_ds = resample_signal(signal=ecg_array)

    # Select first n minutes
    ecg_nmin = get_n_minutes(ecg_ds, n, SAMPLING_RATE=SAMPLING_RATE)
    print(f"Signal duration: {get_signal_duration(ecg_nmin)}")
    

    while end <= len(ecg_nmin)+1:
        stage = ''

        # 5 minutes of ecg data
        ecg = ecg_nmin[start:end]

        # Filter the data with ranges specified from Barbara
        filter_ecg = nk.signal_filter(ecg, sampling_rate=SAMPLING_RATE, lowcut=0.5, highcut=150)

        # Clean ECG data
        cleaned = nk.ecg_clean(filter_ecg, sampling_rate=SAMPLING_RATE, method="pantompkins1985")

        #Find RR intervals    
        hrv_df = find_rr_intervals(cleaned)

        # Clean RR intervals
    
        clean_rri = clean_rr_intervals(hrv_df)
        hrv_df["RR Intervals"] = clean_rri 

        # HRV feature extraction
        nn_epoch = hrv_df['RR Intervals'].values

        time_features = hrvana.get_time_domain_features(nn_epoch)
        frequency_features = hrvana.get_frequency_domain_features(nn_epoch)

        print(f"LF/HF ratio: {frequency_features['lf_hf_ratio']}")
        nrem = get_herzig_ranges()['nrem']
        rem = get_herzig_ranges()['rem']

        if  nrem['min'] <= frequency_features['lf_hf_ratio'] <= nrem['max']:
            stage = 'nrem'

        if frequency_features['lf_hf_ratio'] < nrem['min']:
            stage = 'nrem'

        if rem['min'] <= frequency_features['lf_hf_ratio'] <= rem['max']:
            stage = 'rem'

        if frequency_features['lf_hf_ratio'] > rem['max']:
            stage = 'rem'

        values.append({
            'start_id': start,
            'end_id': end,
            'LF_HF': frequency_features['lf_hf_ratio'],
            'SD': time_features['sdnn'],
            'stage': stage,
            'y': y,
            'x': x
        })

        # Calculate the coordinates for the SleepHeatMap.vue
        if x==((SLEEP_CYCLE/INTERVAL)-1):
            x=0
            y+=1

        else:
            x+=1

        start = end
        end += window_size
    
    return values