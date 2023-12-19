# From Frasch, M. G. (2022). Comprehensive HRV estimation pipeline in Python using Neurokit2: Application to sleep physiology. MethodsX, 9, 101782.

import neurokit2 as nk
import pandas as pd
import numpy as np
from preprocessing import *


"""Return the REM and NREM LF/HF ranges from: Herzig et al., Reproducibility of Heart Rate Variability Is Parameter and Sleep Stage Dependent (2017).
    All the values as a reference:
    stage_2 = {'min': 0.68, 'median': 1.11, 'max': 2.02}
    sws = {'min': 0.31 , 'median': 0.51, 'max': 0.90}
    nrem = {'min': 0.31, 'median': (2.02-0.31)/2 , 'max': 2.02}
    rem = {'min': 1.30, 'median': 2.02 , 'max': 3.22}
"""
def get_herzig_ranges():
    return {
        'nrem': {'min': 0.31, 'median': (2.02+0.31)/2 , 'max': 2.02},
        'rem' : {'min': 1.30, 'median': 2.02 , 'max': 3.22},
        'SSDNRem': {'min': 82.6, 'median': 105.5, 'max': 134.7}
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

def compute_HRV(rpeaks_clean, sampling_rate=2000, window=5):    
    # Regular HRV matrix (from peaks)
    duration_peaks=rpeaks_clean[len(rpeaks_clean)-1] #gives me the duration in samples
    divider=duration_peaks/sampling_rate/60/window  #sampling_rate, 5 min window segments
    segment=np.array_split(rpeaks_clean,divider) #divide in segments of 5 min; the last segment may be shorter; discard during statistical analysis on HRV metrics

    hrv_final_df=pd.DataFrame()

    for i in range(len(segment)):
        hrv_segment = nk.hrv(segment[i], sampling_rate=sampling_rate, show=False)
        print(i)
        hrv_final_df = pd.concat([hrv_final_df, hrv_segment],ignore_index=True)


    return hrv_final_df


# Complete pipeline function
def get_HRV_features(DATABASE, patient_id, week, night_id, recorder, SAMPLING_RATE):
    start = 0
    print(f"start: {start}")
    # Number of data points in 5 minutes
    window_size = 5*60*SAMPLING_RATE
    print(f"window size: {window_size}")
    end = window_size
    print(f"end: {end}")
    values = []
    y=0
    x=0

    df = open_brux_csv(DATABASE, patient_id, week, night_id, recorder, columns=["ECG"])
    print(f"dfshape: {df.shape}")
    ecg = df["ECG"]

    # Filter the data with ranges specified from Barbara
    filter_ecg = nk.signal_filter(ecg, sampling_rate=SAMPLING_RATE, lowcut=0.5, highcut=150)

    # clean ecg signal
    ecg_cleaned = nk.ecg_clean(filter_ecg, sampling_rate=SAMPLING_RATE, method="pantompkins1985")

    # find r peaks
    rpeaks, info = nk.ecg_peaks(ecg_cleaned, sampling_rate=SAMPLING_RATE)

    # Trim trailing zeros
    rpeaks = np.trim_zeros(rpeaks,trim='b')

    # Artifact removal
    # nk.signal_fixpeaks saves the corrected peak locations to the [1] index of the output data sturcture
    # accessible like so: clean_peaks[1]
    rpeaks_clean=nk.signal_fixpeaks(rpeaks, sampling_rate=SAMPLING_RATE, iterative=False, show=False,interval_min=0.33,interval_max=0.75, method="kubios")

    rpeaks_clean = rpeaks_clean[1]

    hrv_final_df = compute_HRV(rpeaks_clean, sampling_rate=SAMPLING_RATE)

    for i, row in hrv_final_df.iterrows():
        print(row['HRV_LFHF'])
        nrem = get_herzig_ranges()['nrem']
        rem = get_herzig_ranges()['rem']


        if  nrem['min'] <= row['HRV_LFHF'] <= nrem['max']:
            stage = 'nrem'

        if row['HRV_LFHF'] < nrem['min']:
            stage = 'nrem'

        if rem['min'] <= row['HRV_LFHF'] <= rem['max']:
            stage = 'rem'

        if row['HRV_LFHF'] > rem['max']:
            stage = 'rem'

        values.append({
                'start_id': start,
                'end_id': end,
                'LF_HF': row['HRV_LFHF'],
                'SD': row['HRV_SDNN'],
                'stage': stage,
                'y': y,
                'x': x
            })

        if x==((90/5)-1):
            x=0
            y+=1

        else:
            x+=1
     

        start = end
        end += window_size
    
    return values




