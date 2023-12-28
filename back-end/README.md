# API Design for the backend
### Divided by frontend components

## Home Page
## GET `/settings-exist/`
### Description
Check if settings already exist on DB.

### Responses

#### 200 OK
Return type: JSON object.

Example response:

```json
{
    "settings_exist": 1
}
```

#### 500 INTERNAL SERVER ERROR

Exception string.



## Settings Page

## GET `/settings/`
### Description
Get the general settings of the application.

### Responses

#### 200 OK
Return type: JSON object.

Example response:

```json
{
    "activity": "bruxism",
    "activity_duration": 30.0,
    "data_path": "C:/Users/eleon/Desktop/Master/FJS 23/Master Project/sensor-data-analysis-pipeline/back-end/src/data/",
    "dataset_format": "csv",
    "filtered": 1,
    "non_selected_sampling": 256,
    "normalized": 1,
    "original_sampling": 2000,
    "selected_sampling": 1000,
    "study_type": "sleep"
}
```

#### 500 INTERNAL SERVER ERROR

Exception string.


## GET `/sensors/`
### Description
Get the sensors of the application.

### Responses

#### 200 OK
Return type: list of JSON objects.


Example response:

```json
[
    {
        "name": "ECG",
        "type": "ECG"
    },
    {
        "name": "MR",
        "type": "EMG"
    },
    {
        "name": "ML",
        "type": "EMG"
    }
]
```


#### 500 INTERNAL SERVER ERROR

Exception string.



## POST `/settings/`
### Description
Post the general settings of the application.


### Payload
JSON object.


| Key | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `studyType`    | ✅        | string                                | -       |
| `activityType`    | ✅        | string | -       |
| `activityDuration`    | ✅        | string | -       |
| `originalSampling`    | ✅        | int                                | -       |
| `SelectedSampling`    | ✅        | int | -       |
| `NonSelectedSampling`    | ✅        | int | -       |
| `fileFormat`    | ✅        | string                                | -       |
| `filtered`    | ✅        | boolean | -       |
| `normalized`    | ✅        | boolean | -       |
| `dataPath`    | ✅        | string | -       |


Example payload:
```json
{
    "studyType": "Sleep",
    "activityType": "Bruxism",
    "activityDuration": 30.00,
    "originalSampling": 2000,
    "SelectedSampling": 1000,
    "NonSelectedSampling": 256,
    "fileFormat": "csv",
    "filtered": true,
    "normalized": true,
    "dataPath": "C:/Users/eleon/Desktop/Master/FJS 23/Master Project/sensor-data-analysis-pipeline/back-end/src/data/"
}
```


### Responses

#### 200 OK
Return type: string.

Example response:

```string
"Inserted settings into DB"
```

#### 500 INTERNAL SERVER ERROR

Exception string.


## POST `/sensors/`
### Description
Post the sensors of the application.


### Payload

List of JSON objects.


| Key | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `type`    | ✅        | string                                | -       |
| `name`    | ✅        | string | -       |



Example payload:
```json
[{
    "type": "ECG",
    "name": "ECG"
},{
    "type": "EMG",
    "name": "MR"
},{
    "type": "EMG",
    "name": "ML"
}]
```


### Responses

#### 200 OK
Return type: string.

Example response:

```string
"Inserted sensors into DB"
```

#### 500 INTERNAL SERVER ERROR

Exception string.


## Patient Data Page

## GET `/existing-patients-recordings/`
### Description
Get the patients recordings present in the dataPath folder specified in the settings.

### Responses

#### 200 OK
Return type: list of JSON objects.

Example response:

```json
[
    {
        "night_id": "0901260",
        "patient_id": "1",
        "recorder": "c",
        "week": "1"
    },
    {
        "night_id": "1022102",
        "patient_id": "1",
        "recorder": "c",
        "week": "1"
    },
    {
        "night_id": "0107285",
        "patient_id": "2",
        "recorder": "e",
        "week": "1-2"
    },
    {
        "night_id": "0123035",
        "patient_id": "2",
        "recorder": "e",
        "week": "1-2"
    }
]
```

#### 500 INTERNAL SERVER ERROR

Exception string.

## Filtering Page

## GET `/ssd/<int:patient_id>/<string:week>/<string:night_id>/<string:recorder>/`
### Description
Get the sleep stage detection data derived from the HRV analysis.

### Parameters

| Parameter | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `patient_id`    | ✅        | int                                | -       |
| `week`    | ✅        | string | -       |
| `night_id`    | ✅        | string | -       |
| `recorder`    | ✅        | string | -       |


### Responses

#### 200 OK
Return type: list of JSON objects.
Every object represents a 5-min interval.

