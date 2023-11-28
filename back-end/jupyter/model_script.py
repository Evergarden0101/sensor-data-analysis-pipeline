#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import xgboost as xgb
import neurokit2 as nk
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import re
import os


# In[2]:


DATA_PATH = '/srv/scratch3/bruxit/bruxit_all_fnorm/'
# DATA_PATH = "/Users/nanashuka/Document/Zurich/UZH/master_project/sensor-data-analysis-pipeline/back-end/data/"
original_sampling = 2000
selected_sampling = 1000


# In[3]:


def resample_signal(signal, sampling_rate=2000, selected_sampling=1000):
    return nk.signal_resample(signal, sampling_rate=sampling_rate, desired_sampling_rate=selected_sampling, method="pandas")


# In[5]:


existing_patients_recordings = {}
for folder in os.listdir(DATA_PATH):
        if not os.path.isdir(DATA_PATH + folder):
            continue
        if not re.search('p(.*?)_', folder):
            continue
        patient_id = re.search('p(.*?)_', folder).group(1)

        patient_week_folder = DATA_PATH + folder

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
                if patient_id in existing_patients_recordings:
                    existing_patients_recordings[patient_id].append({
                        "week": week,
                        "night_id": night_id,
                        "recorder": night_id_recorder[night_id]
                    })
                else:
                    existing_patients_recordings[patient_id] = [{
                        "week": week,
                        "night_id": night_id,
                        "recorder": night_id_recorder[night_id]
                    }]
print(existing_patients_recordings)


# In[8]:


general_model = xgb.XGBClassifier(n_estimators=100, objective='binary:logistic',
        eval_metric='logloss', subsample=0.6, max_depth=3, learning_rate=0.1, colsample_bytree=1.0)
first = True
for patient_id, recordings in existing_patients_recordings.items():
    print("Patient: ", patient_id)
    patient_model = xgb.XGBClassifier(n_estimators=100, objective='binary:logistic',
        eval_metric='logloss', subsample=0.6, max_depth=3, learning_rate=0.1, colsample_bytree=1.0)
    df = pd.DataFrame({'MR': [], 'ML': [], 'Bites': []})
    for recording in recordings:
        try:
            week = recording["week"]
            night_id = recording["night_id"]
            recorder = recording["recorder"]
            print(f"p{patient_id}, wk{week}, {night_id}{recorder}")
            # Load data
            loc = pd.read_csv(DATA_PATH + "p" + patient_id + "_wk" + week + "/" + night_id + recorder + "location_Bites.csv")
            # data = pd.read_csv(DATA_PATH + "p" + patient_id + "_wk" + week + "/" + night_id + recorder + "Fnorm.csv")
            range_min = 0
            range_max = int(loc.iloc[2,1]) + 1
            dur_len = float(loc.iloc[0,2]) + float(loc.iloc[1,2]) + float(loc.iloc[2,2])
            if dur_len*original_sampling*2 > range_max:
                range_max = int(dur_len*2000*2)
            print('range_max: ', range_max)
            data_itr = pd.read_csv(f'{DATA_PATH}p{patient_id}_wk{week}/{night_id}{recorder}Fnorm.csv', chunksize=range_max, iterator=True, usecols=['MR','ML'])
            data = data_itr.get_chunk()
            print('data.shape: ', data.shape)
            # print('data: ', data.describe())
            
            bites = np.zeros(data.shape[0], dtype=int)
            data = data.dropna()
            # print('data.shape after drop: ', data.shape)
            print(f"label bites, wk{week}, {night_id}{recorder}")
            for i in range(0, data.shape[0]):
                if i < int(float(loc.iloc[0,0])) or (i > int(float(loc.iloc[0,1])) and i < int(float(loc.iloc[1,0]))) or (i > int(float(loc.iloc[1,1])) and i < int(float(loc.iloc[2,0]))) or i > int(float(loc.iloc[2,1])):
                    bites[i] = 0
                else:
                    bites[i] = 1
            bites = bites[data.index]
            MR = data['MR'].values.tolist()
            ML = data['ML'].values.tolist()
            if (len(bites) != len(MR)):
                print('/////////////////////////////////////')
                print('len(bites): ', len(bites))
                print('len(MR): ', len(MR))
                print('/////////////////////////////////////')
            # print('MR: ', MR[:10])
            # print('ML: ', ML[:10])
            MR = resample_signal(signal=MR, sampling_rate=original_sampling, selected_sampling=selected_sampling)
            ML = resample_signal(signal=ML, sampling_rate=original_sampling, selected_sampling=selected_sampling)
            bites = resample_signal(signal=bites, sampling_rate=original_sampling, selected_sampling=selected_sampling)
            # df.loc[:,'Bites'] = bites
            df_p = pd.DataFrame({'MR': MR, 'ML': ML, 'Bites': bites})
            print('df_p.shape: ', df_p.shape)
            print('df.shape: ', df.shape)
            # print('df: ', df_p.describe())
            
            df = df.append(df_p, ignore_index=True)
            print()
        except Exception as e:
            print(e)
            print()
            continue
    
    x = df.iloc[:,:2].copy()
    y = df.iloc[:,-1].copy()
    x = np.array(x.values.tolist())
    y = np.array(y.values.tolist())
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25) # Split data for test and training
    SC = StandardScaler()
    x_train = pd.DataFrame(SC.fit_transform(x_train))
    x_test = pd.DataFrame(SC.transform(x_test))
    print(f"fit model p{patient_id}")
    patient_model.fit(x_train, y_train)
    print(f"save model p{patient_id}")
    patient_model.save_model(DATA_PATH + '/models/' +f"p{patient_id}_model.json")

    print("fit general model")
    if first:
        general_model.fit(x_train, y_train)
        first = False
    else:
        general_model.fit(x_train, y_train, xgb_model=general_model)

general_model.save_model(DATA_PATH + '/models/' + "general_model.json")
print("save general model")

