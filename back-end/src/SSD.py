import pandas as pd 
import matplotlib.pyplot as plt
import datetime, math
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
    print(f"Indices of nan values 1: {np.argwhere(np.isnan(clean_rri))}")
    clean_rri = hrvana.interpolate_nan_values(rr_intervals=clean_rri, interpolation_method="linear")
    clean_rri = hrvana.remove_ectopic_beats(rr_intervals=clean_rri, method="malik")
    clean_rri = hrvana.interpolate_nan_values(rr_intervals=clean_rri, interpolation_method="linear")
    print(f"Indices of nan values 2: {np.argwhere(np.isnan(clean_rri))}")
    # If there are still nan values, remove them with further interpolation
    clean_rri = np.array(clean_rri)
    nans, x= nan_helper(clean_rri)
    clean_rri[nans]= np.interp(x(nans), x(~nans), clean_rri[~nans])
    print("check for null values in cleaned rri intervals")
    print(np.isnan(clean_rri).any())

    return clean_rri.tolist()
    #return clean_rri


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

def get_HRV_features(patient_id, week, night_id,  SAMPLING_RATE):
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

    # Open right CSV file and get ECG data
    df = open_brux_csv(patient_id, week, night_id)
    print(f"dfshape: {df.shape}")
    ecg = df["ECG"]
    ecg_array = ecg.values.tolist()
    print(f"last element: {ecg_array[-1]}")
    print(f" ECG Array length: {len(ecg)}")


    print(f"ECG Array duration: {datetime.timedelta(seconds=(len(ecg_array)/SAMPLING_RATE))}")


    print(f"ECG Array duration in minutes: {(datetime.timedelta(seconds=(len(ecg_array)/SAMPLING_RATE))).total_seconds()/60}")

    signal_duration_minutes = (datetime.timedelta(seconds=(len(ecg_array)/SAMPLING_RATE))).total_seconds() / 60
        
    n = math.floor(signal_duration_minutes)

    while n%5!=0:
        n = n-1

    print(f"Adapted minutes duration: {n}")

    data_points = n*60*SAMPLING_RATE
    print(f"New number of data points: {data_points}")
    ecg_nmin = ecg_array[:data_points]
    print(f"rounded down array length: {len(ecg_nmin)}")
    print(f"last element: {ecg_nmin[-1]}")

    print(f"Adapted Signal duration: {datetime.timedelta(seconds=(len(ecg_nmin)/SAMPLING_RATE))}")

    while end <= len(ecg_nmin):
        print("Beginning of while loop")
        print(f"end:{end}")
        print(f"length of data: {len(ecg_nmin)}")
        stage = ''

        # 5 minutes of ecg data
        ecg = ecg_nmin[start:end]

        print(f"5 minutes of data: {len(ecg)}")
        print(f"last element of the 5 minutes: {ecg[-1]}")

        # Filter the data with ranges specified from Barbara
        filter_ecg = nk.signal_filter(ecg, sampling_rate=SAMPLING_RATE, lowcut=0.5, highcut=150)


        # Clean ECG data
        cleaned = nk.ecg_clean(filter_ecg, sampling_rate=SAMPLING_RATE, method="pantompkins1985")

        print(f"cleaned isna(): {np.isnan(cleaned).any()}")

        #Find RR intervals    
        hrv_df = find_rr_intervals(cleaned)

        # Clean RR intervals

        clean_rri = clean_rr_intervals(hrv_df)
        hrv_df["RR Intervals"] = clean_rri 

        # HRV feature extraction
        nn_epoch = hrv_df['RR Intervals'].values

        print(type(nn_epoch))

        print(f"are there nullvalues: {hrv_df['RR Intervals'].isna().any()}")

        time_features = hrvana.get_time_domain_features(nn_epoch)
        print(f"time_features: {time_features}")
        frequency_features = hrvana.get_frequency_domain_features(nn_epoch)
        print(f"frequency features: {frequency_features}")

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

        print(f"values appended: {values[-1]}")
        # Calculate the coordinates for the SleepHeatMap.vue
        if x==((SLEEP_CYCLE/INTERVAL)-1):
            x=0
            y+=1

        else:
            x+=1

        start = end
        end += window_size
        print(f"start after increase: {start}")
        print(f"end after increase: {end}")

    return values