Example response:

```json
[
    {
        "LF_HF": 1.6426161983559298,
        "SD": 76.57010847339781,
        "end_id": 600000,
        "night_id": "1022102",
        "patient_id": 1,
        "stage": "rem",
        "start_id": 0,
        "week": "1",
        "x": 0,
        "y": 0
    },
    {
        "LF_HF": 1.073289488257166,
        "SD": 76.44414531713261,
        "end_id": 1200000,
        "night_id": "1022102",
        "patient_id": 1,
        "stage": "nrem",
        "start_id": 600000,
        "week": "1",
        "x": 1,
        "y": 0
    },
    {
        "LF_HF": 1.7854041157820064,
        "SD": 47.784263999100894,
        "end_id": 1800000,
        "night_id": "1022102",
        "patient_id": 1,
        "stage": "rem",
        "start_id": 1200000,
        "week": "1",
        "x": 2,
        "y": 0
    },
]
```
#### 500 INTERNAL SERVER ERROR

Exception string.


## GET `/selected-sleep-phases/<int:patient_id>/<string:week>/<string:night_id>/`
### Description
Retrieve the selected sleep stages parameters from the DB.

### Parameters

| Parameter | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `patient_id`    | ✅        | int                                | -       |
| `week`    | ✅        | string | -       |
| `night_id`    | ✅        | string | -       |


### Responses

#### 200 OK
Return type: list of lists. A single list element is of the form `[x, y, ROUND(SD), stage, LF_HF]`.

Example response:

```json
[
    [
        0,
        0,
        77.0,
        "rem",
        1.6426161983559298
    ],
    [
        1,
        0,
        76.0,
        "nrem",
        1.073289488257166
    ],
    [
        2,
        0,
        48.0,
        "rem",
        1.7854041157820064
    ],
    [
        3,
        0,
        46.0,
        "nrem",
        1.0764312804609886
    ],
    [
        4,
        0,
        58.0,
        "rem",
        3.2930966254137966
    ],
]
```
#### 500 INTERNAL SERVER ERROR

Exception string.


## POST `/selected-sleep-phases/<int:patient_id>/<string:week>/<string:night_id>/`
### Description
Retrieve the selected sleep stages parameters from the DB.

### Payload

| Key | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `x`    | ✅        | int                                | -       |
| `y`    | ✅        | int | -       |


Example payload: x and y represent the coordinates on the frontend heatmap.

```json
[{
    "x": 0,
    "y": 1
},{
    "x": 0,
    "y": 2
},{
    "x": 2,
    "y": 4
}]
```

### Responses

#### 200 OK
Return type: string.

Example response:

```string
"sleep_stage_detection table updated successfully"
```
#### 500 INTERNAL SERVER ERROR

Exception string.


## Event Classification Page
## GET `/monitoring-allowed/<int:patient_id>/<string:week>/`

### Description
Check if monitoring is allowed for a specific patient on a specific week (the patient on a specific week is trained at list on one night).

### Parameters

| Parameter | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `patient_id`    | ✅        | int                                | -       |
| `week`    | ✅        | string | -       |

### Responses

#### 200 OK
Return type: JSON Object.

Example response:

```json
{
    "is_allowed": 1
}
```
#### 500 INTERNAL SERVER ERROR

Exception string.


## GET `/label-brux/<int:patient_id>/<string:week>/<string:night_id>/<string:recorder>`
### Description
Returns brux events defined by the model for a specific patient_id, week, night_id, and recorder.

### Parameters


| Parameter | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `patient_id`    | ✅        | int                                | -       |
| `week`    | ✅        | string | -       |
| `night_id`    | ✅        | string | -       |
| `recorder`    | ✅        | string | -       |


### Responses

#### 200 OK
Return type: list of JSON objects.

Example response:

```json
[
    {
        "end_index": 7021403,
        "label_id": 1,
        "location_begin": 14032806,
        "location_end": 14042806,
        "night_id": "1022102",
        "patient_id": 1,
        "recorder": "c",
        "start_index": 7016403,
        "week": "1"
    },
    {
        "end_index": 7551509,
        "label_id": 2,
        "location_begin": 15093018,
        "location_end": 15103018,
        "night_id": "1022102",
        "patient_id": 1,
        "recorder": "c",
        "start_index": 7546509,
        "week": "1"
    },
    {
        "end_index": 7771553,
        "label_id": 3,
        "location_begin": 15533106,
        "location_end": 15543106,
        "night_id": "1022102",
        "patient_id": 1,
        "recorder": "c",
        "start_index": 7766553,
        "week": "1"
    },
    {
        "end_index": 8795076,
        "label_id": 4,
        "location_begin": 20560152,
        "location_end": 20590152,
        "night_id": "1022102",
        "patient_id": 1,
        "recorder": "c",
        "start_index": 8780076,
        "week": "1"
    }
]
```


