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

Exeption string.



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

Exeption string.


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

Exeption string.



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

Exeption string.


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

Exeption string.


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

Exeption string.

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

Exeption string.


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

Exeption string.


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

Exeption string.


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

Exeption string.

## GET `/label-brux/<int:patient_id>/<string:week>/<string:night_id>/<string:recorder>`
### TODO

## POST `/label-brux/`
### TODO


## GET `/event-interval/<int:patient_id>/<string:week>/<string:night_id>/<string:recorder>/<int:location_begin>/<int:location_end>`
### TODO

## GET `/weekly-sum-img`
### TODO

## GET `/night-pred-img`
### TODO


## GET `/rerun-model/<int:patient_id>/<string:week>/<string:night_id>/<string:recorder>`
### TODO


### GET `/model-accuracy/<int:patient_id>`
### TODO


## Treatment Analysis Page
## GET `/lineplot-data/<int:patient_id>/<string:week>/<string:night_id>/<string:recorder>`
### TODO


## GET `/weekly-summary/<int:patient_id>/<string:week>/`
### TODO

