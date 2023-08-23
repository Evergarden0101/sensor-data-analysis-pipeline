# API Design for the backend

## GET `/patient-recording/<int:patient_id>/<int:week>/<int:day>`

### Description
Get the recording of a patient on a specific day of the week.


### Parameters

| Parameter | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `patient_id`    | ✅        | int                                | -       |
| `week`    | ✅        | string | -       |
| `day`    | ✅        | string | -       |

### Responses

#### 200 OK

Return type: dataframe of the recordings of the patient on the specified day of the week:



**Example response**: pandas DataFrame

|   | id | patient_id | week | day | hours | minutes | seconds | recorder | MR       | ML        | SU       | Microphone  | Eye       | ECG     | Pressure |
|---|----|------------|------|-----|-------|---------|---------|----------|----------|-----------|----------|-------------|-----------|---------|----------|
| 0 | 1  | 1          | 1    | 09  | 01    | 26      | 0       | c        | 0.060487 | -0.016969 | 0.031892 | -0.00042522 | 0.0026094 | 0.2341  | null     |
| 1 | 2  | 1          | 1    | 09  | 01    | 26      | 0       | c        | 0.65835  | -0.1846   | 0.34712  | -0.00043261 | 0.0025676 | 0.23408 | null     |


#### 404 Not Found

Not Found if there are is no data for the specified patient on the desired day of the week.

**Example response:**


## POST `/patient-recording/<int:patient_id>/<int:week>/<string:day>/<string:hours>/<string:minutes>/<string:seconds>`

### Description

Insert the patient's recording on a specified day of the week in the database.

### Parameters
| Parameter | Required | Type                                  | default |
| --------- | -------- | ------------------------------------- | ------- |
| `patient_id`    | ✅        | int                                | -       |
| `week`    | ✅        | string | -       |
| `day`    | ✅        | string | -       |
| `hours`    | ✅        | string | -       |
| `minutes`    | ✅        | string | -       |
| `seconds`    | ✅        | string | -       |


### Response

#### 200 OK

**Example response**:

```
"Successfuly inserted into Database."
```

#### 400 Bad Request

Bad Request if was not possible to insert data for the specified patient on the desired day of the week.

**Response:** python Exception