#### 500 INTERNAL SERVER ERROR

Exception string.


## POST `/label-brux/`
### Description
Post labels on the DB.

### Payload
List of Objects.

| Key | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `patient_id`    | ✅        | string                                | -       |
| `week`    | ✅        | string | -       |
| `night_id`    | ✅        | string | -       |
| `recorder`    | ✅        | string                                | -       |
| `label_id`    | ✅        | int | -       |
| `location_begin`    | ✅        | int | -       |
| `location_end`    | ✅        | int                                | -       |
| `start_index`    | ✅        | int | -       |
| `end_index`    | ✅        | int | -       |
| `Start`    | ✅        | float | -       |
| `End`    | ✅        | float | -       |
| `Confirm`    | ✅        | boolean | -       |



Example Payload:
```json
[
    {
        "patient_id": "1",
        "week": "1",
        "night_id": "1022102",
        "recorder":"c",
        "label_id": 1,
        "location_begin": 14032806,
        "location_end": 14042806,
        "start_index": 7016403,
        "end_index": 7021403,
        "Start": 7016.403,
        "End": 7021.403,
        "Confirm": true
    },
    {  
        "patient_id": "1",
        "week": "1",
        "night_id": "1022102",
        "recorder": "c",
        "label_id": 2,
        "location_begin": 15093018,
        "location_end": 15103018,
        "start_index": 7546509,
        "end_index": 7551509,
        "Start": 7546.509,
        "End": 7551.509,
        "Confirm": true
    }
]
```
### Responses

#### 200 OK
Return type: string.

Example response:
```string
    "Successfuly inserted into Database"
```

#### 500 INTERNAL SERVER ERROR

Exception string.


## GET `/event-interval/<int:patient_id>/<string:week>/<string:night_id>/<string:recorder>/<int:location_begin>/<int:location_end>/`

### Description
Get the interval in which the event occurs. Default: 5 minutes from the sleep_stage_detection table. Special cases: event duration +- activity duration defined in the settings. location_begin and location_end represents the start and end indexes of the event in the dataset.
### Parameters

| Parameter | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `patient_id`    | ✅        | int                                | -       |
| `week`    | ✅        | string | -       |
| `night_id`    | ✅        | string | -       |
| `recorder`    | ✅        | string | -       |
| `location_begin`    | ✅        | int | -       |
| `location_end`    | ✅        | int | -       |

### Responses

#### 200 OK
Return type: JSON Object.

Example response for request http://localhost:5000/event-interval/1/1/0901260/c/620000/695000:

```json
{
    "5min_end_id": 1200000,
    "5min_start_id": 600000,
    "ML": [
        -0.31824000000000013,
        -0.11351363238393572,
        -0.12759472371292246,
        -0.18950058485962812,
        0.06250958359178863,
        0.1661373819302275,
        ...,
        0.7437700095450963,
        0.590512171282252,
        0.3187415515472481,
        0.08670366276193478,
        -0.0704355786810057,
        -0.32448
    ],
    "MR": [
        0.7437700095450963,
        0.590512171282252,
        0.3187415515472481,
        0.08670366276193478,
        -0.0704355786810057,
        -0.32448,
        ...,
        599.9954999933334,
        599.9964999950017,
        599.9974999966838,
        599.9984999984531,
        599.9995
    ],
    "end_id": 299999,
    "event_end_id": 47499,
    "event_start_id": 10000,
    "start_id": 0
}
```
- 5min_start_id and 5min_end_id represents the index in the original dataset
- start_id and end_id are the indexes of the resampled dataset
- event_start_id and event_end_id are the indexes of the event in the resampled dataset

#### 500 INTERNAL SERVER ERROR

Exception string.



## GET `/weekly-sum-img`
## Description 
Get weekly summary image for a specific patient on a specific week.

## Parameters
| Parameter | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `p`    | ✅        | int                                | -       |
| `w`    | ✅        | string | -       |


### Responses

#### 200 OK
Return type: image/png

Example response for request http://localhost:5000/weekly-sum-img?p=2&w=3-4


![Image generated through weekly-sum-img endpoint for parient 2 on week 3-4](https://gitlab.ifi.uzh.ch/ivda/sensor-data-analysis-pipeline/-/raw/main/examples/response.png?ref_type=heads)

#### 500 INTERNAL SERVER ERROR

Exception string.


## GET `/night-pred-img`
## Description 
Get prediction image for a specific patient on a specificweek and night, and with a specific recorder.

## Parameters
| Parameter | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `p`    | ✅        | int                                | -       |
| `w`    | ✅        | string | -       |
| `n`    | ✅        | string | -       |
| `r`    | ✅        | string | -       |


### Responses

#### 200 OK
Return type: image/png

Example response for request http://localhost:5000/night-pred-img?p=1&w=1&n=1022102&r=c


![Image generated through weekly-sum-img endpoint for parient 2 on week 3-4](https://gitlab.ifi.uzh.ch/ivda/sensor-data-analysis-pipeline/-/raw/main/examples/response_night_pred_img.png?ref_type=heads)

#### 500 INTERNAL SERVER ERROR

Exception string.


## GET `/rerun-model/<int:patient_id>/<string:week>/<string:night_id>/<string:recorder>`

## Description
Reruns the model based on the confirmed events and gets the new precisions of study model and patient model.

## Parameters
| Parameter | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `patient_id`    | ✅        | int                                | -       |
| `week`    | ✅        | string | -       |
| `night_id`    | ✅        | string | -       |
| `recorder`    | ✅        | string | -       |


### Responses

#### 200 OK
Return type: A JSON object.

Example response for request http://localhost:5000/rerun-model/1/1/1022102/c/:
```json
{
    "patient_accuracy":{'accuracy': 97.03, 'precision': 73.63},
    "study_accuracy":{'accuracy': 97.03, 'precision': 73.56},
}
```

#### 500 INTERNAL SERVER ERROR

Exception string.


### GET `/model-accuracy/<int:patient_id>`
## Description
Get the accuracies and precisions of the models for a specific patient and for the whole study.

## Parameters
| Parameter | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `patient_id`    | ✅        | int                                | -       |


### Responses

#### 200 OK
Return type: A JSON object.

Example response for request http://localhost:5000/model-accuracy/1/:
```json
{
    "patient_accuracy": [
        97.03,
        73.63
    ],
    "study_accuracy": [
        97.03,
        73.56
    ]
}
```

#### 500 INTERNAL SERVER ERROR

Exception string.

## Treatment Analysis Page

## GET `/weekly-summary/<int:patient_id>/<string:week>/`

### Description
Get weekly summary (number of events in a specific week) for a specific patient of a specific week.

### Parameters
### Response
#### 200 OK
Return type: list of JSON objects.

Example response for request http://localhost:5000/weekly-summary/1/1/:
```json
[
    {
        "count": 2,
        "cycle": 3,
        "day_no": 2,
        "id": 194,
        "max_cycle": 7,
        "night_id": "1222325",
        "patient_id": 1,
        "type": 0,
        "week": "1"
    },
    {
        "count": 1,
        "cycle": 6,
        "day_no": 2,
        "id": 195,
        "max_cycle": 7,
        "night_id": "1222325",
        "patient_id": 1,
        "type": 1,
        "week": "1"
    },
    ...,
    {
        "count": 4,
        "cycle": 5,
        "day_no": 0,
        "id": 217,
        "max_cycle": 6,
        "night_id": "0901260",
        "patient_id": 1,
        "type": 4,
        "week": "1"
    }
]
```


#### 500 INTERNAL SERVER ERROR

Exception string.


## GET `/event-trend-patients-ids/`
### Description
Get patient ids for which events trend can be performed.


### Response
#### 200 OK
Return type: list.

Example response:
[
    "1",
    "2",
    "3",
    "4"
]

#### 500 INTERNAL SERVER ERROR

Exception string.


## GET `/event-trend`
### Description 
Get interpolated trend of the events for the specified patients.

### Parameters
List containing ids of patients for which we want the events trend.
| Parameter | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `patient_id`    | ✅        | list                                | -       |



### Response
#### 200 OK
Return type: list of JSON objects of dictionaries. Every JSON object represents a night, every dictionary represents a patient for the specific night. The dictionary key is the patient id.


Example response:

```json
[
    {
        "2": {
            "count": 30,
            "day": 14,
            "night": 315230.0,
            "type": 0.0,
            "week": "3-4"
        }
    },
    {
        "2": {
            "count": 30,
            "day": 15,
            "night": null,
            "type": -1.0,
            "week": "3-4"
        }
    },
    {
        "2": {
            "count": 30,
            "day": 16,
            "night": null,
            "type": -1.0,
            "week": "3-4"
        }
    },
    ...,
    {
        "2": {
            "count": 36,
            "day": 28,
            "night": 609302.0,
            "type": 0.0,
            "week": "5-6"
        }
    }
]   

```


#### 500 INTERNAL SERVER ERROR

Exception string.



